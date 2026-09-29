#!/usr/bin/env python3
"""S1: deterministic pass one over work/01-canonical.csv. No model, no network.

Per row: source channel (by referrer HOST, never substring), intent level and
phrase from the fixed tables, email type, RB2B size flag, title group, hard
reason codes that need no research, company key, research priority.
Per company: rollup with priority A/B/C/D/X, research batches, and a
name-collision check against earlier runs.

Writes work/02-pass1.csv, work/02-companies.csv, work/02-batch-deep-<n>.csv,
work/02-batch-triage-<n>.csv, work/02-prior-companies.csv.

Usage:
  classify.py --run RUN_DIR [--prior-dir "/…/1_Projects/Lead Triage"]
  classify.py keeps --run RUN_DIR      # after triage: batch the Keeps for deep research
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

PASS1_FIELDS = [
    "lead_id", "company_key", "is_company_only", "full_name", "title_used",
    "title_group", "flag_generic_exec", "flag_ambiguous_engineer",
    "source_channel", "referrer_host", "paid_referrer", "intent_level",
    "intent_phrase", "intent_page", "job_seeker_hint", "email_type",
    "email_domain", "rb2b_size_flag", "pass1_codes", "research_priority",
    "collision_flag",
]
COMPANY_FIELDS = [
    "company_key", "company_name", "domain_hint", "website_hint", "research_priority",
    "triage_first", "rows", "person_rows", "best_title", "visitor_names",
    "lead_ids", "best_intent", "touch_detail", "rb2b_size_flag",
    "collision_flag", "batch",
]

# ---------------------------------------------------------------------------
# Title groups. Regex lists reused from the 2026-09-25 run with three changes:
# in-house recruiters are Secondary, Generic exec is its own group, and agency
# or staffing recruiters are Excluded.
# ---------------------------------------------------------------------------
BLANK_TITLES = {"", "none", "n a", "na", "n/a", "-", "--", "null", "unknown",
                "client", "retired--", "tbd", "self"}
JUNK_TITLES = {"stay at home mom", "housewife and mother", "enjoying life",
               "working from home", "graduate", "retired"}

TECH_PRODUCT = [
    r"\bcto\b", r"\bchief technology officer\b", r"\bcio\b", r"\bchief information officer\b",
    r"\bchief digital officer\b", r"\bchief product officer\b", r"\bchief data officer\b",
    r"\bchief innovation officer\b", r"\bchief product (and|&) technology officer\b",
    r"\b(e?vp|svp|vice president)\b.*\b(software )?engineering\b",
    r"\b(e?vp|svp|vice president)\b.*\btechnology\b",
    r"\b(e?vp|svp|vice president)\b.*\binformation technology\b",
    r"\b(e?vp|svp|vice president)\b.*\bproduct( management)?\b(?!.*\bdesign\b)",
    r"\b(e?vp|svp|vice president)\b.*\bdigital( transformation)?\b",
    r"\b(e?vp|svp|vice president)\b.*\b(data|analytics|platform|infrastructure)\b",
    r"\bhead of (software )?engineering\b", r"\bhead of technology\b",
    r"\bhead of information technology\b", r"\bhead of it\b",
    r"\bhead of product( management)?\b", r"\bhead of digital\b",
    r"\bhead of (infrastructure|platform|data)( engineering)?\b",
    r"\bdirector\b.*\b(software )?engineering\b", r"\bdirector\b.*\btechnology\b",
    r"\bdirector\b.*\binformation technology\b", r"\bit director\b",
    r"\bdirector\b.*\bproduct( management)?\b(?!.*\bdesign\b)",
    r"\bdirector\b.*\bdigital( transformation)?\b", r"\bdirector\b.*\bdata and analytics\b",
    r"\bdirector\b.*\b(platform|systems|technical|architecture)\b",
    r"\bsenior director\b.*\btechnical\b", r"\bmis director\b",
    r"\bengineering manager\b", r"\bsoftware (engineering|development) manager\b",
    r"\bproduct engineering manager\b", r"\bapplications development manager\b",
    r"\bit manager\b", r"\btechnical director\b", r"\bdirector of ai\b", r"\bhead of ai\b",
    r"\bciso\b", r"\bchief information security officer\b",
    r"\bproduct executive\b",
    # both word orders; commas are stripped first, so "Director, IT" reads "director it"
    r"\b(director|vp|svp|evp|vice president|head|manager)( of)? it\b",
    r"\b(engineering|technology|product|software|platform|data|technical|it|digital) director\b",
    r"\b(director|head|vp|vice president)\b.*\bsoftware development\b",
    r"\binformation technology (manager|director|lead)\b",
    r"\bdirector\b.*\binformation systems\b",
]
DESIGN = [
    r"\bchief design officer\b", r"\bchief creative officer\b",
    r"\b(e?vp|svp|vice president)\b.*\b(design|creative)\b", r"\bhead of design\b",
    r"\bhead of creative\b", r"\bhead of user experience\b", r"\bhead of ux\b",
    r"\bdesign director\b", r"\bcreative director\b", r"\bdirector\b.*\bproduct design\b",
    r"\bdirector\b.*\buser experience\b", r"\bux director\b", r"\bdigital experience director\b",
]
RECRUITING = [
    r"\bchro\b", r"\bchief human resources officer\b", r"\bchief people officer\b",
    r"\bchief talent officer\b",
    r"\b(e?vp|svp|vice president)\b.*\bhuman resources\b", r"\b(e?vp|svp|vice president)\b.*\bpeople\b",
    r"\b(e?vp|svp|vice president)\b.*\btalent( acquisition)?\b", r"\bhead of human resources\b",
    r"\bhead of hr\b", r"\bhead of people\b", r"\bhead of talent( acquisition)?\b",
    r"\bhuman resources director\b", r"\bdirector\b.*\b(human resources|people|talent|recruiting)\b",
    r"\bhr director\b", r"\bpeople director\b", r"\btalent director\b",
    r"\btalent acquisition (director|manager|lead|partner)\b", r"\brecruiting (director|manager|lead)\b",
    r"\bpeople (and|&) talent lead\b", r"\btalent (and|&) people ops lead\b",
    r"\bhead of recruit(ing|ment)\b", r"\b(recruiting|talent acquisition|talent|people) (director|lead)\b",
]
OPS = [
    r"\b(e?vp|svp|vice president)\b.*\b(operations|transformation|procurement|strategy)\b",
    r"\bhead of (operations|transformation|strategy|procurement)\b",
    r"\bdirector\b.*\b(operations|transformation|procurement|strategy)\b",
    r"\b(strategy|operations|transformation) director\b",
    r"\bdirector of business systems\b", r"\bdirector of enterprise applications\b",
]
STRATEGY_EXCLUDE = r"\b(generic|editorial|audience|content|clinical|drug|academic|curriculum)\s+strategy\b"
SECONDARY = [
    r"\bproduct manager\b", r"\bprogram director\b", r"\bprogram manager\b",
    r"\bproject management director\b", r"\btechnical program manager\b",
    r"\bsolutions architect\b", r"\benterprise architect\b",
    r"\bprincipal( software)? engineer\b", r"\bstaff( software)? engineer\b",
    r"\blead software engineer\b", r"\bengineering lead\b", r"\btech lead\b",
    r"\bfounding engineer\b", r"\bproduct owner\b",
    r"\bproduct design lead\b", r"\bsenior ux designer\b",
    r"\bhuman resources? manager\b", r"\bhr manager\b", r"\bhr business partner\b",
    r"\bhr generalist\b", r"\bhuman resources? (generalist|specialist|business partner)\b",
    r"\btalent acquisition (specialist|consultant|coordinator|advisor)\b",
    r"\brecruiting (specialist|consultant|partner)\b", r"\btechnical recruiter\b", r"\brecruiter\b",
    r"\bfinance director\b", r"\bchief financial officer\b", r"\bcfo\b",
    r"\bprocurement manager\b", r"\b(e?vp|svp|vice president)\b.*\bmarketing\b",
    r"\bmarketing director\b", r"\bdirector\b.*\bmarketing\b", r"\bchief marketing officer\b", r"\bcmo\b",
    r"\bprincipal\b.*\b(data|architect)\b", r"\bsenior member of technical staff\b",
    r"\bchief growth officer\b",
]
GENERIC_EXEC = [
    r"\bco[- ]?founder\b", r"\bfounder\b", r"\bowner\b", r"(?<!vice )\bpresident\b", r"\bceo\b",
    r"\bchief executive officer\b", r"\bcoo\b", r"\bchief operating officer\b",
    r"\bmanaging director\b", r"\bmanaging partner\b", r"\bexecutive director\b",
    r"^principal$", r"\bgeneral manager\b", r"\bpartner\b", r"\bchief of staff\b",
    r"\bchief strategy officer\b", r"\bchief transformation officer\b", r"\bshareholder\b",
    r"^(vp|svp|evp|vice president|senior vice president|executive vice president)$",
    r"\bchief\b.*\bofficer\b", r"^chief\b",
]
FLAG_GENERIC = r"\b(owner|president|ceo|founder|co[- ]?founder|managing director|principal|general manager|partner|executive director)\b"
AGENCY_RECRUITER = [
    r"\bagency recruiter\b", r"\brecruiter\b.*\bagency\b", r"\bstaffing (recruiter|specialist|consultant|manager|coordinator)\b",
    # assistants to an executive are excluded before the executive word can match
    r"\b(executive|administrative|personal) assistant\b",
    r"\bthird[- ]party recruiter\b", r"\bcontract recruiter\b(?=.*\bagency\b)",
    r"\brecruitment consultant\b",
]
STUDENT_EDUCATOR = [r"\bstudent\b", r"\bteacher\b", r"\bprofessor\b", r"\binstructor\b",
                    r"\blecturer\b", r"\bgraduate assistant\b", r"\bteaching assistant\b"]
EXCLUDED = [
    r"\bintern\b", r"\binternship\b", r"\bassistant\b(?!\s+(vice president|director|general counsel))",
    r"\bcoordinator\b", r"\bsales rep(resentative)?\b", r"\baccount executive\b",
    r"\bcustomer (support|service|care)\b", r"\bproduction support\b", r"\btechnician\b",
    r"\bapprentice\b", r"\bcashier\b", r"\bdriver\b", r"\bnurse\b", r"\bnursing\b",
    r"\blpn\b", r"\bcna\b", r"\bretired\b", r"\bself[- ]?employed\b", r"\bhousewife\b",
    r"\bjob seeker\b", r"\bseeking (new )?(opportunities|employment|work)\b", r"\bopen to work\b",
    r"\bpolice officer\b", r"\bflight attendant\b", r"\bsecurity officer\b", r"\bbank teller\b",
    r"\blaborer\b", r"\bphlebotom\w*\b", r"\bmedical (assistant|coder|office specialist)\b",
    r"\bcosmetologist\b", r"\bfront desk\b", r"\breceptionist\b",
]
JOB_SEEKER_TITLE = r"\b(job seeker|seeking (new )?(opportunities|employment|work|a new role)|open to work|in transition|between roles)\b"
# "systems" is not a software marker: a systems engineer at a device maker builds hardware.
AMBIGUOUS_ENGINEER_MARKERS = r"\b(software|data|database|platform|dev[- ]?ops|cloud|ml|ai|full[- ]?stack|front[- ]?end|back[- ]?end|sre|security|it|web|mobile|network|qa|test|automation|founding)\b"
# Engineering leaders get a buyer role check from research anyway; the flag is for
# individual engineer titles whose field is unclear (mechanical, civil, systems).
ENGINEERING_LEADER = r"\b(director|vp|svp|evp|vice president|head|chief|manager)\b"


def _norm_title(t):
    t = C.clean(t).lower()
    t = re.sub(r"[.\-_/,|]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _any(pats, text):
    return any(re.search(p, text) for p in pats)


def classify_title(title):
    """Return (title_group, flag_generic_exec yes/no, flag_ambiguous_engineer yes/no)."""
    t = _norm_title(title)
    if t in BLANK_TITLES:
        return "No title", "no", "no"
    if t in JUNK_TITLES:
        return "Excluded title", "no", "no"
    amb = "yes" if re.search(r"\bengineer(s|ing)?\b", t) and not re.search(AMBIGUOUS_ENGINEER_MARKERS, t) \
        and not re.search(ENGINEERING_LEADER, t) else "no"
    if _any(AGENCY_RECRUITER, t):
        return "Excluded title", "no", amb
    if _any(TECH_PRODUCT, t):
        return "Primary: technology/product", "no", amb
    if _any(DESIGN, t):
        return "Primary: design/creative", "no", amb
    if _any(RECRUITING, t):
        return "Primary: recruiting/people", "no", amb
    if (_any(OPS, t) and not re.search(STRATEGY_EXCLUDE, t)):
        return "Primary: operations/transformation", "no", amb
    if _any(SECONDARY, t):
        return "Secondary influencer", "no", amb
    if _any(GENERIC_EXEC, t):
        return "Generic exec", "yes" if re.search(FLAG_GENERIC, t) else "no", amb
    if _any(STUDENT_EDUCATOR, t) or _any(EXCLUDED, t):
        return "Excluded title", "no", amb
    return "Unrelated title", "no", amb


def is_student_educator(title):
    return _any(STUDENT_EDUCATOR, _norm_title(title))


def parse_headline(headline):
    """'CTO at Acme | Builder' -> ('CTO', 'Acme')."""
    h = C.clean(headline)
    if not h:
        return "", ""
    first = re.split(r"\s[|•·]\s|\|", h)[0]
    m = re.split(r"\s+(?:at|@)\s+|\s*@\s*", first, maxsplit=1)
    if len(m) == 2:
        return m[0].strip(), m[1].strip()
    return first.strip(), ""

# ---------------------------------------------------------------------------
# Channel and intent from the reference tables
# ---------------------------------------------------------------------------

def referrer_info(referrer):
    host = C.host_of(referrer) if C.clean(referrer) else ""
    if not host:
        return {"host": "", "channel": "", "paid": False, "scanner": False}
    for r in C.ref_csv("referrer-hosts.csv"):
        h = r["host"]
        hit = host == h if r["match"] == "exact" else (host == h or host.endswith("." + h))
        if hit:
            return {"host": host, "channel": r["channel"], "paid": C.yes(r["paid"]),
                    "scanner": C.yes(r["scanner"])}
    return {"host": host, "channel": host, "paid": False, "scanner": False}


def page_info(path):
    p = path or "/"
    for r in C.ref_csv("page-intent.csv"):
        m = r["match"]
        if m == "exact" and p == r["path"]:
            hit, tail = True, ""
        elif m == "prefix" and p.startswith(r["path"]):
            hit, tail = True, p[len(r["path"]):].strip("/").replace("-", " ")
        elif m == "default":
            hit, tail = True, ""
        else:
            hit = False
        if hit:
            label = r["label"].replace("{tail}", tail or "index").replace("{path}", p)
            return {"level": r["level"], "label": label, "phrase": r["phrase"],
                    "ad_landing": C.yes(r["ad_landing"]), "job_seeker_hint": C.yes(r["job_seeker_hint"])}
    return {"level": "Low", "label": f"page {p}", "phrase": "", "ad_landing": False, "job_seeker_hint": False}


def page_view_intent(pages, referrer):
    """Pick the highest-intent page, then phrase it with the arrival channel."""
    ref = referrer_info(referrer)
    if ref["scanner"]:
        return "None", "Ad-verification scanner, not a person", pages[-1] if pages else "", False, ref
    best, best_page = None, ""
    for p in pages or ["/"]:  # ties go to the later page
        info = page_info(p)
        if best is None or C.INTENT_RANK[info["level"]] <= C.INTENT_RANK[best["level"]]:
            best, best_page = info, p
    level = best["level"]
    # RB2B carries no UTMs, so a paid referrer only makes an ad likely, never proven
    if ref["paid"] and best["ad_landing"]:
        level = "Low"
        phrase = f"Arrived from {ref['channel']} (likely an ad) at the {best['label']}"
    else:
        base = best["phrase"] or f"Viewed the {best['label']}"
        if ref["channel"]:
            if ref["paid"]:
                suffix = f" from {ref['channel']}, likely an ad" if "{source}" in base else \
                    f" from {ref['channel']} (likely an ad)"
            else:
                suffix = f" from {ref['channel']}"
        else:
            suffix = "" if "{source}" in base else " (no referrer)"
        if "{source}" in base:  # a table phrase can place the source itself
            phrase = base.replace("{source}", suffix)
        else:
            phrase = base + suffix if len(base + suffix) <= 120 else base
    return level, C.truncate(phrase, 120), best_page, best["job_seeker_hint"], ref


HIGH_COMMENT_WORDS = r"\b(hiring|looking for|need help|recommend|dm me|how much|pricing|rates?|vendor|partner with)\b"


def social_intent(row):
    counts = json.loads(row["engagement_counts"] or "{}") if row["engagement_counts"] else {}
    comments = counts.get("comments", 0)
    reactions = counts.get("reactions", 0)
    posts = counts.get("posts", 0)
    text = row.get("comment_text", "")
    if row["touch_type"] in ("comment", "reply") or comments:
        if text and re.search(HIGH_COMMENT_WORDS, text, re.I):
            return "High", C.truncate(f'Commented on a Midwestern exec\'s post: "{text[:80]}"', 120)
        return "Medium", "Commented on a Midwestern exec's post"
    if reactions >= 3 and posts >= 2:
        return "Medium", f"Reacted to {posts} posts by Midwestern execs"
    return "Low", "Reacted to a Midwestern exec's post"


CAMPAIGN_TOUCH = {
    "form_fill": ("High", "Filled out a form for {name}"),
    "event_registration": ("Medium", "Registered for {name}"),
    "event_attended": ("Medium", "Attended {name}"),
    "content_download": ("Medium", "Downloaded {name}"),
}


def campaign_intent(row):
    name = row["source_detail"] or "the list"
    if row["touch_type"] in CAMPAIGN_TOUCH:
        level, phrase = CAMPAIGN_TOUCH[row["touch_type"]]
        when = f" on {row['touch_date']}" if row["touch_date"] else ""
        return level, C.truncate(phrase.format(name=name) + when, 120)
    return "None", C.truncate(f"On the {name} list (how they joined is unknown)", 120)

# ---------------------------------------------------------------------------
# Hard codes that need no research
# ---------------------------------------------------------------------------
SELF_EMPLOYED_RE = r"\b(self[- ]?employed|freelanc\w*|independent contractor|sole proprietor)\b|^self$"
RB2B_OVER = {"5001+", "10,000+", "10000+", "enterprise", "5001", "10001"}


_LARGE = None


def known_large():
    """Normalized names of well-known 5,000+ employers (references/large-companies.txt)."""
    global _LARGE
    if _LARGE is None:
        path = os.path.join(C.REF_DIR, "large-companies.txt")
        with open(path, encoding="utf-8") as f:
            _LARGE = {C.norm_company_name(x) for x in f if x.strip() and not x.startswith("#")}
    return _LARGE


def exclusion_codes(full_name, company, email, domain_hint):
    codes = []
    dom = C.email_domain(email) or domain_hint
    for r in C.ref_csv("exclusions.csv"):
        pat = re.compile(r["pattern"], re.I)
        target = {"person": full_name, "company": company, "domain": dom}.get(r["kind"], "")
        if target and pat.search(target) and r["code"] not in codes:
            codes.append(r["code"])
    return codes


def pass1_row(row):
    title = row["title_raw"]
    if not title and row["headline"]:
        title, hc = parse_headline(row["headline"])
        if hc and not row["company_name_raw"]:
            row["company_name_raw"] = hc
    group, flag_gen, flag_amb = classify_title(title) if row["is_company_only"] == "no" else ("No title", "no", "no")

    ref = {"host": "", "channel": "", "paid": False}
    job_hint = False
    page = ""
    if row["source_type"] == "rb2b_visit":
        pages = [p for p in row["pages_all"].split(";") if p] or [row["source_detail"] or "/"]
        level, phrase, page, job_hint, ref = page_view_intent(pages, row["referrer_raw"])
    elif row["source_type"] == "social_engagement":
        level, phrase = social_intent(row)
    else:
        level, phrase = campaign_intent(row)

    codes = exclusion_codes(row["full_name"], row["company_name_raw"], row["email_raw"],
                            row["company_domain_hint"])
    comp_norm = C.norm_company_name(row["company_name_raw"])
    if re.search(SELF_EMPLOYED_RE, comp_norm):
        codes.append("CONSUMER_SELF_EMPLOYED")
    if row["is_company_only"] == "no":
        primary = group in C.PRIMARY_GROUPS
        seeker = row["rb2b_lead_type"].lower() == "likely job seeker" or \
            re.search(JOB_SEEKER_TITLE, _norm_title(title + " " + row["headline"]))
        if seeker and not primary:
            codes.append("JOB_SEEKER")
        if group == "Excluded title":
            codes.append("STUDENT_EDUCATOR" if is_student_educator(title) else "EXCLUDED_TITLE")
        if row["email_origin"] == "person_supplied" and C.email_type(row["email_raw"]) == "personal":
            codes.append("PERSONAL_EMAIL_SUBMITTED")
    if row["suppressed_reason"]:
        codes.append("COMPLIANCE_DNC")

    size_raw = C.clean(row["employee_count_raw"]).lower().replace(" ", "")
    rb2b_flag = "rb2b_says_over" if size_raw in RB2B_OVER else ""
    if not rb2b_flag and comp_norm and comp_norm in known_large():
        rb2b_flag = "known_large"  # sources with no size field (social): triage confirms it first

    # research priority for the row
    absolute_or_company = {"COMPLIANCE_DNC", "INTERNAL", "COMPETITOR_STAFFING", "CONSUMER_SELF_EMPLOYED"}
    person_hard = {"JOB_SEEKER", "STUDENT_EDUCATOR", "EXCLUDED_TITLE"}
    if not row["company_key"] or set(codes) & absolute_or_company:
        prio = "X"
    elif set(codes) & person_hard:
        prio = "X"
    elif row["is_company_only"] == "yes" or group == "No title":
        prio = "C"
    elif group in C.PRIMARY_GROUPS:
        prio = "B" if (flag_amb == "yes" or job_hint) else "A"
    elif group in ("Generic exec", "Secondary influencer"):
        prio = "B"
    else:
        prio = "D"

    return {
        "lead_id": row["lead_id"], "company_key": row["company_key"],
        "is_company_only": row["is_company_only"], "full_name": row["full_name"],
        "title_used": C.clean(title), "title_group": group, "flag_generic_exec": flag_gen,
        "flag_ambiguous_engineer": flag_amb, "source_channel": ref.get("channel", ""),
        "referrer_host": ref.get("host", ""), "paid_referrer": "yes" if ref.get("paid") else "no",
        "intent_level": level, "intent_phrase": phrase, "intent_page": page,
        "job_seeker_hint": "yes" if job_hint else "no",
        "email_type": C.email_type(row["email_raw"]), "email_domain": C.email_domain(row["email_raw"]),
        "rb2b_size_flag": rb2b_flag, "pass1_codes": ";".join(dict.fromkeys(codes)),
        "research_priority": prio, "collision_flag": "",
    }

# ---------------------------------------------------------------------------
# Prior-run name collision map
# ---------------------------------------------------------------------------
NAME_COLS = ["Company", "Company Name", "company_name", "company", "company_verified_name"]
# Curated domain columns only. Raw source website fields (RB2B "Company Website",
# "company_website") are wrong too often to count as evidence of a collision.
DOMAIN_COLS = ["Associate to company domain", "company_key_final", "company_website_verified",
               "Website", "domain", "Company domain"]


def is_test_run(folder):
    """A folder named '... test run ...', or a run folder normalized with --test-run."""
    if "test run" in os.path.basename(folder).lower():
        return True
    return bool((C.read_json(os.path.join(folder, "work", "run.json"), {}) or {}).get("test_run"))


def build_prior(prior_dir):
    out = []
    if not prior_dir or not os.path.isdir(prior_dir):
        return out
    paths = []
    for root, dirs, files in os.walk(prior_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "work" and not is_test_run(os.path.join(root, d))]
        paths += [os.path.join(root, f) for f in files if f.endswith(".csv")]
    seen = set()
    for p in sorted(paths):
        try:
            rows = C.read_csv(p)
        except (UnicodeDecodeError, OSError):
            continue
        if not rows:
            continue
        ncol = next((c for c in NAME_COLS if c in rows[0]), None)
        dcol = next((c for c in DOMAIN_COLS if c in rows[0]), None)
        if not ncol or not dcol:
            continue
        for r in rows:
            n = C.norm_company_name(r.get(ncol))
            d = C.registrable_domain(r.get(dcol))
            if n and d and (n, d) not in seen:
                seen.add((n, d))
                out.append({"name_norm": n, "domain": d, "source_file": os.path.relpath(p, prior_dir)})
    return out


def collision_for(name, domain, prior):
    n = C.norm_company_name(name)
    if not n:
        return ""
    doms = sorted({p["domain"] for p in prior if p["name_norm"] == n})
    if not doms:
        return ""
    # Pre-research domains are hints, so only a name that earlier runs already tied to
    # two or more domains is flagged here. label.py re-checks with the verified domain.
    if len(doms) > 1:
        return f"earlier runs used several domains for this name: {', '.join(doms)}"
    return ""

# ---------------------------------------------------------------------------
# Company rollup and batches
# ---------------------------------------------------------------------------
PRIO_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "X": 4}


def build_companies(canon, p1, prior):
    by_id = {r["lead_id"]: r for r in canon}
    comps = {}
    for p in p1:
        k = p["company_key"]
        if not k:
            continue
        r = by_id[p["lead_id"]]
        c = comps.setdefault(k, {"company_key": k, "company_name": "", "domain_hint": "",
                                 "prios": [], "rows": 0, "person_rows": 0, "titles": [],
                                 "names": [], "ids": [], "intents": [], "details": [], "flag": "",
                                 "websites": []})
        c["company_name"] = c["company_name"] or r["company_name_raw"]
        c["domain_hint"] = c["domain_hint"] or r["company_domain_hint"]
        if r.get("company_website_raw") and r["company_website_raw"] not in c["websites"]:
            c["websites"].append(r["company_website_raw"])
        c["prios"].append(p["research_priority"])
        c["rows"] += 1
        if p["is_company_only"] == "no":
            c["person_rows"] += 1
            if r["full_name"]:
                c["names"].append(r["full_name"])
            if p["title_used"]:
                c["titles"].append((p["title_group"], p["title_used"]))
        c["ids"].append(p["lead_id"])
        c["intents"].append(p["intent_level"])
        c["details"].append(p["intent_page"] or r["source_detail"])
        if p["rb2b_size_flag"]:
            c["flag"] = p["rb2b_size_flag"]
        if r.get("key_note") and r["key_note"] not in c.setdefault("notes", []):
            c["notes"].append(r["key_note"])
    out = []
    for k in sorted(comps):
        c = comps[k]
        prio = min(c["prios"], key=lambda x: PRIO_ORDER[x])
        rank = {g: i for i, g in enumerate(C.TITLE_GROUPS[1:6] + ["Generic exec", "Unrelated title", "No title", "Excluded title"])}
        best = sorted(c["titles"], key=lambda t: rank.get(t[0], 99))
        collision = "; ".join(x for x in [collision_for(c["company_name"], c["domain_hint"], prior)] +
                              c.get("notes", []) if x)
        out.append({
            "company_key": k, "company_name": c["company_name"], "domain_hint": c["domain_hint"],
            "website_hint": ";".join(c["websites"][:3]), "research_priority": prio,
            "triage_first": "yes" if (c["flag"] and prio in ("A", "B")) else "no",
            "rows": c["rows"], "person_rows": c["person_rows"],
            "best_title": f"{best[0][1]} ({best[0][0]})" if best else "",
            "visitor_names": "; ".join(sorted(set(c["names"])))[:300],
            "lead_ids": ";".join(c["ids"]),
            "best_intent": min(c["intents"], key=lambda x: C.INTENT_RANK.get(x, 3)),
            "touch_detail": "; ".join(sorted(set(d for d in c["details"] if d)))[:200],
            "rb2b_size_flag": c["flag"], "collision_flag": collision, "batch": "",
        })
    return out


def assign_batches(companies, deep_size, triage_size):
    deep = [c for c in companies if c["research_priority"] in ("A", "B") and c["triage_first"] == "no"]
    triage = [c for c in companies if c["research_priority"] in ("C", "D") or c["triage_first"] == "yes"]
    order = lambda c: (PRIO_ORDER[c["research_priority"]], C.INTENT_RANK.get(c["best_intent"], 3), c["company_key"])  # noqa: E731
    deep.sort(key=order)
    triage.sort(key=order)
    batches = {}
    for i, c in enumerate(deep):
        c["batch"] = f"deep-{i // deep_size + 1}"
    for i, c in enumerate(triage):
        c["batch"] = f"triage-{i // triage_size + 1}"
    for c in deep + triage:
        batches.setdefault(c["batch"], []).append(c)
    return batches


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "keeps":
        return keeps(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--prior-dir", default="")
    ap.add_argument("--deep-batch", type=int, default=20)
    ap.add_argument("--triage-batch", type=int, default=100)
    args = ap.parse_args(argv)

    canon = C.read_csv(C.work(args.run, "01-canonical.csv"))
    if not canon:
        sys.exit("no canonical rows; run normalize.py first")
    p1 = [pass1_row(dict(r)) for r in canon]
    prior = build_prior(args.prior_dir)
    C.write_csv(C.work(args.run, "02-prior-companies.csv"), prior, ["name_norm", "domain", "source_file"])
    companies = build_companies(canon, p1, prior)
    coll = {c["company_key"]: c["collision_flag"] for c in companies}
    for p in p1:
        p["collision_flag"] = coll.get(p["company_key"], "")
    batches = assign_batches(companies, args.deep_batch, args.triage_batch)

    C.write_csv(C.work(args.run, "02-pass1.csv"), p1, PASS1_FIELDS)
    C.write_csv(C.work(args.run, "02-companies.csv"), companies, COMPANY_FIELDS)
    # replace only this script's own batches; keep batches come from `classify.py keeps`
    for f in C.glob_work(args.run, "02-batch-deep-") + C.glob_work(args.run, "02-batch-triage-"):
        os.remove(f)
    for name, cs in sorted(batches.items()):
        C.write_csv(C.work(args.run, f"02-batch-{name}.csv"), cs, COMPANY_FIELDS)

    assert len(p1) == len(canon)
    keys_p1 = {p["company_key"] for p in p1 if p["company_key"]}
    assert keys_p1 == {c["company_key"] for c in companies}, "company keys differ between pass1 and companies"
    counts = {k: sum(c["research_priority"] == k for c in companies) for k in "ABCDX"}
    deep_n = sum(len(v) for k, v in batches.items() if k.startswith("deep"))
    tri_n = sum(len(v) for k, v in batches.items() if k.startswith("triage"))
    C.append_log(args.run, f"S1 rows={len(p1)} companies={len(companies)} priority A={counts['A']} "
                           f"B={counts['B']} C={counts['C']} D={counts['D']} X={counts['X']} "
                           f"deep={deep_n} triage={tri_n} collisions={sum(bool(c['collision_flag']) for c in companies)}")
    print(f"pass1 rows: {len(p1)}; companies: {len(companies)}; priority {counts}")
    print(f"deep-research companies: {deep_n} in {sum(k.startswith('deep') for k in batches)} batches; "
          f"triage companies: {tri_n} in {sum(k.startswith('triage') for k in batches)} batches")
    if deep_n > 60:
        print("STOP AND ASK JK: more than 60 companies need deep research before any triage Keeps.")
    for c in companies:
        if c["collision_flag"]:
            print(f"collision: {c['company_key']}: {c['collision_flag']}")


def keeps(argv):
    ap = argparse.ArgumentParser(prog="classify.py keeps")
    ap.add_argument("--run", required=True)
    ap.add_argument("--deep-batch", type=int, default=20)
    args = ap.parse_args(argv)
    companies = {c["company_key"]: c for c in C.read_csv(C.work(args.run, "02-companies.csv"))}
    triage = C.read_many(C.glob_work(args.run, "03-triage-"))
    done = {r["company_key"] for r in C.read_many(C.glob_work(args.run, "03-research-companies-"))}
    keep = [r["company_key"] for r in triage if C.clean(r.get("triage")).lower() == "keep"]
    existing = C.glob_work(args.run, "02-batch-keep-")
    queued = {r["company_key"] for r in C.read_many(existing)}
    todo = [companies[k] for k in sorted(set(keep)) if k in companies and k not in done and k not in queued]
    start = max([int(re.search(r"keep-(\d+)", f).group(1)) for f in existing] or [0])
    for i in range(0, len(todo), args.deep_batch):
        n = start + i // args.deep_batch + 1
        chunk = todo[i:i + args.deep_batch]
        for c in chunk:
            c["batch"] = f"keep-{n}"
        C.write_csv(C.work(args.run, f"02-batch-keep-{n}.csv"), chunk, COMPANY_FIELDS)
    deep_total = sum(len(C.read_csv(p)) for p in C.glob_work(args.run, "02-batch-deep-")) + len(todo)
    C.append_log(args.run, f"S2 triage keeps={len(set(keep))} new keep batches={len(todo)} companies")
    print(f"triage keeps: {len(set(keep))}; queued for deep research: {len(todo)}")
    if deep_total > 60:
        print(f"STOP AND ASK JK: deep research would cover {deep_total} companies (cap 60).")


if __name__ == "__main__":
    main()
