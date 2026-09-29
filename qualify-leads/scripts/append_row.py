#!/usr/bin/env python3
"""Append one schema-checked row to a work file. Workers use this so every file
has the exact header the scripts expect and a crash never loses finished rows.

  append_row.py company  FILE --json '{"company_key": "name:pulley", ...}'
  append_row.py person   FILE --json '{"lead_id": "baserow:1171339:97", ...}'
  append_row.py triage   FILE --json '{...}'
  append_row.py committee FILE --json '{...}'
  append_row.py crm-company | crm-contact | crm-committee | override FILE --json '{...}'
  append_row.py skip      work/06-enrich-skipped.csv --json '{"company_key_final": "...", "reason": "budget"}'
  append_row.py bounceban work/07-bounceban.csv --json '{"email": "...", "bounceban_result": "deliverable"}'

Unknown field names are an error (fix the name, don't invent columns). Missing
fields are written blank. Values are written as given; the vocabulary is checked
later by checks.py gate 2.
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import label as L  # noqa: E402
import assemble as A  # noqa: E402

KINDS = {
    "company": L.COMPANY_FACT_FIELDS, "person": L.PERSON_FACT_FIELDS, "triage": L.TRIAGE_FIELDS,
    "committee": L.COMMITTEE_FIELDS, "crm-company": L.CRM_COMPANY_FIELDS,
    "crm-contact": L.CRM_CONTACT_FIELDS, "crm-committee": A.CRM_COMMITTEE_FIELDS,
    "override": ["level", "key", "field", "new_value", "reason", "source_url"],
    "skip": ["company_key_final", "reason"],          # work/06-enrich-skipped.csv
    "bounceban": A.BOUNCEBAN_FIELDS,                  # work/07-bounceban.csv (one bulk call per run)
}
REQUIRED = {"company": "company_key", "person": "lead_id", "triage": "company_key",
            "committee": "company_key_final", "crm-company": "company_key_final",
            "crm-contact": "lead_id", "crm-committee": "company_key_final", "override": "key",
            "skip": "company_key_final", "bounceban": "email"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=sorted(KINDS))
    ap.add_argument("file")
    ap.add_argument("--json", required=True)
    a = ap.parse_args(argv)
    fields = KINDS[a.kind]
    row = json.loads(a.json)
    bad = [k for k in row if k not in fields]
    if bad:
        sys.exit(f"unknown field(s) for {a.kind}: {', '.join(bad)}. Allowed: {', '.join(fields)}")
    if not str(row.get(REQUIRED[a.kind], "")).strip():
        sys.exit(f"{REQUIRED[a.kind]} is required")
    new = not os.path.exists(a.file) or os.path.getsize(a.file) == 0
    if not new:
        with open(a.file, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f), [])
        if header != fields:
            sys.exit(f"{a.file} has a different header; it was not written by append_row.py")
    os.makedirs(os.path.dirname(os.path.abspath(a.file)), exist_ok=True)
    with open(a.file, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow({k: " ".join(str(row.get(k, "")).split()) for k in fields})
    print(f"appended 1 {a.kind} row to {os.path.basename(a.file)}")


if __name__ == "__main__":
    main()
