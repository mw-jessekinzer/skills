#!/usr/bin/env python3
"""Quality gates 1 to 8 (references/quality-gates.md). Exit 1 if any gate fails.

  checks.py all --run RUN_DIR          every gate, for the final hand-off
  checks.py gate --run RUN_DIR --stage S2 1 2   mid-run: gate 1 checks only what exists by S2
                                                (stages S2, S3, S4, S6, S8, S9)
  checks.py lint FILE [FILE ...]       dash, banned-word, and trope lint for any md or csv

Gates:
  1 counts reconcile by key at every hand-off
  2 controlled vocabulary, company size, and cannot-buy guardrails
  3 dash, banned-word, jargon, trope, and cell-length lint
  4 domain match for committee and import emails; collisions resolved
  5 CRM facts applied (status text, owner, HubSpot email)
  6 no intent overstatement; "verified" only with a qualifying email
  7 determinism (label.py twice, identical) and freshness
  8 budget caps and no CRM or Baserow writes
"""
import argparse
import filecmp
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import label as L  # noqa: E402
import assemble as A  # noqa: E402


class Gate:
    def __init__(self, n, name):
        self.n, self.name, self.fails, self.warns = n, name, [], []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def report(self):
        status = "FAIL" if self.fails else ("WARN" if self.warns else "PASS")
        print(f"[{status}] gate {self.n}: {self.name}")
        for m in self.fails[:15]:
            print(f"    fail: {m}")
        if len(self.fails) > 15:
            print(f"    ... {len(self.fails) - 15} more")
        for m in self.warns[:10]:
            print(f"    warn: {m}")
        if len(self.warns) > 10:
            print(f"    ... {len(self.warns) - 10} more warnings")
        return not self.fails


def final_csv(run_dir):
    run = C.load_run(run_dir)
    fp, ip = A.paths(run_dir, run)
    return C.read_csv(fp), C.read_csv(ip), fp, ip


def md_files(run_dir):
    out = []
    s = os.path.join(run_dir, "00 - Summary.md")
    if os.path.exists(s):
        out.append(s)
    pd = os.path.join(run_dir, "Packets")
    if os.path.isdir(pd):
        out += sorted(os.path.join(pd, f) for f in os.listdir(pd) if f.endswith(".md"))
    return out

# ---------------------------------------------------------------------------


STAGES = ["S2", "S3", "S4", "S6", "S8", "S9"]


def reached(stage, s):
    return STAGES.index(stage) >= STAGES.index(s)


def gate1(run_dir, stage="S9"):
    """Only checks what should exist by `stage`: batches at S2, CRM at S3, labels at S4,
    enrichment at S6, the final CSV at S8. `checks.py all` checks everything."""
    g = Gate(1, f"counts reconcile by key (through {stage})")
    run = C.load_run(run_dir)
    canon = C.read_csv(C.work(run_dir, "01-canonical.csv"))
    ids = [r["lead_id"] for r in canon]
    cset = set(ids)
    if len(ids) != len(cset):
        g.fail("duplicate lead_id in 01-canonical.csv")
    dupes = [d for d in C.read_csv(C.work(run_dir, "01-dupes.csv")) if d["merge_key"] != "repeat of the same record id"]
    if run.get("source_rows_in_window") is not None and run["source_rows_in_window"] != len(canon) + len(dupes):
        g.fail(f"source rows {run['source_rows_in_window']} != canonical {len(canon)} + merged {len(dupes)}")
    p1 = C.read_csv(C.work(run_dir, "02-pass1.csv"))
    if {r["lead_id"] for r in p1} != cset:
        g.fail("02-pass1.csv lead ids differ from canonical")
    comps = C.read_csv(C.work(run_dir, "02-companies.csv"))
    if {r["company_key"] for r in p1 if r["company_key"]} != {c["company_key"] for c in comps}:
        g.fail("company keys in pass1 differ from 02-companies.csv")
    by_key = {}
    for r in p1:
        by_key.setdefault(r["company_key"], []).append(r)

    research_keys = set()
    for bpath in C.glob_work(run_dir, "02-batch-"):
        name = os.path.basename(bpath)[len("02-batch-"):-4]
        bkeys = {r["company_key"] for r in C.read_csv(bpath)}
        if name.startswith("triage"):
            out = C.work(run_dir, f"03-triage-{name}.csv")
            if not os.path.exists(out):
                g.fail(f"no output for batch {name} (expected {os.path.basename(out)})")
                continue
            okeys = {r["company_key"] for r in C.read_csv(out)}
        else:
            out = C.work(run_dir, f"03-research-companies-{name}.csv")
            if not os.path.exists(out):
                g.fail(f"no output for batch {name} (expected {os.path.basename(out)})")
                continue
            okeys = {r["company_key"] for r in C.read_csv(out)}
            research_keys |= okeys
            ppath = C.work(run_dir, f"03-research-people-{name}.csv")
            pids = {r["lead_id"] for r in C.read_csv(ppath)}
            need = {r["lead_id"] for k in bkeys for r in by_key.get(k, [])
                    if r["is_company_only"] == "no" and r["research_priority"] != "X"}
            if need - pids:
                g.fail(f"batch {name}: {len(need - pids)} researched-company people missing from "
                       f"{os.path.basename(ppath)}: {sorted(need - pids)[:5]}")
        if bkeys - okeys:
            g.fail(f"batch {name}: companies in but not out: {sorted(bkeys - okeys)[:8]}")
        if okeys - bkeys:
            g.warn(f"batch {name}: extra companies out: {sorted(okeys - bkeys)[:8]}")
    research_keys |= {r["company_key"] for r in C.read_many(C.glob_work(run_dir, "03-research-companies-"))}
    for t in C.read_many(C.glob_work(run_dir, "03-triage-")):
        if C.clean(t.get("triage")).lower() == "keep" and t["company_key"] not in research_keys:
            g.fail(f"triage Keep {t['company_key']} was never deep-researched (run classify.py keeps)")

    if not reached(stage, "S3"):
        return g
    q = C.read_csv(C.work(run_dir, "05-qualified.csv"))
    if q:
        if {r["lead_id"] for r in q} != cset:
            g.fail("05-qualified.csv lead ids differ from canonical")
        acts = sum(1 for r in q if r["action"] in C.ACTIONS)
        if acts != len(q):
            g.fail("Action counts do not sum to rows")
        # CRM coverage: every company that got deep research without a company-level code
        crm_c = {r["company_key_final"]: r for r in C.read_csv(C.work(run_dir, "04-crm-companies.csv"))}
        crm_p = {r["lead_id"]: r for r in C.read_csv(C.work(run_dir, "04-crm-contacts.csv"))}
        company_codes = set(L.ABSOLUTE) | set(L.COMPANY_CODES)
        research = {}
        for r in C.read_many(C.glob_work(run_dir, "03-research-companies-")):
            research[r.get("company_key_final") or r["company_key"]] = r
        for r in q:
            fk = r["company_key_final"]
            if fk in research and not (set(r["reason_codes"].split(";")) & company_codes):
                if fk not in crm_c or not C.yes(crm_c[fk].get("checked")):
                    g.fail(f"CRM not checked for company {fk}")
                if r["is_company_only"] == "no" and (r["lead_id"] not in crm_p or not C.yes(crm_p[r["lead_id"]].get("checked"))):
                    g.fail(f"CRM contact not checked for {r['lead_id']} ({r['name']})")
        g.fails = list(dict.fromkeys(g.fails))
    else:
        g.fail("no 05-qualified.csv yet (run label.py before the CRM stage)")

    if reached(stage, "S8"):
        final, _, fp, _ = final_csv(run_dir)
        if final and {r["Lead ID"] for r in final} != cset:
            g.fail(f"{os.path.basename(fp)} lead ids differ from canonical")
        elif not final:
            g.fail("final CSV not written yet (assemble.py)")

    if not reached(stage, "S6"):
        return g
    tier1 = C.read_csv(C.work(run_dir, "06-tier1.csv"))
    cap = int(run.get("tier1_max") or 8)
    if len(tier1) > cap:
        g.fail(f"Tier 1 has {len(tier1)} companies (cap {cap})")
    committees = {C.clean(r.get("company_key_final")) for r in C.read_many(C.glob_work(run_dir, "07-committee-"))}
    pd = os.path.join(run_dir, "Packets")
    packets = set(os.listdir(pd)) if os.path.isdir(pd) else set()
    skipped = A.enrich_skipped(run_dir)
    for t in tier1:
        if t["company_key_final"] in skipped:  # an explicit, reported state, not a failure
            g.warn(f"Tier 1 {t['company_name']}: enrichment skipped ({skipped[t['company_key_final']]})")
            continue
        if t["company_key_final"] not in committees:
            g.fail(f"Tier 1 {t['company_key_final']} has no 07-committee file")
        name = C.packet_name(t["company_name"])
        if name not in packets:
            g.fail(f"Tier 1 {t['company_name']} has no packet (Packets/{name})")
    return g


ENUMS = {
    "action": C.ACTIONS, "verdict": C.VERDICTS, "account_strength": C.STRENGTHS,
    "confidence": C.CONFIDENCE, "email_status": C.EMAIL_STATUSES, "hiring_status": C.HIRING_STATUSES,
    "size_band": C.SIZE_BANDS, "company_size": C.COMPANY_SIZES, "intent": C.INTENT_LEVELS, "title_group": C.TITLE_GROUPS,
    "crm_state": C.CRM_STATES,
}
FACT_ENUMS = {
    "size_tier": {"", "A", "B", "C"}, "us_company": {"", "yes", "no", "unknown"},
    "hiring_checked": {"", "ats_api", "careers_page", "linkedin_jobs", "hirebase", "search", "none_found",
                       "not_checked"},
    "service_fit": {"", "Recruiting", "Embedded", "Scoped", "None"},
    "sells_staffing_or_dev": {"", "yes", "no"}, "public_body": {"", "yes", "no"},
    "consumer_or_self": {"", "yes", "no"}, "structural_no_need": {"", "yes", "no"},
    "can_buy": {"", "yes", "no", "unknown"}, "parent_centralized": {"", "yes", "no", "unknown"},
    "research_depth": {"", "deep", "quick", "knowledge"},
    "segment": {"", "fintech", "banking_insurance_wealth", "faith", "proptech_construction",
                "cloud_infrastructure", "other"},
}
PERSON_ENUMS = {
    "works_there": {"", "confirmed", "likely", "unknown", "no"},
    "buyer_role": {"", "yes", "partial", "no", "unknown"},
    "vendor_selling": {"", "yes", "no"}, "job_seeker": {"", "yes", "no"},
    "domain_accept_all": {"", "yes", "no", "unknown"},
    "bounceban_result": {"", "deliverable", "undeliverable", "risky", "unknown"},
}


def gate2(run_dir):
    g = Gate(2, "controlled vocabulary and guardrails")
    codes = C.reason_codes()
    q = C.read_csv(C.work(run_dir, "05-qualified.csv"))
    as_of = C.parse_date(C.load_run(run_dir).get("as_of"))
    keys = {r["lead_id"]: r["company_key"] for r in C.read_csv(C.work(run_dir, "02-pass1.csv"))}
    facts = L.load_facts(run_dir)
    L.apply_overrides(facts)
    for r in q:
        for f, allowed in ENUMS.items():
            if r.get(f, "") not in allowed:
                g.fail(f"{r['lead_id']}: {f} '{r.get(f)}' not allowed")
        if r["service_fit"] not in FACT_ENUMS["service_fit"]:
            g.fail(f"{r['lead_id']}: service_fit '{r['service_fit']}' not allowed")
        for code in [x for x in r["reason_codes"].split(";") if x] + [r["primary_code"]]:
            if code not in codes:
                g.fail(f"{r['lead_id']}: unknown reason code {code}")
        emp = C.to_int(r["employees_best"])
        rc = r["reason_codes"].split(";")
        if "TINY_NO_BUDGET" in rc and not (r["size_tier"] in ("A", "B") and
                                           r["hiring_status"] in ("No open roles found", "Hiring, non-tech only")):
            g.fail(f"{r['lead_id']}: TINY_NO_BUDGET without a counted A/B headcount and a job list that was read")
        if "CANNOT_BUY" in rc and emp is not None and emp > 50:
            g.fail(f"{r['lead_id']}: CANNOT_BUY with {emp} employees")
        # size never drops or lowers a row (JK ruling 2026-10-12)
        if set(rc + [r["primary_code"]]) & (C.RETIRED_SIZE_CODES | {"OPEN_SIZE", "INS_SIZE_UNKNOWN"}):
            g.fail(f"{r['lead_id']}: row lowered for size ({r['reason_codes']}); size is a descriptive tier only")
        if r.get("company_size") == "Growth startup":
            c, _, _ = L.company_facts_for(keys.get(r["lead_id"], ""), facts) if keys.get(r["lead_id"]) else ({}, "", [])
            funded = [s for s in L.parse_signals(c.get("need_signals")) if s["type"] == "funding" and
                      L.months_ago(s["ym"], as_of) is not None and L.months_ago(s["ym"], as_of) <= C.STARTUP_FUNDING_MONTHS]
            if not funded or emp is None or emp >= C.MIDMARKET_MIN:
                g.fail(f"{r['lead_id']}: Growth startup without a funding signal in the last "
                       f"{C.STARTUP_FUNDING_MONTHS} months and a figure under {C.MIDMARKET_MIN:,}")
        hard = set(L.ABSOLUTE) | set(L.COMPANY_CODES) | (set(L.PERSON_CODES) - L.SOFT_PERSON_CODES) | {"INS_NO_COMPANY"}
        if r["action"] == "Drop" and not (set(rc) & hard):
            if r.get("company_size") == "Enterprise":
                g.fail(f"{r['lead_id']}: Enterprise row dropped without a hard disqualifier; size never drops a row")
            elif not (r["hiring_status"] in ("No open roles found", "Hiring, non-tech only") and
                      r["us_company"] in ("yes", "no")):
                g.fail(f"{r['lead_id']}: Drop on missing evidence (hiring {r['hiring_status']}, "
                       f"US {r['us_company']}); missing evidence must park the row, not drop it")
        if r["label_warnings"]:
            target = g.fail if "not yet deep-researched" in r["label_warnings"] else g.warn
            target(f"{r['lead_id']}: {r['label_warnings']}")
    for r in C.read_many(C.glob_work(run_dir, "03-research-companies-")):
        for f, allowed in FACT_ENUMS.items():
            if C.clean(r.get(f, "")) not in allowed:
                g.fail(f"research {r.get('company_key')}: {f} '{r.get(f)}' not allowed")
        for part in [p.strip() for p in (r.get("need_signals") or "").split(";") if p.strip()]:
            if not re.match(r"\d{4}-\d{2}(-\d{2})?\s+(funding|new_tech_leader|launch|acquisition|modernization|growth|contraction|ai_initiative):", part):
                g.fail(f"research {r.get('company_key')}: need signal not in 'YYYY-MM type: text' form: {part[:60]}")
    for r in C.read_many(C.glob_work(run_dir, "03-research-people-")):
        for f, allowed in PERSON_ENUMS.items():
            if C.clean(r.get(f, "")).lower() not in allowed:
                g.fail(f"people {r.get('lead_id')}: {f} '{r.get(f)}' not allowed")
    for r in C.read_many(C.glob_work(run_dir, "03-triage-")):
        if C.clean(r.get("triage")).lower() not in ("keep", "drop"):
            g.fail(f"triage {r.get('company_key')}: triage must be Keep or Drop")
        if C.clean(r.get("triage")).lower() == "drop":
            code = C.canonical_code(r.get("drop_code"))
            if code in C.RETIRED_SIZE_CODES:  # an old file still loads; label.py ignores the drop
                g.warn(f"triage {r.get('company_key')}: retired size drop '{r.get('drop_code')}' read as not a drop")
            elif code not in L.TRIAGE_CODES:
                g.fail(f"triage {r.get('company_key')}: drop_code '{r.get('drop_code')}' not allowed")
    for w in facts["warnings"]:
        (g.fail if "override" in w else g.warn)(w)
    return g


RAW_COLUMNS = {"Name", "Title", "Company", "City", "State", "Email", "LinkedIn", "Lead ID", "Website"}
LONG_OK = {"Sources", "Example open roles"}


def gate3(run_dir):
    g = Gate(3, "dash, banned-word, jargon, trope, and length lint")
    final, imp, fp, ip = final_csv(run_dir)
    for r in final:
        for col, val in r.items():
            if col in RAW_COLUMNS:
                if C.DASH_RE.search(val or ""):
                    g.fail(f"{r['Lead ID']} {col}: dash in source text (assemble should have cleaned it)")
                continue
            for p in C.lint_text(val, jargon=True):
                g.fail(f"{r['Lead ID']} {col}: {p}: {val[:80]}")
            limit = 300 if col in LONG_OK else 160
            if len(val or "") > limit:
                g.fail(f"{r['Lead ID']} {col}: {len(val)} chars (limit {limit})")
    for r in imp:
        for col, val in r.items():
            if C.DASH_RE.search(val or ""):
                g.fail(f"import {r.get('Email')} {col}: dash")
    for path in md_files(run_dir):
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                for p in C.lint_text(line):
                    g.fail(f"{os.path.relpath(path, run_dir)}:{i}: {p}")
    return g


def gate4(run_dir):
    g = Gate(4, "domain match and collisions")
    run = C.load_run(run_dir)
    ctx, facts = A.company_context(run_dir)
    members = A.committee_status(run_dir, C.parse_date(run.get("as_of")), ctx, facts)
    for m in members:
        if m["email"] and m["domain_ok"] != "yes":
            g.fail(f"committee {m['full_name']} ({m['company_key_final']}): email {m['email']} is not on the company's domains")
        if m["employer_domain_ok"] != "yes":
            g.fail(f"committee {m['full_name']} ({m['company_key_final']}): employer domain {m['employer_domain']} "
                   f"is a different company")
        if not m["employer_domain"] and m["works_there"] != "confirmed":
            g.warn(f"committee {m['full_name']}: no employer domain recorded and employment not confirmed")
    _, imp, _, _ = final_csv(run_dir)
    for r in imp:
        doms = ctx.get(r["Associate to company domain"], {}).get("domains", set())
        if C.email_domain(r["Email"]) not in doms:
            g.fail(f"import {r['Email']} not on {r['Associate to company domain']} domains")
    roll = C.read_csv(C.work(run_dir, "05-company-rollup.csv"))
    for c in roll:
        if c["collision"] and not c["collision_resolved"] and c["best_action"] != "Drop":
            g.fail(f"{c['company_key_final']}: name collision ({c['collision']}) has no collision_resolved override")
    pd = os.path.join(run_dir, "Packets")
    for c in roll:
        path = os.path.join(pd, C.packet_name(c["company_name"]))
        if not os.path.exists(path):
            continue
        status = {m["email"]: m["email_status"] for m in members
                  if m["company_key_final"] == c["company_key_final"] and m["email"]}
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if not line.lstrip().startswith("|") or "@" not in line:
                    continue
                cells = [x.strip() for x in line.strip().strip("|").split("|")]
                for e in re.findall(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)+", line):
                    e = e.lower()
                    if e not in status:
                        g.fail(f"Packets/{os.path.basename(path)}:{i}: {e} is not in the committee file")
                    elif status[e] not in cells:
                        g.fail(f"Packets/{os.path.basename(path)}:{i}: {e} should show email status '{status[e]}'")
    return g


def gate5(run_dir):
    g = Gate(5, "CRM facts applied")
    q = {r["lead_id"]: r for r in C.read_csv(C.work(run_dir, "05-qualified.csv"))}
    final, _, _, _ = final_csv(run_dir)
    fin = {r["Lead ID"]: r for r in final}
    facts = L.load_facts(run_dir)
    for lid, r in q.items():
        cc = facts["crm_companies"].get(r["company_key_final"])
        ct = facts["crm_contacts"].get(lid)
        if not cc and not ct:
            continue
        state = L.crm_state(cc, ct)
        expect = L.crm_status_plain(state, cc, ct, r["is_company_only"] == "no")
        f = fin.get(lid)
        if f is None:
            continue
        if f["CRM status"] != expect:
            g.fail(f"{lid}: CRM status '{f['CRM status'][:60]}' != HubSpot facts '{expect[:60]}'")
        hs_email = C.clean((ct or {}).get("email")).lower()
        if hs_email and not C.is_personal_domain(hs_email.rsplit("@", 1)[-1]) and r["email_status"] != "Wrong domain":
            if f["Email"] != hs_email or f["Email status"] != "From HubSpot":
                g.fail(f"{lid}: HubSpot email {hs_email} not applied (CSV shows {f['Email']}, {f['Email status']})")
    return g


VERIFIED_RE = re.compile(r"\bverified\b", re.I)


def gate6(run_dir):
    g = Gate(6, "no intent overstatement")
    p1 = {r["lead_id"]: r for r in C.read_csv(C.work(run_dir, "02-pass1.csv"))}
    canon = {r["lead_id"]: r for r in C.read_csv(C.work(run_dir, "01-canonical.csv"))}
    final, _, _, _ = final_csv(run_dir)
    for r in final:
        lid = r["Lead ID"]
        if lid not in p1:
            continue
        if r["What they did"] != p1[lid]["intent_phrase"]:
            g.fail(f"{lid}: 'What they did' differs from the template phrase")
        form = canon[lid]["touch_type"] in C.FORM_TOUCHES
        for col in ("What they did", "Why this verdict", "Next step"):
            m = C.INTENT_OVERSTATE_RE.search(r[col] or "")
            if m and not form:
                g.fail(f"{lid} {col}: '{m.group(0)}' but the touch was {canon[lid]['touch_type']}")
        if r["Email status"] not in C.QUALIFYING_EMAIL:
            for col in ("Why this verdict", "Next step", "Buyer to target"):
                if VERIFIED_RE.search(r[col] or ""):
                    g.fail(f"{lid} {col}: says 'verified' with email status {r['Email status']}")
    roll = C.read_csv(C.work(run_dir, "05-company-rollup.csv"))
    pd = os.path.join(run_dir, "Packets")
    for c in roll:
        path = os.path.join(pd, C.packet_name(c["company_name"]))
        if not os.path.exists(path):
            continue
        form = any(canon.get(lid, {}).get("touch_type") in C.FORM_TOUCHES for lid in c["lead_ids"].split(";"))
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = C.INTENT_OVERSTATE_RE.search(text)
        if m and not form:
            g.fail(f"Packets/{os.path.basename(path)}: '{m.group(0)}' but no form fill on record")
    return g


def gate7(run_dir):
    g = Gate(7, "determinism and freshness")
    names = ["05-qualified.csv", "05-company-rollup.csv"]
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        L.run_label(run_dir, a)
        L.run_label(run_dir, b)
        for n in names:
            if not filecmp.cmp(os.path.join(a, n), os.path.join(b, n), shallow=False):
                g.fail(f"label.py gave different {n} on two runs")
        live = C.work(run_dir, "05-qualified.csv")
        if os.path.exists(live) and not filecmp.cmp(os.path.join(a, names[0]), live, shallow=False):
            g.fail("work/05-qualified.csv is stale: facts changed since the last label.py run; rerun label.py and assemble.py")
    return g


WRITE_PATTERNS = [
    r"baserow\.sh\s+(create|update|batch-create|batch-update|delete)",
    r"\bmanage_[a-z_]+", r"\b(create|update|delete|batch)_(crm|contact|company|deal|object)s?\b",
    r"deepline\s+tools\s+execute\s+hubspot", r"\bhubspot_(create|update|upsert)",
]


def gate8(run_dir):
    g = Gate(8, "budget caps and no writes")
    run = C.load_run(run_dir)
    caps = run.get("caps") or C.DEFAULT_CAPS
    spent = {}
    rows = C.read_csv(os.path.join(run_dir, "cost-ledger.csv"))
    for r in rows:
        spent[r["vendor"]] = spent.get(r["vendor"], 0.0) + float(r["charged"] or 0)
    for v, (cap, unit) in caps.items():
        if spent.get(v, 0.0) > cap + 1e-9:
            g.fail(f"{v}: spent {spent[v]:g} over cap {cap:g} {unit}s")
    import ledger  # noqa: E402
    for v, x in ledger.summarize(run_dir).items():
        if x["reconcile"] and x["reconcile"] != "balances reconcile":
            g.warn(f"{v}: {x['reconcile']}")
        if x["calls"] and not x["reconcile"]:
            g.warn(f"{v}: no start/end balances recorded")
    texts = []
    log = C.work(run_dir, "00-run-log.md")
    if os.path.exists(log):
        with open(log, encoding="utf-8") as f:
            texts.append(("00-run-log.md", f.read()))
    texts.append(("cost-ledger.csv", "\n".join(" ".join(r.values()) for r in rows)))
    for name, t in texts:
        for p in WRITE_PATTERNS:
            m = re.search(p, t, re.I)
            if m:
                g.fail(f"{name}: write command found: '{m.group(0)}'")
    if os.path.exists(log) and "## Commands" not in texts[0][1]:
        g.warn("run log has no '## Commands' section listing vendor and CRM calls")
    return g


GATES = {1: gate1, 2: gate2, 3: gate3, 4: gate4, 5: gate5, 6: gate6, 7: gate7, 8: gate8}


def lint_files(paths):
    ok = True
    for p in paths:
        with open(p, encoding="utf-8-sig") as f:
            for i, line in enumerate(f, start=1):
                for prob in C.lint_text(line, jargon=p.endswith(".csv")):
                    ok = False
                    print(f"{p}:{i}: {prob}")
    print("lint clean" if ok else "lint found problems")
    return ok


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "lint":
        return 0 if lint_files(argv[1:]) else 1
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["all", "gate"])
    ap.add_argument("--run", required=True)
    ap.add_argument("--stage", choices=STAGES, default="S9",
                    help="gate 1 checks only what should exist by this stage (default: everything)")
    ap.add_argument("gates", nargs="*", type=int)
    a = ap.parse_args(argv)
    todo = sorted(GATES) if a.mode == "all" else a.gates
    ok = True
    for n in todo:
        g = GATES[n](a.run, a.stage) if n == 1 else GATES[n](a.run)
        ok = g.report() and ok
    print("ALL GATES PASS" if ok else "GATES FAILED: fix facts in work/overrides.csv, rerun label.py and assemble.py")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
