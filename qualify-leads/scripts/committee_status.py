#!/usr/bin/env python3
"""Print the email status of each committee member for one company. Writes nothing.

Packet workers use this for the packet's Email status column so it is the exact
string the CSV and 08-committee-status.csv will carry. Workers never run
assemble.py; the orchestrator runs it once after every packet is written.

  committee_status.py --run RUN_DIR --company withpulley.com
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import assemble as A  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--company", required=True, help="company_key_final")
    a = ap.parse_args(argv)
    run = C.load_run(a.run)
    ctx, facts = A.company_context(a.run)
    members = [m for m in A.committee_status(a.run, C.parse_date(run.get("as_of")), ctx, facts)
               if m["company_key_final"] == a.company]
    if not members:
        sys.exit(f"no committee rows for {a.company}")
    print("| Name | Email | Email status | Domain ok | Employer ok | In HubSpot |")
    print("|---|---|---|---|---|---|")
    for m in members:
        print(f"| {m['full_name']} | {m['email']} | {m['email_status']} | {m['domain_ok']} | "
              f"{m['employer_domain_ok']} | {m['in_hubspot']} |")


if __name__ == "__main__":
    main()
