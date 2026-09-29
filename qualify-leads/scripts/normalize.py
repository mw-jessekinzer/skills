#!/usr/bin/env python3
"""S0: source adapters. Turn any lead list into work/01-canonical.csv.

Adapters:
  rb2b-baserow   JSON from `baserow.sh rows 1171339 --raw` (one or more page files,
                 a list of rows, or a dict with "results")
  rb2b-export    RB2B direct export CSV (filtered_custom_report_*.csv)
  social         exec-analytics Leads "Export CSV" (leads-list-YYYY-MM-DD.csv)
  csv            any CSV; header aliases below, --map to override, --touch-type required

Writes work/01-canonical.csv, work/01-dupes.csv, work/run.json and appends the
S0 counts and date profile to work/00-run-log.md. Reads only; never calls a CRM.

Usage:
  normalize.py --run RUN_DIR --adapter rb2b-baserow --input page1.json [page2.json ...]
               [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--source-label "RB2B"]
               [--as-of YYYY-MM-DD]
  normalize.py --run RUN_DIR --adapter csv --input list.csv --touch-type form_fill
               --campaign "Q3 webinar" [--map "title=Job Title,company=Org"] [--date-format mdy]

Options for any adapter:
  --since / --until     a date (whole day) or a full timestamp, e.g. 2026-09-25T19:41:04Z
  --exclude-prior DIR   skip lead ids already in an earlier run folder (new since last run)
  --test-run            mark the run as a test so later --prior-dir scans ignore it
Repeated record ids (overlapping pages or exports) are dropped and logged in 01-dupes.csv.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date, timedelta
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

CANONICAL_FIELDS = [
    "lead_id", "source_type", "source_system", "source_record_id", "source_file",
    "source_detail", "touch_type", "touch_date", "touch_ts", "touch_date_basis", "touch_count",
    "email_origin", "is_company_only", "full_name", "first_name", "last_name",
    "title_raw", "company_name_raw", "company_domain_hint", "company_website_raw", "company_key",
    "headline", "linkedin_url", "email_raw", "city", "state", "country",
    "company_linkedin_url", "employee_count_raw", "industry_raw", "referrer_raw",
    "pages_all", "reaction_types", "comment_text", "engagement_counts",
    "crm_hint", "rb2b_lead_type", "past_company", "suppressed_reason",
    "key_note", "touches_json",
]

# Company names that mean "no company". Self-employed wording is kept (classify
# turns it into CONSUMER_SELF_EMPLOYED); pure placeholders become blank.
PLACEHOLDER_COMPANIES = {"", "none", "n a", "na", "home", "all", "business",
                         "unknown", "early retirement", "retired", "unemployed",
                         "student", "null", "not applicable", "private"}

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def path_of(url):
    u = C.clean(url)
    if not u:
        return ""
    try:
        p = urlparse(u if "//" in u else "https://x" + (u if u.startswith("/") else "/" + u)).path
    except ValueError:
        return ""
    p = p or "/"
    if len(p) > 1:
        p = p.rstrip("/")
    return p


def company_key_for(company_name, email, website):
    """Pre-research key. Company name first (source website fields are often
    wrong), then a work-email domain, then the website domain."""
    n = C.norm_company_name(company_name)
    if n and n not in PLACEHOLDER_COMPANIES:
        return "name:" + n
    ed = C.email_domain(email)
    if ed and not C.is_personal_domain(ed):
        return ed
    wd = C.registrable_domain(website)
    if wd and not C.is_personal_domain(wd):
        return wd
    return ""


def domain_hint(email, website):
    ed = C.email_domain(email)
    if ed and not C.is_personal_domain(ed):
        return ed
    return C.registrable_domain(website)


def blank_row():
    return {f: "" for f in CANONICAL_FIELDS}


def finish(row):
    """Fill derived canonical fields shared by every adapter."""
    if C.norm_company_name(row["company_name_raw"]) in PLACEHOLDER_COMPANIES:
        row["company_name_raw"] = ""
    if not row["first_name"] and not row["last_name"] and row["full_name"]:
        row["first_name"], row["last_name"] = C.split_name(row["full_name"])
    if not row["full_name"]:
        row["full_name"] = C.clean(f"{row['first_name']} {row['last_name']}")
    row["linkedin_url"] = C.norm_linkedin(row["linkedin_url"])
    row["company_domain_hint"] = row["company_domain_hint"] or domain_hint(row["email_raw"], "")
    row["company_key"] = company_key_for(row["company_name_raw"], row["email_raw"],
                                         row["company_domain_hint"])
    if not row["email_origin"]:
        row["email_origin"] = "source_matched" if row["email_raw"] else "none"
    if not row["email_raw"]:
        row["email_origin"] = "none"
    row["touch_count"] = row["touch_count"] or "1"
    for k in row:
        if k != "touches_json":
            row[k] = C.clean(row[k])
    return row

# ---------------------------------------------------------------------------
# Adapters
# ---------------------------------------------------------------------------

def load_baserow_rows(paths):
    rows = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else [data]
        for it in items:
            if isinstance(it, dict) and "results" in it and isinstance(it["results"], list):
                rows.extend(it["results"])
            elif isinstance(it, dict):
                rows.append(it)
    return rows


def adapt_rb2b_baserow(args):
    table = args.table
    out = []
    for r in load_baserow_rows(args.input):
        row = blank_row()
        lead_type = C.clean(r.get("Lead Type"))
        company_only = lead_type.lower() == "company only" or (
            not C.clean(r.get("First Name")) and not C.clean(r.get("Last Name")))
        row.update({
            "lead_id": f"baserow:{table}:{r.get('id')}",
            "source_type": "rb2b_visit",
            "source_system": f"baserow:{table}",
            "source_record_id": str(r.get("id")),
            "source_file": f"baserow:{table}",
            "touch_type": "page_view",
            "touch_date": C.iso(C.parse_date(r.get("Last Seen At"))),
            "touch_ts": C.parse_ts(r.get("Last Seen At")) or "",
            "touch_date_basis": "event_time",
            "is_company_only": "yes" if company_only else "no",
            "full_name": "" if company_only else C.clean(r.get("Name")),
            "first_name": "" if company_only else C.clean(r.get("First Name")),
            "last_name": "" if company_only else C.clean(r.get("Last Name")),
            "title_raw": C.clean(r.get("Title")),
            "company_name_raw": C.clean(r.get("Company Name")) or (C.clean(r.get("Name")) if company_only else ""),
            "email_raw": C.clean(r.get("Business Email")).lower(),
            "linkedin_url": r.get("LinkedIn URL") or "",
            "city": r.get("City") or "", "state": r.get("State") or "",
            "country": "",
            "employee_count_raw": r.get("Employee Count") or "",
            "industry_raw": r.get("Industry") or "",
            "referrer_raw": r.get("Referrer") or "",
            "rb2b_lead_type": lead_type,
            "crm_hint": "RB2B: in contact with sales" if "contact with sales" in lead_type.lower() else "",
        })
        pages = []
        for u in (r.get("First Captured URL"), r.get("Last Captured URL")):
            p = path_of(u)
            if p and p not in pages:
                pages.append(p)
        row["source_detail"] = path_of(r.get("Last Captured URL"))
        row["pages_all"] = ";".join(pages)
        row["company_domain_hint"] = domain_hint(row["email_raw"], r.get("Company Website"))
        row["company_website_raw"] = C.registrable_domain(r.get("Company Website"))
        out.append(finish(row))
    return out


def adapt_rb2b_export(args):
    out = []
    for path in args.input:
        for r in C.read_csv(path):
            row = blank_row()
            company_only = C.clean(r.get("ProfileType")).lower() == "company"
            rec = C.clean(r.get("LinkedInUrl"))
            if company_only or not rec:
                rec = "co-" + hashlib.sha1(f"{r.get('CompanyName')}|{r.get('LastSeenAt')}".encode()).hexdigest()[:12]
            pages = []
            try:
                urls = json.loads(r.get("RecentPageUrls") or "[]")
            except ValueError:
                urls = [u for u in re.split(r"[,\s]+", r.get("RecentPageUrls") or "") if u]
            for u in urls:
                p = path_of(u)
                if p and p not in pages:
                    pages.append(p)
            row.update({
                "lead_id": f"rb2b_export:{rec}",
                "source_type": "rb2b_visit", "source_system": "rb2b_export",
                "source_record_id": rec, "source_file": os.path.basename(path),
                "touch_type": "page_view",
                "touch_date": C.iso(C.parse_date(r.get("LastSeenAt"))),
                "touch_ts": C.parse_ts(r.get("LastSeenAt")) or "",
                "touch_date_basis": "event_time",
                "is_company_only": "yes" if company_only else "no",
                "first_name": "" if company_only else r.get("FirstName", ""),
                "last_name": "" if company_only else r.get("LastName", ""),
                "title_raw": r.get("Title", ""),
                "company_name_raw": r.get("CompanyName", ""),
                "email_raw": C.clean(r.get("WorkEmail")).lower(),
                "linkedin_url": r.get("LinkedInUrl", ""),
                "city": r.get("City", ""), "state": r.get("State", ""),
                "employee_count_raw": r.get("EstimatedEmployeeCount", ""),
                "industry_raw": r.get("Industry", ""),
                "referrer_raw": r.get("MostRecentReferrer", ""),
                "pages_all": ";".join(pages),
                "source_detail": pages[-1] if pages else "",
            })
            row["company_domain_hint"] = domain_hint(row["email_raw"], r.get("Website"))
            row["company_website_raw"] = C.registrable_domain(r.get("Website"))
            out.append(finish(row))
    return out


def adapt_social(args):
    """exec-analytics Leads list export: name, title, company, tag,
    outreachStatus, linkedinUrl, listAddedAt, distinctExecs, distinctPosts,
    reactions, comments, replies, firstSeenAt, lastSeenAt, heatTier.
    tag and heatTier are the app's own fit tiers: ignored on purpose."""
    out = []
    for path in args.input:
        for i, r in enumerate(C.read_csv(path), start=2):
            row = blank_row()
            li = C.norm_linkedin(r.get("linkedinUrl"))
            # no LinkedIn URL: file name plus row number, so row 2 of a second export is not
            # mistaken for a repeat of row 2 of the first
            base = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(path))[0].lower()).strip("-")
            slug = li.rsplit("/", 1)[-1] if li else f"{base}-row{i}"
            company = C.clean(r.get("company"))
            past = ""
            if company.endswith("(past)"):
                past, company = company[:-6].strip(), ""
            comments = (C.to_int(r.get("comments")) or 0) + (C.to_int(r.get("replies")) or 0)
            reactions = C.to_int(r.get("reactions")) or 0
            posts = C.to_int(r.get("distinctPosts")) or 0
            execs = C.to_int(r.get("distinctExecs")) or 0
            row.update({
                "lead_id": f"exec_analytics:{slug}",
                "source_type": "social_engagement", "source_system": "exec_analytics",
                "source_record_id": slug, "source_file": os.path.basename(path),
                "touch_type": "comment" if comments else "reaction",
                "touch_date": C.iso(C.parse_date(r.get("lastSeenAt"))),
                "touch_ts": C.parse_ts(r.get("lastSeenAt")) or "",
                "touch_date_basis": "observed",
                "touch_count": str(max(1, reactions + comments)),
                "is_company_only": "no",
                "full_name": r.get("name", ""),
                "title_raw": r.get("title", ""),
                "company_name_raw": company,
                "past_company": past,
                "linkedin_url": li,
                "engagement_counts": json.dumps({"reactions": reactions, "comments": comments,
                                                 "posts": posts, "execs": execs}, sort_keys=True),
                "source_detail": f"LinkedIn posts by Midwestern execs ({posts} posts, {execs} execs)",
                "email_origin": "none",
            })
            out.append(finish(row))
    return out


CSV_ALIASES = {
    "full_name": ["name", "full name", "contact name"],
    "first_name": ["first name", "firstname", "first"],
    "last_name": ["last name", "lastname", "last", "surname"],
    "title_raw": ["title", "job title", "jobtitle", "position", "role"],
    "company_name_raw": ["company", "company name", "organization", "organisation", "account", "employer"],
    "email_raw": ["email", "work email", "business email", "email address", "e-mail"],
    "linkedin_url": ["linkedin", "linkedin url", "profile url", "linkedin profile", "person linkedin url"],
    "company_domain_hint": ["website", "company domain", "domain", "company website", "company url"],
    "touch_date": ["date", "created", "create date", "submitted at", "registered", "date added", "created at", "timestamp"],
    "source_record_id": ["record id", "contact id", "id"],
    "crm_owner": ["contact owner"],
    "crm_lifecycle": ["lifecycle stage"],
    "city": ["city"], "state": ["state", "state/region", "region"], "country": ["country", "country/region"],
    "comment_text": ["comment", "comment text", "message", "notes"],
    "headline": ["headline"],
}


def resolve_columns(header, overrides):
    low = {h.lower().strip(): h for h in header}
    mapping = {}
    for field, aliases in CSV_ALIASES.items():
        for a in aliases:
            if a in low:
                mapping[field] = low[a]
                break
    for part in [p for p in (overrides or "").split(",") if p.strip()]:
        k, _, v = part.partition("=")
        k = k.strip()
        k = {"title": "title_raw", "company": "company_name_raw", "email": "email_raw",
             "name": "full_name", "first": "first_name", "last": "last_name",
             "linkedin": "linkedin_url", "domain": "company_domain_hint", "date": "touch_date",
             "id": "source_record_id"}.get(k, k)
        mapping[k] = v.strip()
    return mapping


def adapt_csv(args):
    if not args.touch_type:
        sys.exit("csv adapter needs --touch-type (ask JK how people got on this list)")
    if args.touch_type not in C.TOUCH_TYPES:
        sys.exit(f"--touch-type must be one of {C.TOUCH_TYPES}")
    source_type = args.source_type or ("campaign_list" if args.campaign else "other_list")
    out = []
    bases = [os.path.splitext(os.path.basename(p))[0] for p in args.input]
    for path in args.input:
        header = C.read_csv_header(path)
        hs = set(header)
        if "Last Captured URL" in hs or "First Captured URL" in hs or "LinkedIn Key" in hs or \
                {"First Seen At", "Last Seen At"} <= hs:
            sys.exit(f"{os.path.basename(path)} is an RB2B Baserow CSV export. Pull the table as JSON through "
                     "the API instead (baserow.sh rows 1171339 --raw) and use --adapter rb2b-baserow; the CSV "
                     "export mixes date formats and loses page detail.")
        mapping = resolve_columns(header, args.map)
        print(f"Column mapping for {os.path.basename(path)}:")
        for k in sorted(mapping):
            print(f"  {k} <- {mapping[k]}")
        unmapped = [h for h in header if h not in mapping.values()]
        if unmapped:
            print(f"  unmapped (kept in touches_json.extra): {', '.join(unmapped)}")
        is_hubspot = "source_record_id" in mapping and mapping["source_record_id"].lower() in ("record id", "contact id")
        base = os.path.splitext(os.path.basename(path))[0]
        if bases.count(base) > 1:  # two inputs share a file name: keep their lead ids apart
            base = f"{os.path.basename(os.path.dirname(os.path.abspath(path)))}-{base}"
        rows_in = C.read_csv(path)
        slash = args.date_format
        if "touch_date" in mapping:
            two_digit = [r.get(mapping["touch_date"], "") for r in rows_in
                         if re.match(r"^\s*\d{1,2}/\d{1,2}/\d{2}\s*$", r.get(mapping["touch_date"], "") or "")]
            if two_digit:  # "9/25/26" is never guessed: 1926 and 2026 are both possible
                sys.exit(f"{os.path.basename(path)}: {len(two_digit)} dates have two-digit years "
                         f"(e.g. {two_digit[0]!r}). Re-export with four-digit years and rerun.")
            found, problem = C.slash_order(r.get(mapping["touch_date"], "") for r in rows_in)
            if problem and not slash:
                sys.exit(f"{os.path.basename(path)}: {problem}. Rerun with --date-format dmy or --date-format mdy.")
            slash = slash or found or "dmy"
            if found and not args.date_format:
                print(f"  dates read as {found} (inferred from values over 12)")
        for i, r in enumerate(rows_in, start=2):
            row = blank_row()
            get = lambda f: r.get(mapping[f], "") if f in mapping else ""  # noqa: E731
            rec = C.clean(get("source_record_id")) or str(i)
            row.update({
                "lead_id": (f"hubspot:{rec}" if is_hubspot else f"csv:{base}:{rec}"),
                "source_type": source_type,
                "source_system": "hubspot_list" if is_hubspot else "csv",
                "source_record_id": rec, "source_file": os.path.basename(path),
                "source_detail": args.campaign or base,
                "touch_type": args.touch_type,
                "touch_date": C.iso(C.parse_date(get("touch_date"), slash or "dmy")),
                "touch_ts": C.parse_ts(get("touch_date")) or "",
                "touch_date_basis": "list_added" if get("touch_date") else "unknown",
                "email_origin": "person_supplied" if args.touch_type in C.PERSON_SUPPLIED_TOUCHES else "source_matched",
                "is_company_only": "no",
                "full_name": get("full_name"), "first_name": get("first_name"),
                "last_name": get("last_name"), "title_raw": get("title_raw"),
                "company_name_raw": get("company_name_raw"),
                "email_raw": C.clean(get("email_raw")).lower(),
                "linkedin_url": get("linkedin_url"), "headline": get("headline"),
                "city": get("city"), "state": get("state"), "country": get("country"),
                "comment_text": C.clean(get("comment_text"))[:280],
                "company_domain_hint": C.registrable_domain(get("company_domain_hint")),
                "company_website_raw": C.registrable_domain(get("company_domain_hint")),
            })
            hint = " ".join(x for x in (get("crm_lifecycle"), ("owner " + get("crm_owner")) if get("crm_owner") else "") if x)
            row["crm_hint"] = f"HubSpot list: {hint}" if hint else ""
            extra = {h: r.get(h, "") for h in unmapped if C.clean(r.get(h, ""))}
            if extra:
                row["touches_json"] = json.dumps({"extra": extra}, sort_keys=True)
            if not row["full_name"] and not row["first_name"] and not row["last_name"]:
                row["is_company_only"] = "yes"
            out.append(finish(row))
    return out


ADAPTERS = {"rb2b-baserow": adapt_rb2b_baserow, "rb2b-export": adapt_rb2b_export,
            "social": adapt_social, "csv": adapt_csv}

# ---------------------------------------------------------------------------
# Dedupe and profile
# ---------------------------------------------------------------------------

def merge_key(row):
    if row["is_company_only"] == "yes":
        return ("company", row["company_key"] or row["lead_id"])
    if row["linkedin_url"]:
        return ("li", row["linkedin_url"])
    if row["email_raw"]:
        return ("email", row["email_raw"])
    if row["full_name"] and row["company_key"]:
        return ("name", row["full_name"].lower() + "|" + row["company_key"])
    return ("id", row["lead_id"])


def dedupe(rows):
    """Collapse repeat touches by the same person (or company-only company).
    The kept lead_id is the earliest touch; touch_date becomes the newest."""
    groups = {}
    order = []
    for r in rows:
        k = merge_key(r)
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(r)
    kept, dupes = [], []
    for k in order:
        g = sorted(groups[k], key=lambda r: (r["touch_date"] or "9999", r["lead_id"]))
        base = dict(g[0])
        if len(g) > 1:
            touches = []
            pages = []
            for r in g:
                touches.append({"lead_id": r["lead_id"], "date": r["touch_date"],
                                "detail": r["source_detail"], "touch_type": r["touch_type"]})
                for p in r["pages_all"].split(";"):
                    if p and p not in pages:
                        pages.append(p)
                if r is not g[0]:
                    dupes.append({"kept_lead_id": base["lead_id"], "merged_lead_id": r["lead_id"],
                                  "merge_key": f"{k[0]}:{k[1]}"})
                for f in ("email_raw", "title_raw", "linkedin_url", "company_name_raw"):
                    if not base[f] and r[f]:
                        base[f] = r[f]
            newest = g[-1]
            base["touch_date"] = newest["touch_date"]
            base["source_detail"] = newest["source_detail"]
            base["referrer_raw"] = newest["referrer_raw"] or base["referrer_raw"]
            base["pages_all"] = ";".join(pages)
            base["touch_count"] = str(sum(int(r["touch_count"] or 1) for r in g))
            base["touches_json"] = json.dumps(touches, sort_keys=True)
        kept.append(base)
    return kept, dupes


def work_domain(row):
    d = C.email_domain(row["email_raw"])
    return d if d and not C.is_personal_domain(d) else ""


def assign_company_keys(rows):
    """Adjust pre-research name keys across the whole file. Nothing is ever merged
    across different names: an email domain can be stale (an old employer), so a
    shared domain is only flagged for the adjudicator (key_note), never acted on.
    - One name on one domain (or none): every row of that name, with or without an
      email, shares name:<name>.
    - One name on several work-email or website domains (Acme at acme.com and acme.io):
      split into name:<name>@<domain>. A row of that name with no domain stays on
      name:<name> and is flagged, because it could be either company.
    - Different names on one work-email domain (CV and CV Christian Vision at
      cvglobal.co, or "Acme Robotics" with a stale oldco.com address): flagged on
      both keys; research and the adjudicator decide."""
    def dom_of(r):
        d = work_domain(r) or C.registrable_domain(r["company_website_raw"])
        return d if d and not C.is_personal_domain(d) else ""

    doms = {}
    for r in rows:
        if r["company_key"].startswith("name:") and dom_of(r):
            doms.setdefault(r["company_key"], set()).add(dom_of(r))
    for r in rows:
        k = r["company_key"]
        if len(doms.get(k, ())) > 1:
            if dom_of(r):
                r["company_key"] = f"{k}@{dom_of(r)}"
            else:
                r["key_note"] = (f"this name appears with several domains in the file "
                                 f"({', '.join(sorted(doms[k]))}) and this row has none; confirm which company")
    by_dom = {}
    for r in rows:
        if r["company_key"].startswith("name:") and work_domain(r):
            by_dom.setdefault(work_domain(r), set()).add(r["company_key"])
    for d, keys in by_dom.items():
        if len(keys) > 1:
            names = ", ".join(sorted(k[5:].split("@")[0] for k in keys))
            for r in rows:
                if r["company_key"] in keys and not r.get("key_note"):
                    r["key_note"] = f"different names share the email domain {d} ({names}); confirm same company or a stale email"
    return rows


def drop_repeat_ids(rows):
    """Overlapping inputs (two exports, overlapping pages) repeat a record id.
    Keep the first copy; log the rest in 01-dupes.csv."""
    seen, kept, repeats = set(), [], []
    for r in rows:
        if r["lead_id"] in seen:
            repeats.append({"kept_lead_id": r["lead_id"], "merged_lead_id": r["lead_id"],
                            "merge_key": "repeat of the same record id"})
            continue
        seen.add(r["lead_id"])
        kept.append(r)
    return kept, repeats


def prior_lead_ids(folder):
    """Lead ids already handled by an earlier run folder."""
    ids = {r["lead_id"] for r in C.read_csv(os.path.join(folder, "work", "01-canonical.csv"))}
    ids |= {r["merged_lead_id"] for r in C.read_csv(os.path.join(folder, "work", "01-dupes.csv"))}
    for f in os.listdir(folder) if os.path.isdir(folder) else []:
        if f.endswith("Leads.csv"):
            ids |= {r.get("Lead ID", "") for r in C.read_csv(os.path.join(folder, f))}
    ids.discard("")
    if not ids:
        sys.exit(f"--exclude-prior: no lead ids found in {folder}")
    return ids


def profile(rows):
    dates = sorted(r["touch_date"] for r in rows if r["touch_date"])
    first, last = (dates[0], dates[-1]) if dates else ("", "")
    zero_days = []
    # social touch dates are scraper batch dates, so a day with no rows says nothing
    social = bool(rows) and all(r["source_type"] == "social_engagement" for r in rows)
    if dates and not social:
        have = set(dates)
        d = C.parse_date(first)
        end = C.parse_date(last)
        while d <= end:
            if d.isoformat() not in have:
                zero_days.append(d.isoformat())
            d += timedelta(days=1)
    n = len(rows) or 1
    return {
        "date_first": first, "date_last": last, "zero_days": zero_days,
        "gaps_profiled": not social,
        "company_only_share": round(sum(r["is_company_only"] == "yes" for r in rows) / n, 3),
        "blank_title_share": round(sum(not r["title_raw"] for r in rows if r["is_company_only"] == "no") / n, 3),
        "undated_rows": sum(not r["touch_date"] for r in rows),
    }


def compress_days(days):
    """['2026-09-11','2026-09-12','2026-09-13'] -> '2026-09-11 to 2026-09-13'."""
    if not days:
        return "none"
    spans, start, prev = [], days[0], days[0]
    for d in days[1:]:
        if C.parse_date(d) - C.parse_date(prev) == timedelta(days=1):
            prev = d
            continue
        spans.append(start if start == prev else f"{start} to {prev}")
        start = prev = d
    spans.append(start if start == prev else f"{start} to {prev}")
    return "; ".join(spans)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--adapter", required=True, choices=sorted(ADAPTERS))
    ap.add_argument("--input", required=True, nargs="+")
    ap.add_argument("--table", default="1171339")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--source-label", default="")
    ap.add_argument("--source-type", choices=C.SOURCE_TYPES)
    ap.add_argument("--touch-type")
    ap.add_argument("--campaign", default="")
    ap.add_argument("--map", default="")
    ap.add_argument("--as-of", default="")
    ap.add_argument("--ids", default="", help="comma list of source_record_ids to keep (fixtures)")
    ap.add_argument("--date-format", choices=["dmy", "mdy"], default="",
                    help="csv adapter: how to read slash dates (required when the file is ambiguous)")
    ap.add_argument("--exclude-prior", nargs="+", default=[],
                    help="run folder(s) whose lead ids are skipped (new-since-last-run)")
    ap.add_argument("--test-run", action="store_true",
                    help="mark this run as a test; --prior-dir scans skip it")
    args = ap.parse_args(argv)

    rows = ADAPTERS[args.adapter](args)
    if args.ids:
        keep = {x.strip() for x in args.ids.split(",")}
        rows = [r for r in rows if r["source_record_id"] in keep]
    rows, repeats = drop_repeat_ids(rows)
    pulled = len(rows)
    if not rows:
        sys.exit("no rows in the input; nothing to qualify")
    if args.since or args.until:
        # full timestamps compare on touch_ts; a bare date covers the whole day
        lo = C.parse_ts(args.since) if args.since else "0000"
        hi = (C.parse_ts(args.until) if args.until else "9999")
        if args.until and len(C.clean(args.until)) == 10:
            hi = args.until + "T23:59:59Z"
        rows = [r for r in rows if (r["touch_ts"] or (r["touch_date"] + "T00:00:00Z" if r["touch_date"] else ""))
                and lo <= (r["touch_ts"] or r["touch_date"] + "T00:00:00Z") <= hi]
    excluded = 0
    if args.exclude_prior:
        prior = set()
        for folder in args.exclude_prior:
            prior |= prior_lead_ids(folder)
        before = len(rows)
        rows = [r for r in rows if r["lead_id"] not in prior]
        excluded = before - len(rows)
    if not rows:
        why = f"all {excluded} rows are already in the prior run" if excluded else "no rows fall inside the window"
        sys.exit(f"nothing new to qualify: {why}. No files written.")
    in_window = len(rows)
    assign_company_keys(rows)
    kept, dupes = dedupe(rows)
    assert in_window == len(kept) + len(dupes), "reconciliation failed: source != canonical + merged"
    dupes = repeats + dupes

    C.write_csv(C.work(args.run, "01-canonical.csv"), kept, CANONICAL_FIELDS)
    C.write_csv(C.work(args.run, "01-dupes.csv"), dupes, ["kept_lead_id", "merged_lead_id", "merge_key"])

    prof = profile(kept)
    run = C.load_run(args.run)
    run.update({
        "adapter": args.adapter,
        "source_label": args.source_label or {"rb2b-baserow": "RB2B", "rb2b-export": "RB2B",
                                              "social": "LinkedIn Engagement", "csv": args.campaign or "List"}[args.adapter],
        "source_type": kept[0]["source_type"] if kept else "",
        "campaign": args.campaign,
        "as_of": args.as_of or run.get("as_of") or date.today().isoformat(),
        "window_requested": [args.since or "", args.until or ""],
        "source_rows_pulled": pulled, "source_rows_in_window": in_window,
        "canonical_rows": len(kept), "merged_rows": len(dupes) - len(repeats),
        "repeated_ids_dropped": len(repeats), "excluded_prior": excluded,
        "exclude_prior": args.exclude_prior,
        "profile": prof,
        "caps": run.get("caps") or C.DEFAULT_CAPS,
        "test_run": bool(args.test_run or run.get("test_run")),
    })
    C.save_run(args.run, run)
    gaps = compress_days(prof["zero_days"]) if prof["gaps_profiled"] else \
        "not profiled (social touch dates are scraper batch dates)"
    C.append_log(args.run, f"S0 adapter={args.adapter} pulled={pulled} in_window={in_window} "
                           f"canonical={len(kept)} merged={len(dupes) - len(repeats)} "
                           f"repeated_ids_dropped={len(repeats)} excluded_prior={excluded}")
    C.append_log(args.run, f"S0 actual date range {prof['date_first']} to {prof['date_last']}; "
                           f"zero-row days: {gaps}; "
                           f"company-only share {prof['company_only_share']}; blank-title share {prof['blank_title_share']}")
    print(f"canonical rows: {len(kept)} (pulled {pulled}, in window {in_window}, merged {len(dupes) - len(repeats)}, "
          f"repeated ids dropped {len(repeats)}, already in a prior run {excluded})")
    print(f"actual date range: {prof['date_first']} to {prof['date_last']}")
    print(f"zero-row days: {gaps}")
    print(f"company-only share: {prof['company_only_share']}, blank-title share: {prof['blank_title_share']}")


if __name__ == "__main__":
    main()
