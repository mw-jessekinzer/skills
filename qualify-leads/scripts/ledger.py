#!/usr/bin/env python3
"""Cost and yield ledger for paid vendor calls (Deepline, Hirebase, MoltSets).

Every paid or possibly paid call gets one `add` BEFORE the next call starts.
A timeout or error is logged as charged at list price until a balance proves otherwise.

  ledger.py add --run RUN --stage S6 --vendor deepline --endpoint dropleads_email_finder \
      --company withpulley.com --person "Chad Ackerman" --input "Chad Ackerman @ withpulley.com" \
      --charged 0.26 --result hit --useful yes [--balance-after 14.82] [--note "..."]
  ledger.py balance --run RUN --vendor deepline --when start --value 20.52
  ledger.py check --run RUN --vendor deepline --projected 2.0     # exit 2 = STOP AND ASK JK
  ledger.py summary --run RUN                                      # table + work/ledger-summary.json
  ledger.py close --run RUN --run-name "2026-09-25 RB2B" --vendor-ledger "/…/Lead Triage/vendor-ledger.csv"

  ledger.py caps --run RUN --deepline 2 --moltsets 10 --approved-by "JK"   # logged in the run log

Caps (per run, JK 2026-09-28): Deepline 10 credits, Hirebase 25 credits,
MoltSets 60 tokens. Change them only with JK's approval, through `caps`.
Caps are enforced on THIS run's ledger spend. Vendor balances are shared across
runs, so `balance` readings are informational (checks.py warns, never fails, on drift).
"""
import argparse
import csv
import fcntl
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

FIELDS = ["run_id", "ts", "stage", "vendor", "endpoint", "company_key", "person",
          "input_summary", "charged", "unit", "result", "useful", "balance_after", "note"]
RESULTS = {"hit", "miss", "timeout", "error", "catch_all", "deliverable", "undeliverable",
           "pending"}  # pending: a BounceBan bulk job submitted, results read later
VENDOR_FIELDS = ["run_date", "run_name", "vendor", "spent", "unit", "cap", "calls", "hits",
                 "useful", "cost_per_useful", "usd_est", "note"]
USD_PER_UNIT = {"deepline": 0.10, "hirebase": 0.0, "moltsets": 0.0}


def ledger_path(run):
    return os.path.join(run, "cost-ledger.csv")


def caps(run):
    return C.load_run(run).get("caps") or C.DEFAULT_CAPS


def spent_by_vendor(run):
    out = {}
    for r in C.read_csv(ledger_path(run)):
        v = r["vendor"]
        out[v] = out.get(v, 0.0) + float(r["charged"] or 0)
    return out


def append_locked(path, row):
    """Append one row under an exclusive lock, so parallel workers never lose rows."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0, os.SEEK_END)
            w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
            if f.tell() == 0:
                w.writeheader()
            w.writerow(row)
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def cmd_caps(a):
    """Set this run's caps from the command line and log who approved the change."""
    run = C.load_run(a.run)
    cp = {k: list(v) for k, v in (run.get("caps") or C.DEFAULT_CAPS).items()}
    changed = []
    for v in ("deepline", "hirebase", "moltsets"):
        val = getattr(a, v)
        if val is not None:
            changed.append(f"{v} {cp[v][0]:g} -> {val:g}")
            cp[v][0] = val
    if not changed:
        sys.exit("give at least one of --deepline, --hirebase, --moltsets")
    run["caps"] = cp
    C.save_run(a.run, run)
    C.append_log(a.run, f"caps changed: {', '.join(changed)} (approved by {a.approved_by})")
    print(f"caps now: " + ", ".join(f"{k} {v[0]:g} {v[1]}s" for k, v in cp.items()))
    return 0


def cmd_add(a):
    v = a.vendor.lower()
    cp = caps(a.run)
    if v not in cp:
        sys.exit(f"unknown vendor {v}; known: {', '.join(cp)}")
    if a.result not in RESULTS:
        sys.exit(f"--result must be one of {sorted(RESULTS)}")
    row = {"run_id": os.path.basename(os.path.abspath(a.run)),
           "ts": datetime.now().isoformat(timespec="seconds"), "stage": a.stage,
           "vendor": v, "endpoint": a.endpoint, "company_key": a.company,
           "person": a.person, "input_summary": a.input, "charged": f"{a.charged:g}",
           "unit": cp[v][1], "result": a.result, "useful": a.useful,
           "balance_after": a.balance_after, "note": a.note}
    append_locked(ledger_path(a.run), row)
    spent = spent_by_vendor(a.run).get(v, 0.0)
    print(f"{v}: spent {spent:g} of {cp[v][0]:g} {cp[v][1]}s")
    if spent > cp[v][0]:
        print(f"OVER CAP: {v} is past its {cp[v][0]:g} cap. Stop and ask JK.")
        return 2
    return 0


def cmd_balance(a):
    run = C.load_run(a.run)
    run.setdefault("balances", {}).setdefault(a.vendor.lower(), {})[a.when] = a.value
    C.save_run(a.run, run)
    print(f"recorded {a.vendor} {a.when} balance {a.value:g}")
    return 0


def cmd_check(a):
    v = a.vendor.lower()
    cp = caps(a.run)
    spent = spent_by_vendor(a.run).get(v, 0.0)
    total = spent + a.projected
    print(f"{v}: spent {spent:g} + projected {a.projected:g} = {total:g} of cap {cp[v][0]:g}")
    for s in C.load_run(a.run).get("budget_short") or []:
        if s.startswith(v + ":"):
            print(f"WARNING: Tier 1 budget below plan ({s}); expect thinner committees or skip a company.")
    if total > cp[v][0]:
        print("STOP AND ASK JK: finish nothing new. Report spent per vendor, what is left undone, "
              "projected cost to finish, and a recommendation.")
        return 2
    return 0


def summarize(run):
    rows = C.read_csv(ledger_path(run))
    cp = caps(run)
    bal = C.load_run(run).get("balances", {})
    out = {}
    for v, (cap, unit) in sorted(cp.items()):
        vr = [r for r in rows if r["vendor"] == v]
        spent = sum(float(r["charged"] or 0) for r in vr)
        hits = sum(r["result"] in ("hit", "deliverable", "catch_all") for r in vr)
        useful = sum(r["useful"] == "yes" for r in vr)
        b = bal.get(v, {})
        recon = ""
        if "start" in b and "end" in b:
            diff = (b["start"] - b["end"]) - spent
            tol = 0.1 if unit == "credit" else 1
            recon = "balances reconcile" if abs(diff) <= tol else \
                f"balance moved {diff:+.2f} {unit}s beyond this ledger (shared account; informational)"
        out[v] = {"spent": round(spent, 2), "cap": cap, "unit": unit, "calls": len(vr), "hits": hits,
                  "useful": useful, "cost_per_useful": round(spent / useful, 2) if useful else "",
                  "usd_est": round(spent * USD_PER_UNIT.get(v, 0), 2), "reconcile": recon}
    return out


def cmd_summary(a):
    s = summarize(a.run)
    C.write_json(C.work(a.run, "ledger-summary.json"), s)
    print("| Vendor | Spent / cap | Calls | Hits | Useful | Cost per useful | USD est. | Balance check |")
    print("|---|---|---|---|---|---|---|---|")
    for v, x in s.items():
        print(f"| {v} | {x['spent']:g} / {x['cap']:g} {x['unit']}s | {x['calls']} | {x['hits']} | "
              f"{x['useful']} | {x['cost_per_useful']} | {x['usd_est']} | {x['reconcile'] or 'no balances recorded'} |")
    return 0


def cmd_close(a):
    s = summarize(a.run)
    existing = C.read_csv(a.vendor_ledger)
    if any(r["run_name"] == a.run_name for r in existing):
        print(f"{a.run_name} already in {a.vendor_ledger}; nothing appended")
        return 0
    d = C.load_run(a.run).get("as_of", "")
    for v, x in s.items():
        existing.append({"run_date": d, "run_name": a.run_name, "vendor": v, "spent": x["spent"],
                         "unit": x["unit"], "cap": x["cap"], "calls": x["calls"], "hits": x["hits"],
                         "useful": x["useful"], "cost_per_useful": x["cost_per_useful"],
                         "usd_est": x["usd_est"], "note": x["reconcile"]})
    C.write_csv(a.vendor_ledger, existing, VENDOR_FIELDS)
    print(f"appended {len(s)} vendor rows to {a.vendor_ledger}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("--run", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--vendor", required=True)
    p.add_argument("--endpoint", required=True)
    p.add_argument("--company", default="")
    p.add_argument("--person", default="")
    p.add_argument("--input", default="")
    p.add_argument("--charged", type=float, required=True)
    p.add_argument("--result", required=True)
    p.add_argument("--useful", choices=["yes", "no"], default="no")
    p.add_argument("--balance-after", default="")
    p.add_argument("--note", default="")
    p = sub.add_parser("balance")
    p.add_argument("--run", required=True)
    p.add_argument("--vendor", required=True)
    p.add_argument("--when", choices=["start", "end"], required=True)
    p.add_argument("--value", type=float, required=True)
    p = sub.add_parser("check")
    p.add_argument("--run", required=True)
    p.add_argument("--vendor", required=True)
    p.add_argument("--projected", type=float, default=0.0)
    p = sub.add_parser("summary")
    p.add_argument("--run", required=True)
    p = sub.add_parser("close")
    p.add_argument("--run", required=True)
    p.add_argument("--run-name", required=True)
    p.add_argument("--vendor-ledger", required=True)
    p = sub.add_parser("caps")
    p.add_argument("--run", required=True)
    p.add_argument("--deepline", type=float)
    p.add_argument("--hirebase", type=float)
    p.add_argument("--moltsets", type=float)
    p.add_argument("--approved-by", required=True)
    a = ap.parse_args(argv)
    return {"add": cmd_add, "balance": cmd_balance, "check": cmd_check,
            "summary": cmd_summary, "close": cmd_close, "caps": cmd_caps}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
