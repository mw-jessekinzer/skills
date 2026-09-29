"""Build throwaway runs for the golden tests. Every test gets its own temp folder."""
import atexit
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)
sys.dont_write_bytecode = True

import common as C  # noqa: E402
import normalize  # noqa: E402
import classify  # noqa: E402
import label as L  # noqa: E402
import assemble as A  # noqa: E402

AS_OF = "2026-09-25"


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def rb2b(id, name="", title="", company="", email="", website="", lead_type="Buyer candidate",
         page="https://midwestern.com/", referrer="", seen="2026-09-08T10:00:00Z", employees=""):
    first, _, last = name.partition(" ")
    return {"id": id, "Name": name or company, "LinkedIn URL": f"https://www.linkedin.com/in/p{id}" if name else "",
            "Lead Type": lead_type if name else "Company only", "First Name": first, "Last Name": last,
            "Title": title, "Company Name": company, "Business Email": email, "Company Website": website,
            "Industry": "", "Employee Count": employees, "City": "", "State": "",
            "First Seen At": seen, "Last Seen At": seen, "Visit Count": "1",
            "First Captured URL": page, "Last Captured URL": page, "Referrer": referrer, "Tags": ""}


_TEMP = []


@atexit.register
def _cleanup():
    for d in _TEMP:
        shutil.rmtree(d, ignore_errors=True)


def new_run(prefix="ql-test-"):
    d = tempfile.mkdtemp(prefix=prefix)
    _TEMP.append(d)
    return d


def run_rb2b(rows, prior_dir=""):
    run = new_run()
    src = os.path.join(run, "rows.json")
    with open(src, "w") as f:
        json.dump(rows, f)
    quiet(normalize.main, ["--run", run, "--adapter", "rb2b-baserow", "--input", src, "--as-of", AS_OF])
    quiet(classify.main, ["--run", run] + (["--prior-dir", prior_dir] if prior_dir else []))
    return run


def run_csv(path, touch_type, campaign="Test list"):
    run = new_run()
    quiet(normalize.main, ["--run", run, "--adapter", "csv", "--input", path, "--touch-type", touch_type,
                           "--campaign", campaign, "--as-of", AS_OF])
    quiet(classify.main, ["--run", run])
    return run


def _append(path, fields, row):
    rows = C.read_csv(path)
    rows.append({f: "" for f in fields} | row)
    C.write_csv(path, rows, fields)


def company(run, key, **facts):
    facts.setdefault("research_depth", "deep")
    _append(C.work(run, "03-research-companies-t.csv"), L.COMPANY_FACT_FIELDS, dict(company_key=key, **facts))


def person(run, lead_id, **facts):
    _append(C.work(run, "03-research-people-t.csv"), L.PERSON_FACT_FIELDS, dict(lead_id=lead_id, **facts))


def triage(run, key, **facts):
    facts.setdefault("size_tier", "C")
    _append(C.work(run, "03-triage-t.csv"), L.TRIAGE_FIELDS, dict(company_key=key, **facts))


def crm_company(run, key, **facts):
    facts.setdefault("checked", "yes")
    _append(C.work(run, "04-crm-companies.csv"), L.CRM_COMPANY_FIELDS, dict(company_key_final=key, **facts))


def crm_contact(run, lead_id, **facts):
    facts.setdefault("checked", "yes")
    _append(C.work(run, "04-crm-contacts.csv"), L.CRM_CONTACT_FIELDS, dict(lead_id=lead_id, **facts))


def committee(run, key, **m):
    _append(C.work(run, f"07-committee-{L.slug(key)}.csv"), L.COMMITTEE_FIELDS, dict(company_key_final=key, **m))


def override(run, level, key, field, value, reason="test"):
    _append(C.work(run, "overrides.csv"), ["level", "key", "field", "new_value", "reason", "source_url"],
            dict(level=level, key=key, field=field, new_value=value, reason=reason))


def label(run):
    rows, roll, tier1 = quiet(L.run_label, run)
    return {r["lead_id"]: r for r in rows}, roll, tier1


def lid(id):
    return f"baserow:1171339:{id}"


# A verified-under US company with open US tech roles: the usual "good account".
GOOD = dict(us_company="yes", employees_best="120", employees_text="about 120",
            employees_source="LinkedIn company page 2026-09", size_tier="A", hiring_checked="ats_api",
            open_roles_total="8", open_tech_roles="5", open_tech_roles_us="5", service_fit="Recruiting")
