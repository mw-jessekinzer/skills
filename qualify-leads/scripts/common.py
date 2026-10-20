"""Shared helpers for the qualify-leads scripts. Python 3 stdlib only.

Everything that more than one script needs lives here: CSV IO, domain and
name normalization, reference-table loading, enums, and the text lint.
"""
import csv
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime
from urllib.parse import urlparse

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR = os.path.join(SKILL_DIR, "references")

csv.field_size_limit(sys.maxsize)

# ---------------------------------------------------------------------------
# Enums (controlled vocabulary). checks.py validates every label cell against
# these sets.
# ---------------------------------------------------------------------------
VERDICTS = ["Qualified", "Possible match", "Insufficient data", "Not qualified"]
ACTIONS = ["Contact now", "Tell account owner", "Account play", "Review",
           "Low priority", "Drop"]
STRENGTHS = ["Strong", "Medium", "Weak", "None"]
CONFIDENCE = ["High", "Medium", "Low"]
INTENT_LEVELS = ["High", "Medium", "Low", "None"]
SERVICE_FITS = ["Recruiting", "Embedded", "Scoped", "None"]
EMAIL_STATUSES = ["None", "Personal", "Wrong domain", "Undeliverable",
                  "From HubSpot", "Given by the person", "Verified",
                  "Verified, catch-all domain", "Catch-all, unconfirmed",
                  "Unverified work email"]
QUALIFYING_EMAIL = {"From HubSpot", "Given by the person", "Verified",
                    "Verified, catch-all domain"}
HIRING_STATUSES = ["Hiring tech roles", "Hiring tech roles, none in US",
                   "Hiring, non-tech only", "No open roles found",
                   "Not checked", "Unknown"]
# Company size is a descriptive tier, never a disqualifier (JK ruling 2026-10-12: no
# size cap; Enterprise companies stay). label.py computes it from employees_best (any
# source tier) and need_signals.
ENTERPRISE_MIN = 5000          # Enterprise: 5,000+ employees
MIDMARKET_MIN = 500            # Mid-market: 500 to 4,999
STARTUP_FUNDING_MONTHS = 24    # under 500 with a funding signal this recent: Growth startup
COMPANY_SIZES = ["Enterprise", "Mid-market", "Growth startup", "Small business", "Unknown"]
# Retired size drop codes. Read only so triage files written before 2026-10-12 still
# load; label.py ignores such a drop with a warning, because size never drops a row.
CODE_ALIASES = {"OVER_2000": "OVER_SIZE_CAP"}
RETIRED_SIZE_CODES = {"OVER_SIZE_CAP", "OVER_2000"}


def canonical_code(code):
    """A reason code as read from a worker file, with old names mapped to current ones."""
    code = clean(code)
    return CODE_ALIASES.get(code, code)


SIZE_BANDS = ["1-10", "11-50", "51-200", "201-500", "501-1,000",
              "1,001-1,999", f"2,000-{ENTERPRISE_MIN - 1:,}", f"{ENTERPRISE_MIN:,}+", "Unknown"]
TITLE_GROUPS = ["No title", "Primary: technology/product",
                "Primary: design/creative", "Primary: recruiting/people",
                "Primary: operations/transformation", "Secondary influencer",
                "Generic exec", "Excluded title", "Unrelated title"]
PRIMARY_GROUPS = {"Primary: technology/product", "Primary: design/creative",
                  "Primary: recruiting/people",
                  "Primary: operations/transformation"}
SOURCE_TYPES = ["rb2b_visit", "social_engagement", "campaign_list", "other_list"]
TOUCH_TYPES = ["page_view", "reaction", "comment", "reply", "form_fill",
               "event_registration", "event_attended", "content_download",
               "list_member"]
PERSON_SUPPLIED_TOUCHES = {"form_fill", "event_registration", "event_attended"}
FORM_TOUCHES = {"form_fill", "event_registration"}
CRM_STATES = ["open_deal", "customer", "owned_active", "owned_inactive",
              "unowned", "possible_match", "not_found", "not_checked"]

ACTION_RANK = {a: i for i, a in enumerate(ACTIONS)}
VERDICT_RANK = {v: i for i, v in enumerate(VERDICTS)}
STRENGTH_RANK = {"Strong": 0, "Medium": 1, "Weak": 2, "None": 3}
INTENT_RANK = {"High": 0, "Medium": 1, "Low": 2, "None": 3, "": 3}

DEFAULT_CAPS = {"deepline": [10.0, "credit"], "hirebase": [25.0, "credit"],
                "moltsets": [60.0, "token"]}

# ---------------------------------------------------------------------------
# CSV / JSON IO
# ---------------------------------------------------------------------------

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [dict(r) for r in csv.DictReader(f)]


def read_csv_header(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return next(csv.reader(f), [])


def write_csv(path, rows, fields, bom=False):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    enc = "utf-8-sig" if bom else "utf-8"
    with open(path, "w", newline="", encoding=enc) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def work(run_dir, *parts):
    return os.path.join(run_dir, "work", *parts)


def append_log(run_dir, line):
    """Add a line to the end of the "## Counts" section, leaving the runner's
    own sections (Rulings, Commands, Notes) where they are."""
    path = work(run_dir, "00-run-log.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = "# Run log\n\n## Counts\n\n"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
    if "## Counts" not in text:
        text = text.rstrip("\n") + "\n\n## Counts\n\n"
    start = text.index("## Counts")
    nxt = text.find("\n## ", start + 1)
    entry = f"- {line}\n"
    if nxt == -1:
        text = text.rstrip("\n") + "\n" + entry
    else:
        head = text[:nxt].rstrip("\n") + "\n"
        text = head + entry + "\n" + text[nxt:].lstrip("\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_run(run_dir):
    return read_json(work(run_dir, "run.json"), {}) or {}


def save_run(run_dir, run):
    write_json(work(run_dir, "run.json"), run)


def glob_work(run_dir, prefix, suffix=".csv"):
    d = work(run_dir)
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d)
                  if f.startswith(prefix) and f.endswith(suffix))


def read_many(paths):
    out = []
    for p in paths:
        out.extend(read_csv(p))
    return out

# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------

def clean(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()


def truncate(text, limit=160):
    text = clean(text)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "."


def to_int(s):
    s = clean(s).replace(",", "")
    if not s:
        return None
    m = re.fullmatch(r"-?\d+", s)
    if m:
        return int(s)
    try:
        return int(float(s))
    except ValueError:
        return None


def yes(v):
    return clean(v).lower() in ("yes", "y", "true", "1")


SLASH_DATE_RE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")


def parse_date(s, slash="dmy"):
    """Return a date from ISO, 'YYYY-MM-DD HH:MM:SS +0000', or a slash date.
    Slash dates are read as `slash` (dmy or mdy). Only the csv adapter sees
    slash dates, and it decides the order per file (see slash_order)."""
    s = clean(s)
    if not s:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = SLASH_DATE_RE.match(s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        d, mo = (a, b) if slash == "dmy" else (b, a)
        try:
            return date(y, mo, d)
        except ValueError:
            return None
    if re.fullmatch(r"\d{12,13}", s):  # epoch ms (Lever)
        return datetime.utcfromtimestamp(int(s) / 1000).date()
    return None


def parse_ts(s):
    """'2026-09-25T19:41:04Z', '2026-09-25 19:41:04 +0000', '...000+00:00', or a bare
    date -> 'YYYY-MM-DDTHH:MM:SSZ' (sources here are UTC). None if not a date."""
    s = clean(s)
    m = re.match(r"(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?)?", s)
    if not m:
        return None
    hh, mm, ss = m.group(2) or "00", m.group(3) or "00", m.group(4) or "00"
    return f"{m.group(1)}T{hh}:{mm}:{ss}Z"


def slash_order(values):
    """Decide how to read the slash dates in one column.
    Returns ('dmy'|'mdy'|None, problem). None means no slash dates at all.
    A problem string means the caller must stop and ask for --date-format."""
    firsts, seconds, iso_seen, slash_seen = [], [], False, False
    for v in values:
        v = clean(v)
        if re.match(r"\d{4}-\d{2}-\d{2}", v):
            iso_seen = True
        m = SLASH_DATE_RE.match(v)
        if m:
            slash_seen = True
            firsts.append(int(m.group(1)))
            seconds.append(int(m.group(2)))
    if not slash_seen:
        return None, ""
    day_first = any(x > 12 for x in firsts)
    month_first = any(x > 12 for x in seconds)
    if iso_seen:
        return None, "the date column mixes ISO and slash dates"
    if day_first and month_first:
        return None, "the date column mixes day-first and month-first dates"
    if day_first:
        return "dmy", ""
    if month_first:
        return "mdy", ""
    return None, "slash dates are ambiguous (every part is 12 or less)"


def packet_name(company):
    """Packet filename for a company: path characters become spaces."""
    safe = re.sub(r'[\\/:*?"<>|]+', " ", clean(company))
    return re.sub(r"\s{2,}", " ", safe).strip(" .") + " - Lead Packet.md"


def iso(d):
    return d.isoformat() if d else ""

# ---------------------------------------------------------------------------
# Domains, emails, names
# ---------------------------------------------------------------------------
PERSONAL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "rocketmail.com",
    "hotmail.com", "outlook.com", "live.com", "msn.com", "windowslive.com",
    "icloud.com", "me.com", "mac.com", "aol.com", "netscape.net",
    "protonmail.com", "proton.me", "pm.me", "comcast.net", "att.net",
    "sbcglobal.net", "bellsouth.net", "verizon.net", "cox.net", "charter.net",
    "spectrum.net", "earthlink.net", "juno.com", "mail.com", "gmx.com",
    "zoho.com", "optonline.net", "windstream.net", "frontier.com",
    "centurylink.net", "hey.com", "fastmail.com", "yahoo.co.uk",
}
PERSONAL_SUFFIXES = (".rr.com",)

TWO_LEVEL_SUFFIXES = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "me.uk", "com.au", "net.au", "org.au",
    "edu.au", "co.nz", "org.nz", "co.jp", "com.br", "co.in", "com.mx", "co.za",
    "com.sg", "com.hk", "co.il", "com.tr", "com.cn",
}


def host_of(value):
    """Host from a URL, bare domain, or email address. Lowercase, no www."""
    v = clean(value).lower()
    if not v:
        return ""
    if "@" in v and "//" not in v:
        v = v.rsplit("@", 1)[-1]
    if "//" not in v:
        v = "http://" + v
    try:
        host = urlparse(v).netloc
    except ValueError:
        return ""
    host = host.split("@")[-1].split(":")[0].strip(".")
    return re.sub(r"^www\d?\.", "", host)


def registrable_domain(value):
    host = host_of(value)
    if not host or "." not in host:
        return ""
    labels = host.split(".")
    if len(labels) >= 3 and ".".join(labels[-2:]) in TWO_LEVEL_SUFFIXES:
        return ".".join(labels[-3:])
    if labels[-1] == "us" and len(labels) >= 3 and len(labels[-2]) == 2:
        # state and K-12 domains: chatham.nc.us, ewg.k12.ri.us
        n = 4 if len(labels) >= 4 and labels[-3] == "k12" else 3
        return ".".join(labels[-n:])
    return ".".join(labels[-2:])


def email_domain(email):
    e = clean(email).lower()
    if "@" not in e:
        return ""
    return registrable_domain(e.rsplit("@", 1)[-1])


def is_personal_domain(domain):
    d = clean(domain).lower()
    return d in PERSONAL_DOMAINS or any(d.endswith(s) for s in PERSONAL_SUFFIXES)


def email_type(email):
    e = clean(email).lower()
    if not e or "@" not in e:
        return "none"
    return "personal" if is_personal_domain(e.rsplit("@", 1)[-1]) else "work"


def domain_list(value):
    """Semicolon list of domains -> set of registrable domains."""
    out = set()
    for part in re.split(r"[;,\s]+", clean(value)):
        d = registrable_domain(part)
        if d:
            out.add(d)
    return out


def domain_in(email_or_domain, domains):
    d = email_domain(email_or_domain) if "@" in (email_or_domain or "") \
        else registrable_domain(email_or_domain)
    return bool(d) and d in domains


SUFFIX_WORDS = {"inc", "llc", "corp", "corporation", "co", "company", "ltd",
                "llp", "lp", "plc", "pllc", "pc", "group", "holdings", "the"}


def norm_company_name(name):
    """Lowercase key for a company name. Accents fold to ASCII (Café -> cafe);
    non-Latin scripts are kept as they are (华为 stays 华为), never blanked."""
    n = unicodedata.normalize("NFKD", clean(name))
    n = "".join(ch for ch in n if not unicodedata.combining(ch)).casefold()
    n = n.replace("&", " and ")
    n = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in n)
    words = [w for w in n.split() if w]
    while words and (words[-1] in SUFFIX_WORDS or (words[-1] == "and" and len(words) > 1)):
        words.pop()  # "JPMorgan Chase & Co." -> "jpmorgan chase"
    while words and words[0] == "the":
        words.pop(0)
    return " ".join(words)


def norm_linkedin(url):
    u = clean(url).lower()
    if not u:
        return ""
    m = re.search(r"linkedin\.com/in/([^/?#\s]+)", u)
    if not m:
        return ""
    return "https://www.linkedin.com/in/" + m.group(1).strip("/")


def split_name(full):
    parts = clean(full).split(" ")
    if not parts or not parts[0]:
        return "", ""
    return parts[0], " ".join(parts[1:])

# ---------------------------------------------------------------------------
# Reference tables
# ---------------------------------------------------------------------------
_REF_CACHE = {}


def ref_csv(name):
    if name not in _REF_CACHE:
        _REF_CACHE[name] = read_csv(os.path.join(REF_DIR, name))
    return _REF_CACHE[name]


def reason_codes():
    """code -> dict(code, class, template)."""
    return {r["code"]: r for r in ref_csv("reason-codes.csv")}


def tech_role_regex():
    path = os.path.join(REF_DIR, "tech-roles.txt")
    pats = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pats.append(line)
    return re.compile("|".join(f"(?:{p})" for p in pats), re.I)

# ---------------------------------------------------------------------------
# Lint (dashes, banned words, tropes). Used by checks.py and assemble.py.
# ---------------------------------------------------------------------------
DASH_RE = re.compile("[—–]| -- ")
# "broker" is banned as a word for what Midwestern does; a prospect's industry
# (broker-dealer, insurance broker, mortgage broker) is a fact and stays.
BANNED_COPY_RE = re.compile(
    r"(?<!insurance )(?<!mortgage )(?<!freight )(?<!customs )(?<!estate )"
    r"\bbrokers?\b(?!-dealer)|\b(staffing firms?|staffing partners?|outsourc\w*)\b", re.I)
JARGON_RE = re.compile(r"\b(DQ|ICP gate|pass1|ATS)\b")
TROPE_RES = [re.compile(p, re.I) for p in (
    r"didn't [^.;]*; (it|they)\b", r"; you have\b", r"isn't [^.;]*, it's\b",
    r"^(that instinct is right|you're right to)")]
INTENT_OVERSTATE_RE = re.compile(
    r"\b(submitted|filled out|requested|signed up|registered|interested in)\b", re.I)


def desdash(text):
    """For source text only (names, titles): swap dashes for commas."""
    t = re.sub(r"\s*[—–]\s*|\s+--\s+", ", ", text or "")
    return re.sub(r"\s{2,}", " ", t).strip(" ,")


def lint_text(text, jargon=False):
    """Return a list of problem strings for one piece of text."""
    problems = []
    if not text:
        return problems
    if DASH_RE.search(text):
        problems.append("em/en dash or ' -- '")
    m = BANNED_COPY_RE.search(text)
    if m:
        problems.append(f"banned word '{m.group(0)}'")
    if jargon:
        m = JARGON_RE.search(text)
        if m:
            problems.append(f"internal jargon '{m.group(0)}'")
    for r in TROPE_RES:
        if r.search(text):
            problems.append(f"trope '{r.pattern}'")
    return problems
