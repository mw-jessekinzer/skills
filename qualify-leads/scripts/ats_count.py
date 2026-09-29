#!/usr/bin/env python3
"""Count open roles from a company's job board JSON. Free; never parse boards by eye.

  ats_count.py --ats greenhouse --slug <slug>
  ats_count.py --ats lever --slug <slug>
  ats_count.py --ats ashby --slug <slug>
  ats_count.py --ats workday --tenant <tenant> --site <site> [--wd wd5]
  ats_count.py --ats workable --slug <slug>           # apply.workable.com/<slug>
  ats_count.py --ats adp --cid <cid>                  # cid= from the ADP careers page URL
  ats_count.py --ats ashby --file saved.json          # parse a saved response instead

iCIMS has no public JSON endpoint: read those careers pages directly.

Prints JSON: open_roles_total, open_tech_roles, open_tech_roles_us,
non_us_tech_locations, examples (up to 3 tech titles, US first), newest_post_date,
oldest_tech_post_date, source_url, hiring_checked. Tech roles = references/tech-roles.txt.
A role counts as US when its location says so; an unspecified location (Remote,
Americas, "2 Locations") counts as US only when --us-company is yes (default).
A 404, a wrong slug, or an unreadable board prints hiring_checked "not_checked"
with the error, never a traceback.

Network calls need Bash with the sandbox disabled.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

US_STATES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM "
             "NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
# Georgia and Jersey are left out on purpose: both are also places outside the US.
STATE_NAMES = ("alabama,alaska,arizona,arkansas,california,colorado,connecticut,delaware,florida,hawaii,"
               "idaho,illinois,indiana,iowa,kansas,kentucky,louisiana,maine,maryland,massachusetts,michigan,"
               "minnesota,mississippi,missouri,montana,nebraska,nevada,new hampshire,new jersey,new mexico,"
               "new york,north carolina,north dakota,ohio,oklahoma,oregon,pennsylvania,rhode island,"
               "south carolina,south dakota,tennessee,texas,utah,vermont,virginia,washington,west virginia,"
               "wisconsin,wyoming").split(",")
US_CITIES = {"san francisco", "new york", "nyc", "chicago", "austin", "boston", "seattle", "denver", "atlanta",
             "los angeles", "dallas", "houston", "miami", "kansas city", "st. louis", "saint louis", "philadelphia",
             "washington", "san diego", "san jose", "palo alto", "menlo park", "mountain view", "portland",
             "nashville", "raleigh", "salt lake city", "phoenix", "minneapolis", "detroit", "pittsburgh",
             "columbus", "indianapolis", "charlotte", "springfield", "joplin", "carthage", "tulsa", "omaha"}
STATE_RE = re.compile(r",\s*(" + "|".join(US_STATES) + r")\b")


NON_US_RE = re.compile(
    r"\b(canada|india|united kingdom|england|scotland|wales|ireland|germany|france|spain|portugal|"
    r"netherlands|poland|romania|ukraine|israel|australia|new zealand|mexico|brazil|argentina|colombia|"
    r"philippines|singapore|japan|china|south africa|sweden|denmark|norway|finland|belgium|switzerland|"
    r"austria|italy|cape town|bangalore|bengaluru|hyderabad|pune|chennai|london|toronto|vancouver|"
    r"montreal|ottawa|dublin|berlin|tel aviv|manila|kyiv)\b", re.I)
CA_PROVINCE_RE = re.compile(r",\s*(on|bc|qc|ab|mb|ns|nb|nl|pe|sk)\s*,\s*ca\b", re.I)
# trailing country codes that are not also US state codes (so not CA, DE, IN, IL, CO)
FOREIGN_CODE_RE = re.compile(r",\s*(gb|uk|au|ie|za|nl|se|fr|es|br|mx|sg|jp|cn|ph|ua|ro|nz|pl|pt)\s*$", re.I)
UNSPECIFIED_WORDS = re.compile(r"\b(remote|hybrid|anywhere|americas|north america|\d+ locations?|multiple locations|"
                               r"various locations|on site|onsite)\b", re.I)


def is_us(location, remote, us_company=True):
    """True for a US role. Unspecified locations (Remote, Americas, '2 Locations')
    count as US only for a US company; explicit foreign places never do."""
    loc = C.clean(location)
    low = loc.lower()
    if re.search(r",\s*us\s*$", low) or re.search(r"\b(united states|usa|u\.s\.a?\.?|us[- ]remote|remote[- ,(]*us\b|us only)\b", low):
        return True
    if NON_US_RE.search(loc) or CA_PROVINCE_RE.search(loc) or FOREIGN_CODE_RE.search(loc):
        return False
    if STATE_RE.search(loc) or any(re.search(rf"\b{re.escape(n)}\b", low) for n in STATE_NAMES) or \
            any(re.search(rf"\b{re.escape(c)}\b", low) for c in US_CITIES):
        return True
    if not re.sub(r"[\W_]+", "", UNSPECIFIED_WORDS.sub("", low)):
        return us_company
    return False


def fetch(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json", "User-Agent": "qualify-leads/1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def jobs_greenhouse(d):
    for j in d.get("jobs", []):
        yield j.get("title", ""), (j.get("location") or {}).get("name", ""), False, \
            j.get("first_published") or j.get("updated_at", "")


def jobs_lever(d):
    for j in d if isinstance(d, list) else []:
        cat = j.get("categories") or {}
        yield j.get("text", ""), " ".join(x for x in (cat.get("location", ""), j.get("country", "")) if x), \
            j.get("workplaceType") == "remote", str(j.get("createdAt", ""))


def jobs_ashby(d):
    for j in d.get("jobs", []):
        if str(j.get("isListed", True)).lower() == "false":
            continue
        addr = ((j.get("address") or {}).get("postalAddress") or {})
        loc = " ".join(x for x in (j.get("location", ""), addr.get("addressRegion", ""), addr.get("addressCountry", "")) if x)
        yield j.get("title", ""), loc, str(j.get("isRemote")).lower() == "true", j.get("publishedAt", "")


def jobs_workday(d):
    for j in d.get("jobPostings", []):
        yield j.get("title", ""), j.get("locationsText", ""), False, ""


def jobs_workable(d):
    for j in d.get("jobs", []):
        locs = j.get("locations") or [{"country": j.get("country", ""), "city": j.get("city", ""),
                                       "region": j.get("state", "")}]
        loc = "; ".join(", ".join(x for x in (l.get("city", ""), l.get("region", ""), l.get("country", "")) if x)
                        for l in locs)
        yield j.get("title", ""), loc, bool(j.get("telecommuting")), j.get("published_on", "")


def jobs_adp(d):
    for j in d.get("jobRequisitions", []):
        locs = [((l.get("nameCode") or {}).get("shortName") or "").strip() for l in j.get("requisitionLocations") or []]
        yield j.get("requisitionTitle", ""), "; ".join(x for x in locs if x), False, j.get("postDate", "")


PARSERS = {"greenhouse": jobs_greenhouse, "lever": jobs_lever, "ashby": jobs_ashby, "workday": jobs_workday,
           "workable": jobs_workable, "adp": jobs_adp}
# iCIMS is not supported: its career portals have no public JSON endpoint (HTML only).
# Read an iCIMS careers page directly and record hiring_checked = careers_page.


def count(ats, data, source_url="", us_company=True):
    tech_re = C.tech_role_regex()
    total = tech = tech_us = 0
    ex_us, ex_other, dates, tech_dates, non_us = [], [], [], [], []
    for title, loc, remote, posted in PARSERS[ats](data):
        total += 1
        d = C.parse_date(posted)
        if d:
            dates.append(d)
        if tech_re.search(title or ""):
            tech += 1
            if d:
                tech_dates.append(d)
            if is_us(loc, remote, us_company):
                tech_us += 1
                ex_us.append(title)
            else:
                ex_other.append(title)
                where = C.clean(loc)
                if where and where not in non_us:
                    non_us.append(where)
    return {"open_roles_total": total, "open_tech_roles": tech, "open_tech_roles_us": tech_us,
            "non_us_tech_locations": "; ".join(non_us[:3]),
            "examples": (ex_us + ex_other)[:3], "newest_post_date": C.iso(max(dates)) if dates else "",
            "oldest_tech_post_date": C.iso(min(tech_dates)) if tech_dates else "",
            "source_url": source_url, "hiring_checked": "ats_api"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ats", required=True, choices=sorted(PARSERS))
    ap.add_argument("--slug", default="")
    ap.add_argument("--tenant", default="")
    ap.add_argument("--site", default="")
    ap.add_argument("--wd", default="wd5")
    ap.add_argument("--file", default="")
    ap.add_argument("--us-company", default="yes", choices=["yes", "no"])
    ap.add_argument("--cid", default="", help="ADP: the cid= value from the careers page URL")
    a = ap.parse_args(argv)
    url = ""
    try:
        data, url = load(a)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError) as e:
        # a 404, a wrong slug, or an unreadable board is "not checked", never a crash
        print(json.dumps({"hiring_checked": "not_checked", "source_url": url or a.slug or a.cid,
                          "error": f"{type(e).__name__}: {e}"[:200]}, indent=2))
        return
    print(json.dumps(count(a.ats, data, url, a.us_company == "yes"), indent=2))


def load(a):
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            return json.load(f), a.file
    if a.ats == "workable":
        url = f"https://apply.workable.com/api/v1/widget/accounts/{a.slug}"
        return fetch(url), url
    if a.ats == "adp":
        base = ("https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/"
                f"job-requisitions?cid={a.cid}&ccId=19000101_000001&lang=en_US&locale=en_US")
        reqs, skip = [], 0
        while True:
            page = fetch(f"{base}&$top=100&$skip={skip}")
            got = page.get("jobRequisitions", [])
            reqs += got
            total = ((page.get("meta") or {}).get("totalNumber")) or len(reqs)
            skip += 100
            if not got or len(reqs) >= total:
                break
        return {"jobRequisitions": reqs}, base
    if a.ats == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{a.slug}/jobs"
        data = fetch(url)
    elif a.ats == "lever":
        url = f"https://api.lever.co/v0/postings/{a.slug}?mode=json"
        data = fetch(url)
    elif a.ats == "ashby":
        url = f"https://api.ashbyhq.com/posting-api/job-board/{a.slug}"
        data = fetch(url)
    else:
        url = f"https://{a.tenant}.{a.wd}.myworkdayjobs.com/wday/cxs/{a.tenant}/{a.site}/jobs"
        posts, offset, total = [], 0, None
        while total is None or offset < total:
            page = fetch(url, {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": ""})
            total = page.get("total", 0) if total is None else total
            posts += page.get("jobPostings", [])
            offset += 20
            if not page.get("jobPostings"):
                break
        data = {"jobPostings": posts}
    return data, url


if __name__ == "__main__":
    main()
