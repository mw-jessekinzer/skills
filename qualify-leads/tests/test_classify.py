"""Golden tests for classify.py and normalize.py adapters."""
import json
import os
import re
import unittest

from helpers import AS_OF, C, classify, lid, new_run, normalize, quiet, rb2b, run_rb2b

REF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")


def p1(run):
    return {r["lead_id"]: r for r in C.read_csv(C.work(run, "02-pass1.csv"))}


class TitleGroups(unittest.TestCase):
    CASES = {
        "Chief Technology Officer": "Primary: technology/product",
        "VP of Engineering": "Primary: technology/product",
        "MIS Director at Chatham County (Interim)": "Primary: technology/product",
        "Head of Infrastructure Engineering": "Primary: technology/product",
        "Creative Director": "Primary: design/creative",
        "Talent Acquisition Manager": "Primary: recruiting/people",
        "Director of Talent Acquisition": "Primary: recruiting/people",
        "Head of Talent": "Primary: recruiting/people",
        "Recruiting Director": "Primary: recruiting/people",
        "Director of Operations": "Primary: operations/transformation",
        "Recruiter": "Secondary influencer",
        "Technical Recruiter": "Secondary influencer",
        "Vice President, Marketing": "Secondary influencer",
        "Lead Software Engineer": "Secondary influencer",
        "Co-Founder": "Generic exec",
        "PRESIDENT": "Generic exec",
        "Chief Everything Officer": "Generic exec",
        "Acting President and CEO": "Generic exec",
        "Agency Recruiter": "Excluded title",
        "Staffing Recruiter": "Excluded title",
        "Special Education Teacher": "Excluded title",
        "Retired": "Excluded title",
        "Customer Service Representative": "Excluded title",
        "Retail sales associate": "Unrelated title",
        "2nd VP Mortgage Banker at MidWestOne Bank": "Unrelated title",
        "": "No title",
        "None": "No title",
    }

    def test_groups(self):
        for title, group in self.CASES.items():
            self.assertEqual(classify.classify_title(title)[0], group, title)

    def test_ambiguous_engineer_flag(self):
        self.assertEqual(classify.classify_title("Mechanical Engineer")[2], "yes")
        self.assertEqual(classify.classify_title("Senior Software Engineer")[2], "no")


class Intent(unittest.TestCase):
    def test_survey_is_a_visit_not_a_submission(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme", page="https://midwestern.com/survey",
                             referrer="https://l.facebook.com/")])
        r = p1(run)[lid(1)]
        self.assertEqual(r["intent_level"], "High")
        self.assertIn("Configure a team quiz", r["intent_phrase"])
        self.assertIsNone(C.INTENT_OVERSTATE_RE.search(r["intent_phrase"]))

    def test_referrer_by_host_never_substring(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme", referrer="https://connect.themediatrust.com/x"),
                        rb2b(2, "C D", "CTO", "Beta", referrer="https://www.nypost.com/")])
        rows = p1(run)
        self.assertEqual(rows[lid(1)]["intent_level"], "None")
        self.assertNotIn("Twitter", rows[lid(1)]["source_channel"])
        self.assertEqual(rows[lid(2)]["source_channel"], "nypost.com")

    def test_paid_ad_landing_page_is_low(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme", page="https://midwestern.com/services/recruiting/direct-placement",
                             referrer="https://l.facebook.com/")])
        r = p1(run)[lid(1)]
        self.assertEqual(r["intent_level"], "Low")
        self.assertEqual(r["intent_phrase"], "Arrived from Facebook (likely an ad) at the recruiting direct-placement page")


class SizeAndCodes(unittest.TestCase):
    def test_rb2b_size_is_only_a_flag(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme", employees="10001"),
                        rb2b(2, "C D", "CTO", "Beta", employees="1001")])
        rows = p1(run)
        self.assertEqual(rows[lid(1)]["rb2b_size_flag"], "rb2b_says_over")
        self.assertEqual(rows[lid(2)]["rb2b_size_flag"], "")
        self.assertNotIn("OVER", rows[lid(1)]["pass1_codes"])
        comp = {c["company_key"]: c for c in C.read_csv(C.work(run, "02-companies.csv"))}
        self.assertEqual(comp["name:acme"]["triage_first"], "yes")

    def test_hard_codes(self):
        run = run_rb2b([rb2b(1, "A B", "Operations Manager", "Total Aviation Staffing"),
                        rb2b(2, "C D", "Psychopedagogist", "Self employed", lead_type="Likely job seeker"),
                        rb2b(3, "E F", "Engineer", "Midwestern Interactive"),
                        rb2b(4, "G H", "Student at State College", "")])
        rows = p1(run)
        self.assertIn("COMPETITOR_STAFFING", rows[lid(1)]["pass1_codes"])
        self.assertIn("CONSUMER_SELF_EMPLOYED", rows[lid(2)]["pass1_codes"])
        self.assertIn("JOB_SEEKER", rows[lid(2)]["pass1_codes"])
        self.assertIn("INTERNAL", rows[lid(3)]["pass1_codes"])
        self.assertIn("STUDENT_EDUCATOR", rows[lid(4)]["pass1_codes"])
        self.assertTrue(all(rows[lid(i)]["research_priority"] == "X" for i in (1, 2, 3, 4)))

    def test_company_key_prefers_name_over_rb2b_website(self):
        run = run_rb2b([rb2b(1, "A B", "Owner", "Bunk Bar, Inc", website="https://carahsoft.com")])
        self.assertEqual(p1(run)[lid(1)]["company_key"], "name:bunk bar")


class Adapters(unittest.TestCase):
    def test_social_export_ignores_app_tiers_and_past_employers(self):
        d = new_run("ql-social-")
        path = os.path.join(d, "leads-list-2026-09-28.csv")
        fields = ["name", "title", "company", "tag", "outreachStatus", "linkedinUrl", "listAddedAt", "distinctExecs",
                  "distinctPosts", "reactions", "comments", "replies", "firstSeenAt", "lastSeenAt", "heatTier"]
        C.write_csv(path, [
            dict(name="Ana Ruiz", title="VP Engineering", company="Acme", tag="not_fit", linkedinUrl="https://www.linkedin.com/in/anaruiz",
                 distinctExecs="2", distinctPosts="3", reactions="4", comments="0", replies="0", lastSeenAt="2026-09-20T10:00:00Z", heatTier="like"),
            dict(name="Ben Cho", title="CTO", company="OldCo (past)", tag="prospect", linkedinUrl="https://linkedin.com/in/bencho/",
                 distinctExecs="1", distinctPosts="1", reactions="0", comments="1", replies="0", lastSeenAt="2026-09-21", heatTier="comment"),
        ], fields)
        run = new_run("ql-test-")
        quiet(normalize.main, ["--run", run, "--adapter", "social", "--input", path, "--as-of", AS_OF])
        quiet(classify.main, ["--run", run])
        canon = {r["lead_id"]: r for r in C.read_csv(C.work(run, "01-canonical.csv"))}
        rows = p1(run)
        ana, ben = canon["exec_analytics:anaruiz"], canon["exec_analytics:bencho"]
        self.assertEqual(ana["email_origin"], "none")
        self.assertEqual(rows["exec_analytics:anaruiz"]["intent_level"], "Medium")
        self.assertEqual(ben["company_name_raw"], "")
        self.assertEqual(ben["past_company"], "OldCo")
        self.assertEqual(rows["exec_analytics:bencho"]["intent_phrase"], "Commented on a Midwestern exec's post")
        self.assertNotIn("not_fit", json.dumps(canon))

    def test_dedupe_reconciles(self):
        rows = [rb2b(1, "A B", "CTO", "Acme", seen="2026-09-02T00:00:00Z"),
                rb2b(2, "A B", "CTO", "Acme", seen="2026-09-09T00:00:00Z", page="https://midwestern.com/contact")]
        rows[1]["LinkedIn URL"] = rows[0]["LinkedIn URL"]
        run = run_rb2b(rows)
        canon = C.read_csv(C.work(run, "01-canonical.csv"))
        self.assertEqual(len(canon), 1)
        self.assertEqual(canon[0]["lead_id"], lid(1))
        self.assertEqual(canon[0]["touch_date"], "2026-09-09")
        self.assertEqual(p1(run)[lid(1)]["intent_level"], "High")
        self.assertEqual(len(C.read_csv(C.work(run, "01-dupes.csv"))), 1)


class Batches(unittest.TestCase):
    def test_keep_batches_survive_reruns(self):
        run = run_rb2b([rb2b(1, company="Net Health"), rb2b(2, company="Acme Labs")])
        C.write_csv(C.work(run, "03-triage-triage-1.csv"), [
            {"company_key": "name:net health", "triage": "Keep", "size_tier": "C"},
            {"company_key": "name:acme labs", "triage": "Drop", "drop_code": "UNIDENTIFIABLE", "size_tier": "C"}],
            ["company_key", "company_name", "what_they_do", "employees_text", "employees_best", "size_tier",
             "us_company", "triage", "drop_code", "why"])
        quiet(classify.main, ["keeps", "--run", run])
        quiet(classify.main, ["keeps", "--run", run])          # idempotent: no second batch
        quiet(classify.main, ["--run", run])                   # a rerun keeps the keep batch
        keeps = C.glob_work(run, "02-batch-keep-")
        self.assertEqual([os.path.basename(p) for p in keeps], ["02-batch-keep-1.csv"])
        self.assertEqual([r["company_key"] for r in C.read_csv(keeps[0])], ["name:net health"])


class HumanFacingText(unittest.TestCase):
    """Anything a rep or JK reads: no dashes, no banned words, no tropes."""

    def test_templates_and_tables(self):
        texts = [r["template"] for r in C.ref_csv("reason-codes.csv")]
        texts += [r["label"] + " " + r["phrase"] for r in C.ref_csv("page-intent.csv")]
        texts += [r["channel"] for r in C.ref_csv("referrer-hosts.csv")]
        for t in texts:
            self.assertEqual(C.lint_text(t, jargon=True), [], t)

    def test_reference_docs_have_no_dashes(self):
        for name in os.listdir(REF):
            if name.endswith(".md"):
                with open(os.path.join(REF, name), encoding="utf-8") as f:
                    text = f.read()
                self.assertIsNone(re.search("[—–]", text), name)


if __name__ == "__main__":
    unittest.main()
