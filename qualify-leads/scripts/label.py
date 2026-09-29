#!/usr/bin/env python3
"""S4 and S7: turn facts into labels. Deterministic: same inputs, same output.

Reads (all optional except canonical and pass1; missing fact files just mean
"not researched yet"):
  work/01-canonical.csv, work/02-pass1.csv, work/run.json
  work/03-research-companies-*.csv   company facts (research-brief.md schema)
  work/03-research-people-*.csv      person facts
  work/03-triage-*.csv               knowledge triage rows
  work/04-crm-companies.csv, work/04-crm-contacts.csv   read-only HubSpot facts
  work/07-committee-*.csv            enrichment committees (Buyer to target)
  work/overrides.csv                 fact corrections: level,key,field,new_value,reason,source_url
  work/02-prior-companies.csv        name-collision map from classify.py

Writes work/05-qualified.csv, work/05-company-rollup.csv, work/06-tier1.csv
(or work/06-tier1-candidates.csv once Tier 1 is frozen), and work/05-changes.csv
listing every label that differs from the previous 05-qualified.csv.

No judgment happens here. Workers supply facts; this script applies the label
spec in references/label-spec.md. To change a label, change a fact (overrides.csv).

Usage:
  label.py --run RUN_DIR [--out-dir DIR] [--freeze-tier1] [--tier1-max N]
"""
import argparse
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
from classify import classify_title, is_student_educator  # noqa: E402

COMPANY_FACT_FIELDS = [
    "company_key", "company_key_final", "company_name_verified", "domains",
    "what_they_do", "us_company", "employees_best", "employees_text",
    "employees_source", "size_tier", "parent_name", "parent_employees",
    "parent_tier", "parent_centralized", "sells_staffing_or_dev", "sells_why",
    "public_body", "consumer_or_self", "structural_no_need", "no_need_why",
    "can_buy", "ats_type", "ats_slug", "hiring_source_url", "hiring_checked",
    "open_roles_total", "open_tech_roles", "open_tech_roles_us",
    "hiring_examples", "need_signals", "strength_downgrade", "service_fit",
    "service_fit_why", "segment", "sources", "research_depth",
    "collision_resolved", "tech_role_locations", "peer_buys_recruiting", "known_buyer",
]
PERSON_FACT_FIELDS = [
    "lead_id", "works_there", "works_there_source", "title_verified",
    "buyer_role", "buyer_role_why", "vendor_selling", "job_seeker",
    "email_found", "email_found_source", "email_risk", "email_validated_at",
    "domain_accept_all", "bounceban_result", "smtp_valid", "deepline_verified",
]
TRIAGE_FIELDS = ["company_key", "company_name", "what_they_do", "employees_text",
                 "employees_best", "size_tier", "us_company", "triage", "drop_code", "why"]
TRIAGE_CODES = {"COMPETITOR_STAFFING", "PUBLIC_BODY_NON_BUYER", "CONSUMER_SELF_EMPLOYED",
                "CANNOT_BUY", "STRUCTURAL_NO_NEED", "NOT_US", "OVER_2000", "UNIDENTIFIABLE"}
CRM_COMPANY_FIELDS = ["company_key_final", "checked", "hs_company_id", "hs_company_name",
                      "match_type", "owner_name", "owner_active", "lifecycle",
                      "open_deals", "open_deal_summary", "closed_won_24m_count",
                      "closed_won_24m_amount", "last_activity"]
CRM_CONTACT_FIELDS = ["lead_id", "checked", "hs_contact_id", "match_type", "email",
                      "job_title", "contact_owner", "contact_owner_active",
                      "lifecycle", "lead_status"]
COMMITTEE_FIELDS = [
    "company_key_final", "order", "full_name", "first_name", "last_name", "title",
    "role_in_decision", "priority", "email", "email_source", "email_risk",
    "email_validated_at", "domain_accept_all", "bounceban_result", "smtp_valid",
    "deepline_verified", "employer_domain", "works_there", "works_there_source",
    "linkedin_url", "lead_id", "notes",
]
QUALIFIED_FIELDS = [
    "lead_id", "rank", "action", "verdict", "account_strength", "primary_code",
    "reason_codes", "why", "next_step", "watch_outs", "name", "title", "title_group", "company",
    "company_key_final", "website", "what_they_do", "employees_text", "employees_best",
    "size_band", "size_status", "size_tier", "headcount_source", "us_company",
    "hiring_status", "open_tech_roles_display", "open_tech_roles_us", "example_roles",
    "need_signals_display", "service_fit", "source_label", "what_they_did",
    "touch_date", "touch_date_display", "touch_type", "intent", "crm_state",
    "crm_status", "hubspot_owner", "routing_owner", "suggested_owner",
    "buyer_to_target", "email", "email_status", "email_source", "linkedin",
    "confidence", "city", "state", "sources", "is_company_only", "segment",
    "label_warnings",
]
ROLLUP_FIELDS = [
    "company_key_final", "company_name", "best_action", "best_verdict",
    "account_strength", "rows", "n_contact_now", "n_tell_owner", "n_account_play",
    "n_review", "n_low", "n_drop", "lead_row_id", "lead_ids", "crm_state",
    "open_tech_roles_us", "tech_roles_all", "best_intent", "freshest_need_days", "newest_touch",
    "collision", "collision_resolved",
]
TIER1_FIELDS = ["company_key_final", "company_name", "tier1_reason", "best_action",
                "account_strength", "lead_ids", "projected_moltsets",
                "projected_deepline", "packet_file", "collision"]

ABSOLUTE = ["COMPLIANCE_DNC", "INTERNAL"]
COMPANY_CODES = ["COMPETITOR_STAFFING", "NOT_US", "OVER_2000",
                 "PUBLIC_BODY_NON_BUYER", "CONSUMER_SELF_EMPLOYED", "CANNOT_BUY",
                 "STRUCTURAL_NO_NEED", "TINY_NO_BUDGET"]
BOARD_SOURCES = ("ats_api", "careers_page", "linkedin_jobs")  # a job list that was actually read
PERSON_CODES = ["VENDOR_SELLING", "JOB_SEEKER", "STUDENT_EDUCATOR", "NOT_AT_COMPANY",
                "EXCLUDED_TITLE", "UNRELATED_TITLE", "PERSONAL_EMAIL_SUBMITTED"]
INS_CODES = ["INS_NO_PERSON", "INS_NO_COMPANY", "INS_NO_TITLE", "INS_SIZE_UNKNOWN",
             "INS_US_UNKNOWN"]
OPEN_CODES = ["OPEN_PARENT", "OPEN_AUTHORITY", "OPEN_NEED", "OPEN_EMPLOYMENT", "OPEN_EMAIL",
              "OPEN_SIZE", "OPEN_TINY"]
NO_RESEARCH_CODES = set(ABSOLUTE) | {"JOB_SEEKER", "STUDENT_EDUCATOR", "EXCLUDED_TITLE",
                                     "PERSONAL_EMAIL_SUBMITTED"}
# Person codes that are about the buying role, not an excluded audience. A row with
# only these can still lead to the account, so missing account evidence must not Drop it.
SOFT_PERSON_CODES = {"UNRELATED_TITLE", "NOT_AT_COMPANY"}
GAP_CODES = ["GAP_HIRING_NOT_CHECKED", "GAP_HIRING_UNREAD"]
GAP_SHORT = {"GAP_HIRING_NOT_CHECKED": "hiring", "GAP_HIRING_UNREAD": "hiring",
             "INS_SIZE_UNKNOWN": "headcount", "INS_US_UNKNOWN": "the US base"}
NEED_WINDOW_MONTHS = 18          # JK ruling 2026-09-28 (was 12)
NEED_SIGNAL_TYPES = {"funding", "new_tech_leader", "launch", "acquisition", "modernization",
                     "growth", "ai_initiative"}  # "contraction" is recorded but is not a need
ALLOWED_DOWNGRADES = {"PARENT_UNCLEAR", "CONTRACTION", "ROLES_STALE"}  # offshore hiring is neutral

SEGMENT_OWNERS = {"fintech": "Kent Richeson", "banking_insurance_wealth": "Derris Butler",
                  "faith": "Spencer Hahn", "proptech_construction": "Blake Fisher",
                  "cloud_infrastructure": "Shiley Johnson", "other": "Derris Butler"}
DEFAULT_OWNER = "Jesse Kinzer"
FIT_ROLES = {"Recruiting": "the Head of Talent Acquisition or VP Engineering",
             "Embedded": "the VP Engineering or CTO", "Scoped": "the CTO or VP Product",
             "None": "the CTO or VP Engineering", "": "the CTO or VP Engineering"}
EMAIL_PHRASE = {"From HubSpot": "work email on the HubSpot record",
                "Given by the person": "work email they gave us",
                "Verified": "verified work email",
                "Verified, catch-all domain": "work email confirmed deliverable on a catch-all domain"}
OPEN_SHORT = {"OPEN_PARENT": "whether buying sits with the parent company",
              "OPEN_AUTHORITY": "whether {name} has buying authority",
              "OPEN_NEED": "for a current tech hiring or project need",
              "OPEN_EMPLOYMENT": "that {name} still works there",
              "OPEN_EMAIL": "a work email for {name}",
              "OPEN_SIZE": "the real headcount",
              "OPEN_TINY": "for budget at a very small company"}
SOURCE_LABEL = {"rb2b_visit": "RB2B website visit", "social_engagement": "LinkedIn engagement"}


class Blank(dict):
    def __missing__(self, key):
        return ""


def fill(template, values):
    """Fill a reason template. Inserted values lose a trailing period so a
    template's own punctuation never doubles up."""
    return template.format_map(Blank({k: C.clean(v).rstrip(".") for k, v in values.items()}))


ABSENCE_RE = re.compile(r"\b(no|none|nothing)\b[^.;]*\b(found|seen|visible|identified|surfaced|observed)\b|"
                        r"\bnot (found|seen|visible|identified)\b|\bnone found\b", re.I)


def structural_reason_ok(reason):
    """STRUCTURAL_NO_NEED needs a stated business-model cause ("museum; no software product;
    IT run by a vendor"). A reason that rests on not finding anything ("no tech hiring need
    found") is an absence of evidence and cannot drop the account."""
    return bool(C.clean(reason)) and not ABSENCE_RE.search(reason)


def clip(text, n):
    """Cut at a word boundary with a clean end: no half word, no trailing comma."""
    text = C.clean(text)
    if len(text) <= n:
        return text
    return text[:n + 1].rsplit(" ", 1)[0].rstrip(",;:( ")


LONG_FIELDS = ("no_need_why", "works_there_source", "employees_source", "title", "parent_name", "company")


def fit(template, values, limit=160):
    """Fill a template within `limit` characters without cutting a sentence: first
    shorten long inserted values to their first clause, then to a few words."""
    text = fill(template, values)
    if len(text) <= limit:
        return text
    v = dict(values)
    for k in LONG_FIELDS:
        if "{" + k + "}" in template and len(C.clean(v.get(k, ""))) > 25:
            v[k] = re.split(r"[,;(]", C.clean(v[k]))[0].strip()
            text = fill(template, v)
            if len(text) <= limit:
                return text
    for k in LONG_FIELDS:
        if "{" + k + "}" in template:
            v[k] = clip(v[k], 40)
    return C.truncate(fill(template, v), limit)


def approx(text):
    """'about 100' -> '100' so templates that say 'about {x}' read once."""
    return re.sub(r"^(about|approximately|around|roughly|~)\s*", "", C.clean(text), flags=re.I)


def fmt_int(v):
    n = C.to_int(v)
    return f"{n:,}" if n is not None else C.clean(v)


def slug(key):
    return re.sub(r"[^a-z0-9.\-]+", "_", key.lower()).strip("_")

# ---------------------------------------------------------------------------
# Fact loading
# ---------------------------------------------------------------------------

def load_facts(run_dir):
    f = {}
    warnings = []
    comp = {}
    for path in C.glob_work(run_dir, "03-research-companies-"):
        for r in C.read_csv(path):
            k = C.clean(r.get("company_key"))
            if not k:
                continue
            if k in comp:
                warnings.append(f"company {k} researched twice; {os.path.basename(path)} wins")
            comp[k] = {fld: C.clean(r.get(fld, "")) for fld in COMPANY_FACT_FIELDS}
    f["companies"] = comp
    people = {}
    for path in C.glob_work(run_dir, "03-research-people-"):
        for r in C.read_csv(path):
            lid = C.clean(r.get("lead_id"))
            if lid:
                people[lid] = {fld: C.clean(r.get(fld, "")) for fld in PERSON_FACT_FIELDS}
    f["people"] = people
    tri = {}
    for path in C.glob_work(run_dir, "03-triage-"):
        for r in C.read_csv(path):
            k = C.clean(r.get("company_key"))
            if k:
                tri[k] = {fld: C.clean(r.get(fld, "")) for fld in TRIAGE_FIELDS}
    f["triage"] = tri
    f["crm_companies"] = {C.clean(r.get("company_key_final")): r
                          for r in C.read_csv(C.work(run_dir, "04-crm-companies.csv"))}
    f["crm_contacts"] = {C.clean(r.get("lead_id")): r
                         for r in C.read_csv(C.work(run_dir, "04-crm-contacts.csv"))}
    committees = defaultdict(list)
    for path in C.glob_work(run_dir, "07-committee-"):
        for r in C.read_csv(path):
            committees[C.clean(r.get("company_key_final"))].append(r)
    for k in committees:
        committees[k].sort(key=lambda r: (C.to_int(r.get("order")) or 99, r.get("full_name", "")))
    f["committees"] = committees
    f["overrides"] = C.read_csv(C.work(run_dir, "overrides.csv"))
    f["prior"] = C.read_csv(C.work(run_dir, "02-prior-companies.csv"))
    f["warnings"] = warnings
    return f


def apply_overrides(facts):
    """Overrides change facts, never labels. level=company keys on company_key or
    company_key_final; level=person keys on lead_id."""
    bad = []
    for o in facts["overrides"]:
        level, key, field = C.clean(o.get("level")), C.clean(o.get("key")), C.clean(o.get("field"))
        val = C.clean(o.get("new_value"))
        if level == "company":
            if field not in COMPANY_FACT_FIELDS or field == "company_key":
                bad.append(f"override field '{field}' is not a company fact")
                continue
            hits = [k for k, c in facts["companies"].items() if key in (k, c.get("company_key_final"))]
            if not hits:
                if key in facts["triage"]:
                    facts["companies"][key] = {fld: "" for fld in COMPANY_FACT_FIELDS}
                    facts["companies"][key]["company_key"] = key
                    hits = [key]
                else:
                    bad.append(f"override key '{key}' matches no researched company")
                    continue
            for k in hits:
                facts["companies"][k][field] = val
        elif level == "person":
            if field not in PERSON_FACT_FIELDS or field == "lead_id":
                bad.append(f"override field '{field}' is not a person fact")
                continue
            p = facts["people"].setdefault(key, {fld: "" for fld in PERSON_FACT_FIELDS})
            p["lead_id"] = key
            p[field] = val
        else:
            bad.append(f"override level '{level}' must be company or person")
    facts["warnings"].extend(bad)

# ---------------------------------------------------------------------------
# Derived facts
# ---------------------------------------------------------------------------

def months_ago(ym, as_of):
    m = re.match(r"(\d{4})-(\d{2})", ym or "")
    if not m:
        return None
    return (as_of.year * 12 + as_of.month) - (int(m.group(1)) * 12 + int(m.group(2)))


def parse_signals(text):
    out = []
    for part in [p.strip() for p in (text or "").split(";") if p.strip()]:
        m = re.match(r"(\d{4}-\d{2})(?:-\d{2})?\s+([a-z_]+):\s*(.*)", part)
        if m:
            out.append({"ym": m.group(1), "type": m.group(2), "text": m.group(3).strip()})
    return sorted(out, key=lambda s: s["ym"], reverse=True)


def parent_over(c):
    """The unit's buying runs through a parent of 2,000+ (A/B) or 5,000+ (any tier).
    Size and facts stay the operating company's; this only raises an open item."""
    pemp = C.to_int(c.get("parent_employees"))
    ptier = (c.get("parent_tier") or c.get("size_tier", "")).upper()
    return C.yes(c.get("parent_centralized")) and pemp is not None and (
        (ptier in ("A", "B") and pemp >= 2000) or pemp >= 5000)


def size_status(c):
    emp = C.to_int(c.get("employees_best"))
    tier = c.get("size_tier", "").upper()
    if emp is None or tier not in ("A", "B", "C"):
        return "unknown", ""
    if tier in ("A", "B"):
        return ("verified_over", "OVER_2000") if emp >= 2000 else ("verified_under", "")
    if emp >= 5000:
        return "verified_over", "OVER_2000"
    if emp >= 1000:
        return "straddles", ""
    return "likely_under", ""


def size_band(emp, status):
    if status == "unknown" or emp is None:
        return "Unknown"
    for hi, band in ((10, "1-10"), (50, "11-50"), (200, "51-200"), (500, "201-500"),
                     (1000, "501-1,000"), (1999, "1,001-1,999")):
        if emp <= hi:
            return band
    return "2,000+"


def hiring_status(c):
    checked = c.get("hiring_checked", "")
    total, tech, us = (C.to_int(c.get(k)) for k in ("open_roles_total", "open_tech_roles", "open_tech_roles_us"))
    if checked in ("", "not_checked"):
        return "Not checked"
    if us and us >= 1:
        return "Hiring tech roles"
    if tech and tech >= 1:
        return "Hiring tech roles, none in US"
    if checked in BOARD_SOURCES + ("hirebase", "search"):
        if total and total >= 1:
            return "Hiring, non-tech only"
        if checked in BOARD_SOURCES and total == 0:
            return "No open roles found"  # includes a careers page that says "coming soon"
    return "Unknown"


def email_status(email, domains, origin, from_hubspot, v):
    """v = verification facts dict. Order is the label spec's table 3.3."""
    if not email or "@" not in email:
        return "None"
    d = C.email_domain(email)
    if C.is_personal_domain(email.rsplit("@", 1)[-1]):
        return "Personal"
    if domains and d not in domains:
        return "Wrong domain"
    risk = C.clean(v.get("email_risk")).upper()
    bb = C.clean(v.get("bounceban_result")).lower()
    accept_all = C.clean(v.get("domain_accept_all")).lower()
    if bb == "undeliverable" or risk in ("D", "E", "F"):
        return "Undeliverable"
    if from_hubspot:
        return "From HubSpot"
    if origin == "person_supplied":
        return "Given by the person"
    validated = C.parse_date(v.get("email_validated_at"))
    as_of = v.get("_as_of")
    fresh = validated is not None and as_of is not None and (as_of - validated).days <= 90
    if (risk == "A" and fresh) or (C.yes(v.get("smtp_valid")) and accept_all != "yes") or \
            C.yes(v.get("deepline_verified")) or (bb == "deliverable" and accept_all != "yes"):
        return "Verified"
    if accept_all == "yes" and bb == "deliverable":
        return "Verified, catch-all domain"
    if accept_all == "yes":
        return "Catch-all, unconfirmed"
    return "Unverified work email"


def crm_state(cc, ct):
    if not cc and not ct:
        return "not_checked"
    cc = cc or {}
    ct = ct or {}
    if cc and not C.yes(cc.get("checked")) and not ct:
        return "not_checked"
    if C.clean(cc.get("match_type")) == "name":
        return "possible_match"
    if (C.to_int(cc.get("open_deals")) or 0) > 0:
        return "open_deal"
    if (C.to_int(cc.get("closed_won_24m_count")) or 0) > 0:
        return "customer"
    owners = [(cc.get("owner_name"), cc.get("owner_active")),
              (ct.get("contact_owner"), ct.get("contact_owner_active"))]
    if any(C.clean(n) and C.yes(a) for n, a in owners):
        return "owned_active"
    if any(C.clean(n) for n, a in owners):
        return "owned_inactive"
    if C.clean(cc.get("hs_company_id")) or C.clean(ct.get("hs_contact_id")):
        return "unowned"
    return "not_found"


def owner_text(name, active):
    n = C.clean(name)
    if not n:
        return ""
    return n if C.yes(active) else f"{n} (inactive)"


def crm_status_plain(state, cc, ct, is_person):
    cc, ct = cc or {}, ct or {}
    if state == "not_checked":
        return "Not checked in HubSpot."
    if state == "possible_match":
        nm = C.clean(cc.get("hs_company_name")) or "a similar name"
        return f"HubSpot has a company named {nm}; confirm it is the same company."
    parts = []  # most important first; the tail is dropped when the sentence runs long
    if C.clean(cc.get("hs_company_id")):
        own = owner_text(cc.get("owner_name"), cc.get("owner_active"))
        s = "HubSpot company record, " + (f"owner {own}" if own else "unowned")
        if C.clean(cc.get("lifecycle")):
            s += f", {C.clean(cc.get('lifecycle'))} stage"
        parts.append(s)
    elif C.yes(cc.get("checked")):
        parts.append("No HubSpot company record")
    won = C.to_int(cc.get("closed_won_24m_count")) or 0
    if won:
        amt = C.clean(cc.get("closed_won_24m_amount"))
        parts.append(f"customer, {won} closed-won deals in 24 months" + (f" ({amt})" if amt else ""))
    if (C.to_int(cc.get("open_deals")) or 0) > 0:
        parts.append("open deal: " + (C.clean(cc.get("open_deal_summary")) or f"{cc.get('open_deals')} open"))
    if is_person:
        if C.clean(ct.get("hs_contact_id")):
            own = owner_text(ct.get("contact_owner"), ct.get("contact_owner_active"))
            parts.append("this person is a HubSpot contact" + (f" owned by {own}" if own else ", unowned"))
        elif C.yes(ct.get("checked")):
            parts.append("this person is not a HubSpot contact")
    if state == "not_found" and not parts:
        return "Not in HubSpot; net-new."
    if state == "not_found":
        parts.append("net-new")
    while len(parts) > 1 and len("; ".join(parts)) + 1 > 160:
        parts.pop(-2 if parts[-1] == "net-new" else -1)
    s = "; ".join(parts)
    return C.truncate(s[0].upper() + s[1:] + ".", 160)

# ---------------------------------------------------------------------------
# One row
# ---------------------------------------------------------------------------

def company_facts_for(key, facts):
    """Research beats triage. Triage rows become C-tier pseudo facts; an
    override on a triage-only company overlays those pseudo facts."""
    res = facts["companies"].get(key) or {}
    deep = res.get("research_depth") in ("deep", "quick")
    t = facts["triage"].get(key)
    warn = []
    tri_code = ""
    c = {}
    if t and not deep:
        c = {fld: "" for fld in COMPANY_FACT_FIELDS}
        c.update({"company_key": key, "company_name_verified": t["company_name"],
                  "what_they_do": t["what_they_do"], "us_company": t["us_company"],
                  "employees_best": t["employees_best"], "employees_text": t["employees_text"],
                  "employees_source": "knowledge estimate", "size_tier": "C",
                  "research_depth": "knowledge", "hiring_checked": "not_checked"})
    for fld, v in res.items():
        if v:
            c[fld] = v
    if t:
        if C.clean(t["triage"]).lower() == "drop" and not deep:
            code = t["drop_code"]
            emp = C.to_int(t["employees_best"])
            if code not in TRIAGE_CODES:
                warn.append(f"triage drop_code '{code}' not allowed")
            elif code == "OVER_2000" and (emp is None or emp < 5000):
                warn.append(f"triage OVER_2000 ignored: estimate {t['employees_best'] or 'blank'} is under 5,000, research it")
            elif code == "CANNOT_BUY" and emp is not None and emp > 50:
                warn.append(f"triage CANNOT_BUY ignored: {emp} employees is over 50")
            else:
                tri_code = code
            c["_triage_why"] = t["why"]
        elif C.clean(t["triage"]).lower() == "keep" and not deep:
            warn.append("triage Keep not yet deep-researched")
    c.setdefault("company_key", key)
    return c, tri_code, warn


def label_row(canon, p1, facts, as_of, run):
    lid = canon["lead_id"]
    key = p1["company_key"]
    person = canon["is_company_only"] == "no"
    c, tri_code, warn = company_facts_for(key, facts) if key else ({}, "", [])
    pf = dict(facts["people"].get(lid) or {})
    final_key = C.clean(c.get("company_key_final")) or key
    domains = C.domain_list(c.get("domains", ""))
    if final_key and not final_key.startswith("name:"):
        d = C.registrable_domain(final_key)
        if d:
            domains.add(d)
    if not domains and c:
        # research gave no domain: fall back to the source website so a stale
        # employer email still reads as Wrong domain instead of passing unchecked
        d = C.registrable_domain(canon.get("company_website_raw", ""))
        if d and not C.is_personal_domain(d):
            domains.add(d)
    researched = bool(c.get("research_depth")) and c.get("research_depth") != "knowledge"

    # title
    title = C.clean(pf.get("title_verified")) or p1["title_used"]
    if pf.get("title_verified"):
        group = classify_title(title)[0]
    else:
        group = p1["title_group"] if person else "No title"
    br = C.clean(pf.get("buyer_role")).lower()
    if not br:
        br = ("yes" if group in C.PRIMARY_GROUPS else "partial" if group == "Secondary influencer"
              else "unknown" if group in ("Generic exec", "No title") else "no")

    # email: HubSpot contact email at the company domain beats everything
    ct = facts["crm_contacts"].get(lid)
    cc = facts["crm_companies"].get(final_key)
    raw = canon["email_raw"]
    crm_email = C.clean((ct or {}).get("email")).lower()
    verify = {"_as_of": as_of}
    if crm_email and "@" in crm_email and not C.is_personal_domain(crm_email.rsplit("@", 1)[-1]) and \
            (not domains or C.email_domain(crm_email) in domains):
        email, src, from_hs, origin = crm_email, "HubSpot contact record", True, "crm"
    elif C.clean(pf.get("email_found")):
        found = C.clean(pf["email_found"]).lower()
        # a verified copy of the address the person typed keeps "Given by the person"
        origin = canon["email_origin"] if found == raw else "research"
        email, src, from_hs = found, pf.get("email_found_source") or "research", False
        verify.update(pf)
    else:
        email, src, from_hs, origin = raw, ("the source list" if raw else ""), False, canon["email_origin"]
    estatus = email_status(email, domains, origin, from_hs, verify) if person else "None"

    # size, hiring, need
    status, over_code = size_status(c)
    emp = C.to_int(c.get("employees_best"))
    band = size_band(emp, status)
    tech = C.to_int(c.get("open_tech_roles"))
    tech_us = C.to_int(c.get("open_tech_roles_us"))
    hstatus = hiring_status(c)
    signals = parse_signals(c.get("need_signals"))
    fresh_signals = [s for s in signals if s["type"] in NEED_SIGNAL_TYPES and
                     (months_ago(s["ym"], as_of) if months_ago(s["ym"], as_of) is not None else 99) <= NEED_WINDOW_MONTHS]
    # tech roles anywhere count as demand: Midwestern sells global talent too (JK 2026-09-28)
    roles = max(tech or 0, tech_us or 0)
    offshore_only = roles >= 1 and (tech_us or 0) == 0
    need_found = bool(roles >= 1 or fresh_signals)

    # --- codes -----------------------------------------------------------
    p1codes = [x for x in p1["pass1_codes"].split(";") if x]
    codes = [x for x in ABSOLUTE if x in p1codes]
    comp = set()
    # Peer vendors (MSPs, IT services, dev shops, consultancies) are excluded by default.
    # Exception: research confirms the firm buys recruiting for its own staff AND this
    # person is that buyer. Named competitors and staffing names (pass one) never qualify.
    peer_buyer = (C.yes(c.get("peer_buys_recruiting")) and c.get("research_depth") in ("deep", "quick") and
                  person and (group == "Primary: recruiting/people" or C.clean(pf.get("buyer_role")).lower() == "yes"))
    if "COMPETITOR_STAFFING" in p1codes or tri_code == "COMPETITOR_STAFFING" or \
            (C.yes(c.get("sells_staffing_or_dev")) and not peer_buyer):
        comp.add("COMPETITOR_STAFFING")
    if C.clean(c.get("us_company")).lower() == "no" or tri_code == "NOT_US":
        comp.add("NOT_US")
    if status == "verified_over":
        comp.add(over_code)
    tech_or_ops = group in ("Primary: technology/product", "Primary: operations/transformation") or \
        (br == "yes" and group not in ("Excluded title", "Unrelated title"))
    if tri_code == "PUBLIC_BODY_NON_BUYER" and person and tech_or_ops:
        warn.append("triage PUBLIC_BODY_NON_BUYER ignored: this person is a technology or operating buyer")
    elif (C.yes(c.get("public_body")) and person and not tech_or_ops) or tri_code == "PUBLIC_BODY_NON_BUYER":
        comp.add("PUBLIC_BODY_NON_BUYER")
    if "CONSUMER_SELF_EMPLOYED" in p1codes or C.yes(c.get("consumer_or_self")) or tri_code == "CONSUMER_SELF_EMPLOYED":
        comp.add("CONSUMER_SELF_EMPLOYED")
    if C.clean(c.get("can_buy")).lower() == "no" or tri_code == "CANNOT_BUY":
        if emp is not None and emp > 50:
            warn.append(f"CANNOT_BUY ignored: {emp} employees is over 50")
        else:
            comp.add("CANNOT_BUY")
    if C.yes(c.get("structural_no_need")) or tri_code == "STRUCTURAL_NO_NEED":
        reason = C.clean(c.get("no_need_why") or c.get("_triage_why"))
        if structural_reason_ok(reason):
            comp.add("STRUCTURAL_NO_NEED")
        else:  # "no tech hiring need found" is an absence of evidence, not a business model
            warn.append("STRUCTURAL_NO_NEED ignored: the reason states no business-model cause "
                        f"({reason or 'blank'}); treated as an open item")
    # only on evidence: a counted A/B headcount and a job list that was actually read
    if emp is not None and emp < 11 and not need_found and C.clean(c.get("can_buy")).lower() != "yes" and \
            c.get("size_tier", "").upper() in ("A", "B") and c.get("hiring_checked") in BOARD_SOURCES:
        comp.add("TINY_NO_BUDGET")
    codes += [x for x in COMPANY_CODES if x in comp]

    if person:
        pc = set()
        if C.yes(pf.get("vendor_selling")):
            pc.add("VENDOR_SELLING")
        if "JOB_SEEKER" in p1codes or C.yes(pf.get("job_seeker")):
            pc.add("JOB_SEEKER")
        if group == "Excluded title":
            pc.add("STUDENT_EDUCATOR" if is_student_educator(title) else "EXCLUDED_TITLE")
        if C.clean(pf.get("works_there")).lower() == "no":
            pc.add("NOT_AT_COMPANY")
        if (group == "Unrelated title" and br != "yes") or (br == "no" and group not in ("Excluded title", "No title")):
            pc.add("UNRELATED_TITLE")  # research saying buyer_role = yes overrides the title table
        if "PERSONAL_EMAIL_SUBMITTED" in p1codes and estatus == "Personal":
            pc.add("PERSONAL_EMAIL_SUBMITTED")
        codes += [x for x in PERSON_CODES if x in pc]

    ins = []
    if not person:
        ins.append("INS_NO_PERSON")
    if not key or tri_code == "UNIDENTIFIABLE":
        ins.append("INS_NO_COMPANY")
    if person and group == "No title":
        ins.append("INS_NO_TITLE")
    if key and tri_code != "UNIDENTIFIABLE":
        if status in ("unknown", "straddles"):
            ins.append("INS_SIZE_UNKNOWN")
        if C.clean(c.get("us_company")).lower() not in ("yes", "no"):  # "no" is NOT_US above
            ins.append("INS_US_UNKNOWN")

    opens = []
    if person:
        if parent_over(c):
            opens.append("OPEN_PARENT")
        if group == "Secondary influencer" or br in ("partial", "unknown"):
            opens.append("OPEN_AUTHORITY")
        if not need_found:
            opens.append("OPEN_NEED")
        works = C.clean(pf.get("works_there")).lower()
        if works != "confirmed" and estatus not in C.QUALIFYING_EMAIL:
            opens.append("OPEN_EMPLOYMENT")
        if estatus not in C.QUALIFYING_EMAIL:
            opens.append("OPEN_EMAIL")
        if status == "likely_under":
            opens.append("OPEN_SIZE")
        if band == "1-10" and "TINY_NO_BUDGET" not in comp:
            opens.append("OPEN_TINY")

    if codes:
        verdict, primary = "Not qualified", codes[0]
    elif ins:
        verdict, primary = "Insufficient data", ins[0]
    elif opens:
        verdict, primary = "Possible match", opens[0]
    else:
        verdict, primary = "Qualified", "QUALIFIED"
    all_codes = codes + ins + (opens if not codes and not ins else [])

    # --- account strength --------------------------------------------------
    us = C.clean(c.get("us_company")).lower() == "yes"
    if any(x in ABSOLUTE or x in COMPANY_CODES for x in codes) or "INS_NO_COMPANY" in ins:
        strength = "None"
    elif status == "verified_under" and (emp or 0) >= 11 and us and (roles >= 3 or (roles >= 1 and fresh_signals)):
        strength = "Strong"
    elif status in ("verified_under", "likely_under") and us and (roles >= 1 or fresh_signals):
        strength = "Medium"
    else:
        strength = "Weak"
    downgrades = [x for x in re.split(r"[;,\s]+", c.get("strength_downgrade", "")) if x in ALLOWED_DOWNGRADES]
    if parent_over(c):
        downgrades.append("PARENT_UNCLEAR")  # a big parent may run the buying: an open item, never a Drop
    if downgrades and strength in ("Strong", "Medium"):
        strength = {"Strong": "Medium", "Medium": "Weak"}[strength]

    # --- missing account evidence (never a reason to Drop) ---------------------
    gaps = []
    if key and tri_code != "UNIDENTIFIABLE":
        if not need_found and hstatus == "Not checked":
            gaps.append("GAP_HIRING_NOT_CHECKED")
        elif not need_found and hstatus == "Unknown":
            gaps.append("GAP_HIRING_UNREAD")
        if status in ("unknown", "straddles"):
            gaps.append("INS_SIZE_UNKNOWN")
        if C.clean(c.get("us_company")).lower() not in ("yes", "no"):
            gaps.append("INS_US_UNKNOWN")

    # --- CRM -----------------------------------------------------------------
    state = crm_state(cc, ct)
    company_owner = owner_text((cc or {}).get("owner_name"), (cc or {}).get("owner_active"))
    contact_owner = owner_text((ct or {}).get("contact_owner"), (ct or {}).get("contact_owner_active"))
    routing = ""
    if state in ("open_deal", "customer") and cc and C.clean(cc.get("owner_name")) and C.yes(cc.get("owner_active")):
        routing = C.clean(cc.get("owner_name"))  # the account's owner holds the relationship
    elif state != "possible_match":
        if ct and C.clean(ct.get("contact_owner")) and C.yes(ct.get("contact_owner_active")):
            routing = C.clean(ct.get("contact_owner"))
        elif cc and C.clean(cc.get("owner_name")) and C.yes(cc.get("owner_active")):
            routing = C.clean(cc.get("owner_name"))
    hs_owner = "; ".join(x for x in ((f"Contact: {contact_owner}" if contact_owner else ""),
                                     (f"Company: {company_owner}" if company_owner else "")) if x) or "none"

    # --- action ------------------------------------------------------------
    only_person_level = all(x in PERSON_CODES for x in codes) and \
        all(x in ("INS_NO_PERSON", "INS_NO_TITLE") for x in ins)
    soft_only = all(x in SOFT_PERSON_CODES for x in codes) and "INS_NO_COMPANY" not in ins
    gap_action = False
    if any(x in ABSOLUTE for x in codes):
        action = "Drop"
    elif state in ("open_deal", "customer") and verdict in ("Qualified", "Possible match"):
        action = "Tell account owner"
    elif state in ("open_deal", "customer") and verdict in ("Not qualified", "Insufficient data") and soft_only:
        # someone at a live deal or a customer showed up: the owner should hear about it
        action = "Tell account owner"
    elif verdict == "Qualified":
        action = "Contact now"
    elif verdict in ("Not qualified", "Insufficient data") and strength in ("Strong", "Medium") and \
            state not in ("open_deal", "customer") and only_person_level:
        action = "Account play"
    elif verdict == "Possible match":
        action = "Review"
    elif verdict in ("Not qualified", "Insufficient data") and soft_only and gaps and \
            state not in ("open_deal", "customer"):
        # the account was never fully assessed: park or review it, never Drop it
        gap_action = True
        rest_strong = all(g in GAP_CODES for g in gaps) and us and status == "verified_under"
        action = "Review" if rest_strong else "Low priority"
    elif verdict == "Insufficient data":
        action = "Low priority"
    else:
        action = "Drop"
    if gap_action:
        all_codes += [g for g in gaps if g not in all_codes]

    # --- text ----------------------------------------------------------------
    name = canon["full_name"] if person else ""
    company = C.clean(c.get("company_name_verified")) or canon["company_name_raw"] or "(unidentified)"
    # reason text uses the number, never the worker's free text ("about Knock unit small")
    emp_text = f"{emp:,}" if emp is not None else "no figure"
    if (tech_us or 0) >= 1:
        need_text = f"{tech_us} open US tech role" + ("s" if tech_us != 1 else "")
    elif roles >= 1:
        need_text = f"{roles} open tech role" + ("s" if roles != 1 else "") + ", all outside the US"
    else:
        need_text = clip(f"{fresh_signals[0]['ym']} {fresh_signals[0]['text']}", 60) if fresh_signals else "no need found"
    vals = {"company": company, "name": name or "this person", "title": title or "no title",
            "employees_text": emp_text, "employees_source": c.get("employees_source") or "source not named",
            "parent_name": c.get("parent_name") or "the parent company",
            "parent_employees": fmt_int(c.get("parent_employees")) or "an unknown number of",
            "no_need_why": c.get("no_need_why") or c.get("_triage_why") or "no need found",
            "works_there_source": pf.get("works_there_source") or "research",
            "email_status": estatus, "need_text": need_text,
            "size_note": f"estimate {emp_text}" if emp is not None else "no figure",
            "email_phrase": EMAIL_PHRASE.get(estatus, "work email")}
    templates = C.reason_codes()
    if verdict in ("Not qualified", "Qualified"):
        why = fit(templates[primary]["template"], vals)
        clause = ""
        if primary in ("UNRELATED_TITLE", "EXCLUDED_TITLE") and pf.get("buyer_role_why"):
            clause = pf["buyer_role_why"]
        elif primary == "COMPETITOR_STAFFING" and c.get("sells_why"):
            clause = c["sells_why"]
        elif primary in ("CANNOT_BUY", "CONSUMER_SELF_EMPLOYED", "PUBLIC_BODY_NON_BUYER", "NOT_US") and c.get("_triage_why"):
            clause = c["_triage_why"]
        if clause:
            cand = f"{why} {clause[0].upper()}{clause[1:].rstrip('.')}."
            why = cand if len(cand) <= 160 else why
    else:
        items = (ins if verdict == "Insufficient data" else opens)
        why = fit(templates[items[0]]["template"], vals)
        if len(items) > 1 and not gap_action:
            cand = why + " " + fit(templates[items[1]]["template"], vals)
            why = cand if len(cand) <= 160 else why
    if gap_action:
        gap_text = "Account open item: " + fit(templates[gaps[0]]["template"], vals)
        base = fit(templates[primary]["template"], vals)
        why = next((w for w in (f"{why} {gap_text}", f"{base} {gap_text}") if len(w) <= 160), base)
    why = C.truncate(why, 160)

    committee = facts["committees"].get(final_key, [])
    named = []
    if action == "Contact now":
        buyer = name
    elif action == "Account play":
        named = [f"{m['full_name']} ({m['title']})" for m in committee
                 if m.get("full_name") and m.get("lead_id") != lid and
                 C.clean(m.get("works_there")).lower() != "no"][:2]
        buyer = "; ".join(named) if named else (C.clean(c.get("known_buyer")) or
                                                 FIT_ROLES.get(c.get("service_fit", ""), FIT_ROLES[""]))
        if strength in ("Strong", "Medium"):
            cand = f"{why} {strength} account: {need_text}."
            why = cand if len(cand) <= 160 else why
    else:
        buyer = ""

    if action == "Contact now":
        nxt = f"Contact {name} this week" + (f"; owner {routing}" if routing else "") + "."
    elif action == "Tell account owner":
        fact = C.clean((cc or {}).get("open_deal_summary")) if state == "open_deal" else \
            f"existing customer, {C.to_int((cc or {}).get('closed_won_24m_count')) or 0} closed-won deals in 24 months"
        who = C.clean((cc or {}).get("owner_name")) or C.clean((ct or {}).get("contact_owner")) or "the account team"
        extra = f" (contact owner {C.clean(ct.get('contact_owner'))})" if ct and C.clean(ct.get("contact_owner")) and \
            C.clean(ct.get("contact_owner")) != who else ""
        nxt = f"Tell {who}{extra}: {fact or 'open deal'}. Don't prospect separately."
    elif action == "Account play":
        nxt = f"Reach {' or '.join(named) if named else buyer}"
        if state in ("owned_inactive", "unowned", "possible_match"):
            nxt += "; claim or reassign the HubSpot record first"
        elif state == "owned_active" and routing:
            nxt += f"; loop in owner {routing}"
        nxt += "."
    elif gap_action:
        what = " and ".join(dict.fromkeys(GAP_SHORT[g] for g in gaps))
        nxt = (f"Check {what} at {company} before deciding on an account play." if action == "Review"
               else f"Park; confirm {what} at {company} before deciding on an account play.")
    elif action == "Review":
        nxt = f"Check {OPEN_SHORT[opens[0]].format(name=name or 'them')} before outreach."
    elif action == "Low priority":
        nxt = "Park; no company to research." if primary == "INS_NO_COMPANY" else \
            f"Park; revisit if {company} posts tech roles."
    else:
        nxt = "Do not contact. Suppress everywhere." if primary == "COMPLIANCE_DNC" else "No outreach."
    nxt = C.truncate(nxt, 160)

    # confidence
    a = c.get("size_tier", "").upper() in ("A", "B")
    b = C.clean(pf.get("works_there")).lower() == "confirmed" or estatus in C.QUALIFYING_EMAIL
    hc = c.get("hiring_checked") in BOARD_SOURCES
    if codes and (codes[0] in NO_RESEARCH_CODES or codes[0] in p1codes):
        conf = "High"
    elif person:
        n = sum((a, b, hc))
        conf = "High" if n == 3 else "Medium" if n == 2 else "Low"
    else:
        n = sum((a, hc))
        conf = "High" if n == 2 else "Medium" if n == 1 else "Low"

    if action == "Drop":
        suggested = ""
    elif routing:
        suggested = routing
    else:
        seg = SEGMENT_OWNERS.get(c.get("segment", ""))
        suggested = DEFAULT_OWNER + (f" (segment owner {seg})" if seg and seg != DEFAULT_OWNER else "")

    basis = {"observed": " (seen by scraper)", "post_date": " (post date)",
             "list_added": " (date added)"}.get(canon["touch_date_basis"], "")
    st = canon["source_type"]
    src_label = SOURCE_LABEL.get(st) or (f"Campaign list: {run.get('campaign') or canon['source_detail']}"
                                         if st == "campaign_list" else f"List: {canon['source_file']}")
    open_disp = ""
    if tech_us is not None and c.get("hiring_checked") == "hirebase":
        open_disp = f"{tech_us}+ (Hirebase, may undercount)"
    elif c.get("hiring_checked") == "hirebase":
        open_disp = "Hirebase: no match"
    elif tech_us is not None:
        open_disp = str(tech_us)
    if roles > (tech_us or 0):
        open_disp = f"{tech_us or 0} ({roles - (tech_us or 0)} outside the US)"
    watch = []
    if offshore_only:
        where = C.clean(c.get("tech_role_locations"))
        watch.append("Open tech roles are all outside the US" + (f" ({where})" if where else "") +
                     ". Fit may be embedded global talent rather than US direct hire.")
    examples = "; ".join([x.strip() for x in c.get("hiring_examples", "").split(";") if x.strip()][:3])
    sig_disp = "; ".join(f"{s['ym']} {s['text']}" for s in fresh_signals[:2])  # stale ones are context only
    website = final_key if final_key and not final_key.startswith("name:") else ""

    return {
        "lead_id": lid, "action": action, "verdict": verdict, "account_strength": strength,
        "primary_code": primary, "reason_codes": ";".join(all_codes), "why": why, "next_step": nxt,
        "watch_outs": C.truncate(" ".join(watch), 160),
        "name": name or "(company only)", "title": title, "title_group": group,
        "company": company, "company_key_final": final_key, "website": website,
        "what_they_do": C.truncate(c.get("what_they_do", ""), 160),
        "employees_text": C.clean(c.get("employees_text")) or (f"{emp:,}" if emp is not None else ""),
        "employees_best": "" if emp is None else str(emp), "size_band": band, "size_status": status,
        "size_tier": c.get("size_tier", ""), "headcount_source": c.get("employees_source", ""),
        "us_company": C.clean(c.get("us_company")).lower() or "unknown",
        "hiring_status": hstatus, "open_tech_roles_display": open_disp,
        "open_tech_roles_us": "" if tech_us is None else str(tech_us), "example_roles": examples,
        "need_signals_display": C.truncate(sig_disp, 160), "service_fit": c.get("service_fit", ""),
        "source_label": src_label, "what_they_did": p1["intent_phrase"],
        "touch_date": canon["touch_date"], "touch_date_display": (canon["touch_date"] + basis) if canon["touch_date"] else "",
        "touch_type": canon["touch_type"], "intent": p1["intent_level"], "crm_state": state,
        "crm_status": crm_status_plain(state, cc, ct, person), "hubspot_owner": hs_owner,
        "routing_owner": routing, "suggested_owner": suggested, "buyer_to_target": C.truncate(buyer, 160),
        "email": email if person else "", "email_status": estatus, "email_source": src if person else "",
        "linkedin": canon["linkedin_url"], "confidence": conf, "city": canon["city"], "state": canon["state"],
        "sources": "; ".join([s.strip() for s in re.split(r"[;\s]+", c.get("sources", "")) if s.strip()][:3]),
        "is_company_only": canon["is_company_only"], "segment": c.get("segment", ""),
        "label_warnings": "; ".join(dict.fromkeys(warn)),
        # sort helpers (not written)
        "_roles": roles, "_fresh_days": min([(months_ago(s["ym"], as_of) or 0) * 30 for s in fresh_signals] or [9999]),
        "_researched": researched, "_key_note": canon.get("key_note", ""),
    }

# ---------------------------------------------------------------------------
# Sorting, rollup, tier 1
# ---------------------------------------------------------------------------

def roles_bucket(n):
    n = n or 0
    return 0 if n >= 11 else 1 if n >= 6 else 2 if n >= 3 else 3 if n >= 1 else 4


CRM_CLEAN = {"not_found": 0, "unowned": 0, "owned_inactive": 1, "possible_match": 2, "owned_active": 3}


def touch_ord(d):
    dd = C.parse_date(d)
    return -dd.toordinal() if dd else 0


def company_tuple(strength, roles, intent, fresh_days, state, newest, key):
    return (C.STRENGTH_RANK.get(strength, 3), roles_bucket(roles), C.INTENT_RANK.get(intent, 3),
            fresh_days, CRM_CLEAN.get(state, 4), touch_ord(newest), key)


def sort_rows(rows):
    best_intent = {}
    for r in rows:
        k = r["company_key_final"] or r["lead_id"]
        best_intent[k] = min(best_intent.get(k, 3), C.INTENT_RANK.get(r["intent"], 3))
    inv = {v: k for k, v in C.INTENT_RANK.items() if k}

    def key(r):
        k = r["company_key_final"] or r["lead_id"]
        # within an Action, strength comes before Verdict so Rank agrees with the Tier 1 order
        t = company_tuple(r["account_strength"], r["_roles"], inv[best_intent[k]], r["_fresh_days"],
                          r["crm_state"], r["touch_date"], k)
        return (C.ACTION_RANK[r["action"]], t[0], C.VERDICT_RANK[r["verdict"]]) + t[1:] + (r["lead_id"],)
    rows.sort(key=key)
    for i, r in enumerate(rows, start=1):
        r["rank"] = str(i)
    return rows


def rollup(rows, facts):
    groups = defaultdict(list)
    for r in rows:
        if r["company_key_final"]:
            groups[r["company_key_final"]].append(r)
    out = []
    for k in sorted(groups):
        g = sorted(groups[k], key=lambda r: int(r["rank"]))
        lead = g[0]
        counts = defaultdict(int)
        for r in g:
            counts[r["action"]] += 1
        strength = min((r["account_strength"] for r in g), key=lambda s: C.STRENGTH_RANK.get(s, 3))
        names = {C.norm_company_name(r["company"]) for r in g}
        coll = []
        dom = k if not k.startswith("name:") else ""
        for p in facts["prior"]:
            if p["name_norm"] in names and dom and p["domain"] != dom:
                coll.append(f"{p['domain']} ({p['source_file']})")
        notes = sorted({r["_key_note"] for r in g if r.get("_key_note")})  # from normalize: shared or split domains
        resolved = next((facts["companies"][ck].get("collision_resolved", "") for ck in facts["companies"]
                         if facts["companies"][ck].get("company_key_final") == k and
                         facts["companies"][ck].get("collision_resolved")), "")
        out.append({
            "company_key_final": k, "company_name": lead["company"],
            "best_action": lead["action"], "best_verdict": min((r["verdict"] for r in g), key=lambda v: C.VERDICT_RANK[v]),
            "account_strength": strength, "rows": len(g),
            "n_contact_now": counts["Contact now"], "n_tell_owner": counts["Tell account owner"],
            "n_account_play": counts["Account play"], "n_review": counts["Review"],
            "n_low": counts["Low priority"], "n_drop": counts["Drop"],
            "lead_row_id": lead["lead_id"], "lead_ids": ";".join(r["lead_id"] for r in g),
            "crm_state": lead["crm_state"], "open_tech_roles_us": lead["open_tech_roles_us"],
            "tech_roles_all": max(r["_roles"] for r in g),
            "best_intent": min((r["intent"] for r in g), key=lambda i: C.INTENT_RANK.get(i, 3)),
            "freshest_need_days": min(r["_fresh_days"] for r in g),
            "newest_touch": max((r["touch_date"] for r in g), default=""),
            "collision": "; ".join(([("prior runs used " + "; ".join(sorted(set(coll))))] if coll else []) + notes),
            "collision_resolved": resolved,
        })
    return out


# Planning estimate per enriched company, set so the default caps fit a full Tier 1 of 8
# exactly (8 x 1.25 = 10 Deepline credits, 8 x 7.5 = 60 MoltSets tokens). Observed spend:
# Deepline 5.70 for 5 accounts on 2026-09-25 (1.14 each), 1.24 for Pulley on 2026-09-27,
# 1.18 for 2 companies in the 2026-09-28 test run; MoltSets 4 tokens for 2 companies in the
# test run (Pulley's 21 included committee search, which now goes to Deepline's free search first).
PLAN_PER_COMPANY = {"moltsets": 7.5, "deepline": 1.25}
TIER1_CEILING = 8  # JK's hard limit on Tier 1 size


def select_tier1(roll, max_total=8, max_plays=5, caps=None):
    max_plays = min(max_plays, max_total)
    cn = [c for c in roll if c["best_action"] == "Contact now"]
    plays = [c for c in roll if c["best_action"] == "Account play"]
    # all tech roles count as demand, US or not (JK 2026-09-28)
    plays.sort(key=lambda c: company_tuple(c["account_strength"], C.to_int(c["tech_roles_all"]) or 0,
                                           c["best_intent"], c["freshest_need_days"], c["crm_state"],
                                           c["newest_touch"], c["company_key_final"]))
    n_plays = min(max_plays, max(0, max_total - len(cn)))
    out = []
    for c in sorted(cn, key=lambda c: c["company_key_final"]):
        out.append(dict(c, tier1_reason="Contact now"))
    for i, c in enumerate(plays[:n_plays], start=1):
        out.append(dict(c, tier1_reason=f"Top account play {i}"))
    # scale the per-company projection so the whole Tier 1 fits the run's caps
    caps = caps or C.DEFAULT_CAPS
    n = max(1, len(out))
    short = []  # a scaled-down projection means the plan does not fit: say so, never hide it
    for v in ("moltsets", "deepline"):
        cap = float((caps.get(v) or [PLAN_PER_COMPANY[v]])[0])
        if out and cap / n < PLAN_PER_COMPANY[v]:
            short.append(f"{v}: {cap:g} cap over {n} companies is {cap / n:.2f} each, "
                         f"below the {PLAN_PER_COMPANY[v]:g} plan per company")
    for c in out:
        for v in ("moltsets", "deepline"):
            cap = float((caps.get(v) or [PLAN_PER_COMPANY[v]])[0])
            c[f"projected_{v}"] = f"{min(PLAN_PER_COMPANY[v], cap / n):.2f}"
        c["packet_file"] = C.packet_name(c["company_name"])
    return out, len(cn) > max_total, short


def run_label(run_dir, out_dir=None, freeze=False, quiet=None, tier1_max=None):
    out_dir = out_dir or C.work(run_dir)
    if quiet is None:
        quiet = out_dir != C.work(run_dir)
    run = C.load_run(run_dir)
    as_of = C.parse_date(run.get("as_of"))
    if as_of is None:
        sys.exit("work/run.json has no as_of date; rerun normalize.py (with --as-of for a fixed date)")
    if tier1_max is not None and not 1 <= tier1_max <= TIER1_CEILING:
        sys.exit(f"--tier1-max must be 1 to {TIER1_CEILING} (JK's hard limit is {TIER1_CEILING} companies)")
    if tier1_max is not None and out_dir == C.work(run_dir):
        run["tier1_max"] = tier1_max
        C.save_run(run_dir, run)
    tier1_max = int(run.get("tier1_max") or 8)
    canon = C.read_csv(C.work(run_dir, "01-canonical.csv"))
    p1 = {r["lead_id"]: r for r in C.read_csv(C.work(run_dir, "02-pass1.csv"))}
    if not canon or len(p1) != len(canon):
        sys.exit("canonical and pass1 rows differ; rerun classify.py")
    facts = load_facts(run_dir)
    apply_overrides(facts)
    rows = [label_row(r, p1[r["lead_id"]], facts, as_of, run) for r in canon]
    sort_rows(rows)
    roll = rollup(rows, facts)
    tier1, over, budget_short = select_tier1(roll, max_total=min(tier1_max, TIER1_CEILING), caps=run.get("caps"))
    if out_dir == C.work(run_dir) and run.get("budget_short") != budget_short:
        run["budget_short"] = budget_short  # ledger.py check repeats this warning
        C.save_run(run_dir, run)

    prev = {r["lead_id"]: r for r in C.read_csv(os.path.join(out_dir, "05-qualified.csv"))}
    changes = []
    for r in rows:
        p = prev.get(r["lead_id"])
        if p:
            for f in ("action", "verdict", "account_strength", "primary_code", "email_status"):
                if p.get(f) != r[f]:
                    changes.append({"lead_id": r["lead_id"], "field": f, "old": p.get(f), "new": r[f]})

    C.write_csv(os.path.join(out_dir, "05-qualified.csv"), rows, QUALIFIED_FIELDS)
    C.write_csv(os.path.join(out_dir, "05-company-rollup.csv"), roll, ROLLUP_FIELDS)
    C.write_csv(os.path.join(out_dir, "05-changes.csv"), changes, ["lead_id", "field", "old", "new"])
    frozen = run.get("tier1_frozen") and os.path.exists(os.path.join(out_dir, "06-tier1.csv"))
    tier_name = "06-tier1-candidates.csv" if frozen else "06-tier1.csv"
    C.write_csv(os.path.join(out_dir, tier_name), tier1, TIER1_FIELDS)
    if freeze and out_dir == C.work(run_dir):
        run["tier1_frozen"] = True
        C.save_run(run_dir, run)

    if out_dir == C.work(run_dir):
        acts = defaultdict(int)
        for r in rows:
            acts[r["action"]] += 1
        C.append_log(run_dir, "S4/S7 label rows={} {} tier1={} warnings={} changes={}".format(
            len(rows), " ".join(f"{a.replace(' ', '_')}={acts[a]}" for a in C.ACTIONS),
            len(tier1), sum(bool(r["label_warnings"]) for r in rows) + len(facts["warnings"]), len(changes)))
    if quiet:
        return rows, roll, tier1
    for w in facts["warnings"]:
        print("warning:", w)
    for r in rows:
        if r["label_warnings"]:
            print(f"warning: {r['lead_id']}: {r['label_warnings']}")
    for s in budget_short:
        print(f"WARNING: Tier 1 budget below plan ({s}). Cut the Tier 1 size, skip companies, "
              "or ask JK to raise the cap.")
    if over:
        print(f"STOP AND ASK JK: more than {tier1_max} Contact now companies; ask which to enrich.")
    return rows, roll, tier1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--freeze-tier1", action="store_true")
    ap.add_argument("--tier1-max", type=int, default=None,
                    help="Tier 1 size (default 8; saved in run.json); account plays fill up to it, 5 at most")
    args = ap.parse_args(argv)
    rows, roll, tier1 = run_label(args.run, args.out_dir or None, args.freeze_tier1, tier1_max=args.tier1_max)
    acts = defaultdict(int)
    for r in rows:
        acts[(r["action"], r["verdict"])] += 1
    print(f"labeled {len(rows)} rows, {len(roll)} companies, tier 1 = {len(tier1)}")
    for (a, v), n in sorted(acts.items(), key=lambda x: (C.ACTION_RANK[x[0][0]], C.VERDICT_RANK[x[0][1]])):
        print(f"  {a:18s} {v:18s} {n}")
    for t in tier1:
        print(f"  tier1: {t['company_key_final']} ({t['tier1_reason']})")


if __name__ == "__main__":
    main()
