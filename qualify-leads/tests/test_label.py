"""Golden tests for label.py (and the assemble/checks rules it feeds), built from
real cases in the 2026-09-25 RB2B run. Run: python3 -m unittest discover -s tests"""
import filecmp
import os
import tempfile
import unittest

from helpers import (A, AS_OF, C, GOOD, L, committee, company, crm_company, crm_contact, label, lid,
                     new_run, override, person, quiet, rb2b, run_csv, run_rb2b, triage)
import checks


class Cyera(unittest.TestCase):
    """About 1,771 from knowledge must never read as over 2,000."""

    def setUp(self):
        self.run = run_rb2b([rb2b(237, "Dan McLaughlin", "Federal Civilian Sales Director", "Cyera",
                                  website="https://cyera.com", employees="1001-5000")])
        self.key = "name:cyera"

    def test_triage_over_2000_on_1771_is_rejected(self):
        triage(self.run, self.key, company_name="Cyera", employees_best="1771", employees_text="about 1,771",
               us_company="yes", triage="Drop", drop_code="OVER_2000", why="About 1,771 in Mar 2026")
        r = label(self.run)[0][lid(237)]
        self.assertNotIn("OVER_2000", r["reason_codes"])
        self.assertNotIn("2,000 cap", r["why"])
        self.assertEqual(r["size_status"], "straddles")
        self.assertIn("OVER_2000 ignored", r["label_warnings"])

    def test_knowledge_1771_straddles_and_tier_b_1550_is_under(self):
        company(self.run, self.key, company_key_final="cyera.com", domains="cyera.com", us_company="yes",
                employees_best="1771", employees_text="about 1,771", size_tier="C", hiring_checked="ats_api",
                open_roles_total="12", open_tech_roles="9", open_tech_roles_us="4")
        person(self.run, lid(237), works_there="likely", buyer_role="no", buyer_role_why="federal sales")
        r = label(self.run)[0][lid(237)]
        self.assertEqual(r["size_status"], "straddles")
        self.assertEqual(r["account_strength"], "Weak")
        self.assertNotIn("OVER_2000", r["reason_codes"])
        self.assertEqual(r["action"], "Low priority")  # size unconfirmed is a gap, not a Drop
        override(self.run, "company", "cyera.com", "employees_best", "1550")
        override(self.run, "company", "cyera.com", "size_tier", "B")
        r = label(self.run)[0][lid(237)]
        self.assertEqual(r["size_status"], "verified_under")
        self.assertEqual((r["verdict"], r["action"], r["primary_code"]), ("Not qualified", "Account play", "UNRELATED_TITLE"))


class MoMA(unittest.TestCase):
    """About 900 staff must never be 'can't buy'."""

    def setUp(self):
        self.run = run_rb2b([rb2b(320, "Kevin Reid", "Head of Learning and Development", "The Museum of Modern Art",
                                  email="kevinreid4@hotmail.com", website="https://moma.org")])
        self.key = "name:museum of modern art"

    def test_cannot_buy_rejected_over_50(self):
        triage(self.run, self.key, company_name="MoMA", employees_best="900", us_company="yes",
               triage="Drop", drop_code="CANNOT_BUY", why="Museum")
        r = label(self.run)[0][lid(320)]
        self.assertNotIn("CANNOT_BUY", r["reason_codes"])
        self.assertNotIn("can't realistically buy", r["why"])
        self.assertIn("CANNOT_BUY ignored", r["label_warnings"])

    def test_structural_no_need_is_used_with_a_business_model_reason(self):
        triage(self.run, self.key, company_name="The Museum of Modern Art", employees_best="900", us_company="yes",
               triage="Drop", drop_code="STRUCTURAL_NO_NEED",
               why="Museum; no software product; IT and web run by an outside vendor.")
        r = label(self.run)[0][lid(320)]
        self.assertEqual(r["primary_code"], "STRUCTURAL_NO_NEED")
        self.assertEqual(r["action"], "Drop")
        self.assertNotIn("..", r["why"])

    def test_structural_no_need_on_absence_of_evidence_is_parked(self):
        triage(self.run, self.key, company_name="The Museum of Modern Art", employees_best="900", us_company="yes",
               triage="Drop", drop_code="STRUCTURAL_NO_NEED", why="Museum with no tech hiring need found.")
        r = label(self.run)[0][lid(320)]
        self.assertNotIn("STRUCTURAL_NO_NEED", r["reason_codes"])
        self.assertEqual(r["action"], "Low priority")
        self.assertIn("STRUCTURAL_NO_NEED ignored", r["label_warnings"])


class LetterAI(unittest.TestCase):
    """HubSpot's work email replaces RB2B's Gmail; open deal = Tell account owner."""

    def test(self):
        run = run_rb2b([rb2b(18, "Abby Hunt", "Vice President, Marketing", "Letter AI",
                             email="abigailkhunt@gmail.com", website="https://www.letter.ai/")])
        company(run, "name:letter ai", company_key_final="letter.ai", domains="letter.ai", **GOOD)
        person(run, lid(18), works_there="confirmed", buyer_role="partial")
        crm_company(run, "letter.ai", hs_company_id="1", match_type="domain", owner_name="Jonathan Gonzalez",
                    owner_active="yes", open_deals="1", open_deal_summary="Recruiting, 3 roles, $60,000")
        crm_contact(run, lid(18), hs_contact_id="9", match_type="name", email="abby@letter.ai",
                    contact_owner="Blake Fisher", contact_owner_active="yes")
        r = label(run)[0][lid(18)]
        self.assertEqual(r["email"], "abby@letter.ai")
        self.assertEqual(r["email_status"], "From HubSpot")
        self.assertEqual((r["verdict"], r["action"]), ("Possible match", "Tell account owner"))
        self.assertIn("Jonathan Gonzalez", r["next_step"])
        self.assertIn("Blake Fisher", r["next_step"])


class PURE(unittest.TestCase):
    """Person fails (left the company) but the account is strong = Account play."""

    def test(self):
        run = run_rb2b([rb2b(203, "John Burnsed", "Director, Head of Platform Operations", "PURE Insurance",
                             email="john.burnsed@gmail.com", website="https://pureins.co")])
        company(run, "name:pure insurance", company_key_final="pureinsurance.com", domains="pureinsurance.com",
                need_signals="2026-09 ai_initiative: hiring a Senior AI Engineer (Workday)", **GOOD)
        person(run, lid(203), works_there="no", works_there_source="left Jun 2025 per LinkedIn", buyer_role="no")
        r = label(run)[0][lid(203)]
        self.assertEqual((r["verdict"], r["primary_code"]), ("Not qualified", "NOT_AT_COMPANY"))
        self.assertEqual((r["account_strength"], r["action"]), ("Strong", "Account play"))


class PulleyCollision(unittest.TestCase):
    """withpulley.com (construction permitting) is not pulley.com (cap tables)."""

    def setUp(self):
        self.run = run_rb2b([rb2b(97, "Charlie Jacobson", "Co-Founder", "Pulley", email="charlie@withpulley.com",
                                  website="https://withpulley.com")])
        company(self.run, "name:pulley", company_key_final="withpulley.com", domains="withpulley.com", **GOOD)
        person(self.run, lid(97), works_there="confirmed", buyer_role="yes", email_found="charlie@withpulley.com",
               email_risk="A", email_validated_at="2026-09-08")

    def test_committee_member_from_pulley_com_is_rejected(self):
        committee(self.run, "withpulley.com", order="2", full_name="Yin Wu", title="Co-founder and CEO",
                  email="", employer_domain="pulley.com", works_there="confirmed", priority="First call")
        committee(self.run, "withpulley.com", order="3", full_name="Michellie McDonald-O'Brien",
                  title="Talent and People Ops Lead", email="mmcdo@sas.upenn.edu", email_risk="A",
                  email_validated_at="2026-08-31", employer_domain="withpulley.com", works_there="confirmed")
        label(self.run)
        ctx, facts = A.company_context(self.run)
        members = {m["full_name"]: m for m in A.committee_status(self.run, C.parse_date(AS_OF), ctx, facts)}
        self.assertEqual(members["Yin Wu"]["employer_domain_ok"], "no")
        self.assertEqual(members["Michellie McDonald-O'Brien"]["email_status"], "Wrong domain")
        g = checks.gate4(self.run)
        self.assertTrue(any("Yin Wu" in f for f in g.fails))
        self.assertTrue(any("mmcdo@sas.upenn.edu" in f for f in g.fails))

    def test_prior_run_collision_flag(self):
        prior = new_run("ql-prior-")
        C.write_csv(os.path.join(prior, "old.csv"), [{"company": "Pulley", "domain": "pulley.com"},
                                                     {"company": "Pulley", "domain": "withpulley.com"}],
                    ["company", "domain"])
        run = run_rb2b([rb2b(97, "Charlie Jacobson", "Co-Founder", "Pulley", email="charlie@withpulley.com")],
                       prior_dir=prior)
        comp = {c["company_key"]: c for c in C.read_csv(C.work(run, "02-companies.csv"))}
        self.assertIn("pulley.com", comp["name:pulley"]["collision_flag"])
        company(run, "name:pulley", company_key_final="withpulley.com", domains="withpulley.com", **GOOD)
        _, roll, _ = label(run)
        self.assertIn("pulley.com", roll[0]["collision"])


class GiveCampus(unittest.TestCase):
    def test_customer_is_tell_account_owner(self):
        run = run_rb2b([rb2b(77, "Raghavendra Kulkarni", "Head of Infrastructure Engineering", "GiveCampus",
                             email="raghavendra.kulkarni@givecampus.com")])
        company(run, "name:givecampus", company_key_final="givecampus.com", domains="givecampus.com", **GOOD)
        person(run, lid(77), works_there="confirmed", buyer_role="yes")
        crm_company(run, "givecampus.com", hs_company_id="2", match_type="domain", owner_name="Derris Butler",
                    owner_active="yes", lifecycle="customer", closed_won_24m_count="7", closed_won_24m_amount="about $406K")
        crm_contact(run, lid(77), hs_contact_id="3", match_type="email", email="raghavendra.kulkarni@givecampus.com",
                    contact_owner="Derris Butler", contact_owner_active="yes")
        r = label(run)[0][lid(77)]
        self.assertEqual((r["verdict"], r["action"], r["crm_state"]), ("Qualified", "Tell account owner", "customer"))
        self.assertIn("Derris Butler", r["next_step"])


class EmailRules(unittest.TestCase):
    def test_vendor_matched_gmail_caps_at_possible_match(self):
        run = run_rb2b([rb2b(5, "Pat Lee", "VP of Engineering", "Acme Robotics", email="patlee@gmail.com")])
        company(run, "name:acme robotics", company_key_final="acmerobotics.com", domains="acmerobotics.com", **GOOD)
        person(run, lid(5), works_there="confirmed", buyer_role="yes")
        r = label(run)[0][lid(5)]
        self.assertEqual((r["verdict"], r["email_status"]), ("Possible match", "Personal"))
        self.assertIn("OPEN_EMAIL", r["reason_codes"])
        self.assertEqual(r["action"], "Review")

    def test_form_typed_gmail_is_not_qualified(self):
        d = new_run("ql-csv-")
        path = os.path.join(d, "webinar.csv")
        C.write_csv(path, [{"First Name": "Pat", "Last Name": "Lee", "Email": "patlee@gmail.com",
                            "Job Title": "VP of Engineering", "Company": "Acme Robotics"}],
                    ["First Name", "Last Name", "Email", "Job Title", "Company"])
        run = run_csv(path, "form_fill")
        company(run, "name:acme robotics", company_key_final="acmerobotics.com", domains="acmerobotics.com", **GOOD)
        r = list(label(run)[0].values())[0]
        self.assertEqual((r["verdict"], r["primary_code"]), ("Not qualified", "PERSONAL_EMAIL_SUBMITTED"))
        # a person-level fail: the strong account behind it is still worth an account play
        self.assertEqual(r["action"], "Account play")
        run2 = run_csv(path, "form_fill")
        company(run2, "name:acme robotics", company_key_final="acmerobotics.com", domains="acmerobotics.com",
                us_company="yes", employees_best="120", size_tier="A", hiring_checked="ats_api", open_roles_total="0")
        r = list(label(run2)[0].values())[0]
        self.assertEqual((r["verdict"], r["action"]), ("Not qualified", "Drop"))

    def test_form_typed_work_email_is_given_by_the_person(self):
        d = new_run("ql-csv-")
        path = os.path.join(d, "webinar.csv")
        C.write_csv(path, [{"Name": "Pat Lee", "Email": "pat@acmerobotics.com", "Title": "CTO", "Company": "Acme Robotics"}],
                    ["Name", "Email", "Title", "Company"])
        run = run_csv(path, "form_fill")
        company(run, "name:acme robotics", company_key_final="acmerobotics.com", domains="acmerobotics.com", **GOOD)
        r = list(label(run)[0].values())[0]
        self.assertEqual((r["email_status"], r["verdict"], r["action"]), ("Given by the person", "Qualified", "Contact now"))

    def test_status_table(self):
        es = L.email_status
        d = {"acme.com"}
        now = C.parse_date(AS_OF)
        self.assertEqual(es("", d, "none", False, {}), "None")
        self.assertEqual(es("a@other.com", d, "research", False, {}), "Wrong domain")
        self.assertEqual(es("a@acme.com", d, "research", False, {"bounceban_result": "undeliverable"}), "Undeliverable")
        self.assertEqual(es("a@acme.com", d, "research", False, {"email_risk": "A", "email_validated_at": "2026-09-01", "_as_of": now}), "Verified")
        self.assertEqual(es("a@acme.com", d, "research", False, {"email_risk": "A", "email_validated_at": "2026-01-01", "_as_of": now}), "Unverified work email")
        self.assertEqual(es("a@acme.com", d, "research", False, {"domain_accept_all": "yes", "bounceban_result": "deliverable"}), "Verified, catch-all domain")
        self.assertEqual(es("a@acme.com", d, "research", False, {"domain_accept_all": "yes"}), "Catch-all, unconfirmed")
        self.assertEqual(es("a@acme.com", d, "research", False, {"smtp_valid": "yes", "domain_accept_all": "no"}), "Verified")


class Titles(unittest.TestCase):
    def test_ta_title_at_prospect_is_a_buyer(self):
        run = run_rb2b([rb2b(6, "Sam Ortiz", "Talent Acquisition Manager", "Acme Robotics", email="sam@acmerobotics.com")])
        company(run, "name:acme robotics", company_key_final="acmerobotics.com", domains="acmerobotics.com", **GOOD)
        person(run, lid(6), works_there="confirmed", email_found="sam@acmerobotics.com", email_risk="A",
               email_validated_at="2026-09-10")
        r = label(run)[0][lid(6)]
        self.assertEqual(r["title_group"], "Primary: recruiting/people")
        self.assertEqual((r["verdict"], r["action"]), ("Qualified", "Contact now"))

    def test_agency_recruiter_is_excluded(self):
        run = run_rb2b([rb2b(7, "Jo Park", "Senior Recruiter", "Apex Staffing Group", email="jo@apexstaffing.com"),
                        rb2b(8, "Lee Fox", "Agency Recruiter", "Blue Talent", email="lee@bluetalent.com")])
        rows = label(run)[0]
        self.assertEqual((rows[lid(7)]["primary_code"], rows[lid(7)]["action"]), ("COMPETITOR_STAFFING", "Drop"))
        self.assertEqual(rows[lid(8)]["title_group"], "Excluded title")
        self.assertEqual(rows[lid(8)]["action"], "Drop")


class CompanyOnlyAndCompliance(unittest.TestCase):
    def test_company_only_strong_account_is_account_play(self):
        run = run_rb2b([rb2b(348, company="Net Health", website="https://nethealth.com",
                             page="https://midwestern.com/survey", referrer="https://l.facebook.com/")])
        company(run, "name:net health", company_key_final="nethealth.com", domains="nethealth.com",
                need_signals="2026-01 acquisition: acquired Keet Health (press)", **GOOD)
        r = label(run)[0][lid(348)]
        self.assertEqual((r["verdict"], r["primary_code"], r["action"]), ("Insufficient data", "INS_NO_PERSON", "Account play"))

    def test_compliance_exclusion_is_drop(self):
        run = run_rb2b([rb2b(9, "Andrew Ferich", "Partner", "Ahdoot & Wolfson", email="aferich@ahdootwolfson.com")])
        r = label(run)[0][lid(9)]
        self.assertEqual((r["primary_code"], r["action"]), ("COMPLIANCE_DNC", "Drop"))
        self.assertEqual(r["next_step"], "Do not contact. Suppress everywhere.")

    def test_offshore_only_hiring_is_neutral_with_a_watch_out(self):
        """JK 2026-09-28: offshore roles still count as demand (we sell global talent)."""
        run = run_rb2b([rb2b(74, company="Sumo Logic")])
        facts = dict(GOOD, open_tech_roles_us="0", tech_role_locations="India",
                     need_signals="2026-07 ai_initiative: new CEO (press)")
        company(run, "name:sumo logic", company_key_final="sumologic.com", domains="sumologic.com", **facts)
        r = label(run)[0][lid(74)]
        self.assertEqual(r["hiring_status"], "Hiring tech roles, none in US")
        self.assertEqual((r["account_strength"], r["action"]), ("Strong", "Account play"))
        self.assertIn("all outside the US (India)", r["watch_outs"])
        self.assertIn("embedded global talent", r["watch_outs"])
        self.assertEqual(r["open_tech_roles_display"], "0 (5 outside the US)")


class NeedWindow(unittest.TestCase):
    """Need signals count for 18 months (JK 2026-09-28); contraction is not a need."""

    def strength(self, signal):
        run = run_rb2b([rb2b(221, "Danielle Slauter", "Writer", "Lincoln Investment")])
        company(run, "name:lincoln investment", company_key_final="lincolninvestment.com", us_company="yes",
                employees_best="600", size_tier="A", hiring_checked="none_found", need_signals=signal)
        person(run, lid(221), works_there="no", works_there_source="left per LinkedIn", buyer_role="no")
        return label(run)[0][lid(221)]

    def test_14_months_counts(self):
        r = self.strength("2025-07 new_tech_leader: new EVP and CITO Jason Estes (press)")
        self.assertEqual((r["account_strength"], r["action"]), ("Medium", "Account play"))

    def test_20_months_and_contraction_do_not(self):
        for sig in ("2025-01 new_tech_leader: new CIO (press)", "2026-06 contraction: layoffs (press)"):
            r = self.strength(sig)
            self.assertEqual(r["account_strength"], "Weak", sig)
            self.assertNotEqual(r["action"], "Drop", sig)  # hiring unknown is a gap, not a Drop


class MissingEvidenceNeverDrops(unittest.TestCase):
    """Drop only for a hard disqualifier or a confirmed absence of need."""

    def row(self, **facts):
        run = run_rb2b([rb2b(237, "Dan McLaughlin", "Federal Civilian Sales Director", "Cyera")])
        base = dict(company_key_final="cyera.com", domains="cyera.com", us_company="yes", employees_best="1550",
                    size_tier="B")
        company(run, "name:cyera", **dict(base, **facts))
        person(run, lid(237), works_there="likely", buyer_role="no", buyer_role_why="federal sales")
        return label(run)[0][lid(237)]

    def test_hiring_not_checked_goes_to_review(self):
        r = self.row(hiring_checked="not_checked")
        self.assertEqual((r["verdict"], r["action"]), ("Not qualified", "Review"))
        self.assertIn("GAP_HIRING_NOT_CHECKED", r["reason_codes"])
        self.assertIn("Hiring not checked", r["why"])
        self.assertIn("before deciding on an account play", r["next_step"])

    def test_unreadable_board_and_unknown_size_go_to_low_priority(self):
        r = self.row(hiring_checked="none_found", employees_best="1771", size_tier="C")
        self.assertEqual(r["action"], "Low priority")
        self.assertIn("GAP_HIRING_UNREAD", r["reason_codes"])

    def test_confirmed_absence_is_drop(self):
        r = self.row(hiring_checked="ats_api", open_roles_total="0", open_tech_roles="0", open_tech_roles_us="0")
        self.assertEqual((r["hiring_status"], r["action"]), ("No open roles found", "Drop"))

    def test_funding_signal_makes_it_an_account_play(self):
        r = self.row(hiring_checked="not_checked", need_signals="2026-06 funding: $540M Series G (press)")
        self.assertEqual((r["account_strength"], r["action"]), ("Medium", "Account play"))

    def test_hard_person_code_at_unresearched_company_still_drops(self):
        run = run_rb2b([rb2b(60, "William Cowart", "Cashier", "Chick Fil A Corporate Support Center")])
        r = label(run)[0][lid(60)]
        self.assertEqual((r["primary_code"], r["action"]), ("EXCLUDED_TITLE", "Drop"))

    def test_gate_catches_a_drop_on_missing_evidence(self):
        run = run_rb2b([rb2b(237, "Dan McLaughlin", "Federal Civilian Sales Director", "Cyera")])
        company(run, "name:cyera", company_key_final="cyera.com", us_company="yes", employees_best="1550",
                size_tier="B", hiring_checked="not_checked")
        label(run)
        rows = C.read_csv(C.work(run, "05-qualified.csv"))
        rows[0]["action"] = "Drop"
        C.write_csv(C.work(run, "05-qualified.csv"), rows, L.QUALIFIED_FIELDS)
        self.assertTrue(any("missing evidence" in f for f in checks.gate2(run).fails))


class ImportRule(unittest.TestCase):
    """New contacts only; owner = active company owner, else Jesse Kinzer."""

    def test(self):
        run = run_rb2b([rb2b(97, "Charlie Jacobson", "Co-Founder", "Pulley", email="charlie@withpulley.com")])
        company(run, "name:pulley", company_key_final="withpulley.com", domains="withpulley.com", **GOOD)
        person(run, lid(97), works_there="confirmed", buyer_role="yes")
        crm_company(run, "withpulley.com", hs_company_id="1", match_type="domain")
        crm_contact(run, lid(97), hs_contact_id="c1", match_type="email", email="charlie@withpulley.com",
                    contact_owner="Jonathan Gonzalez", contact_owner_active="yes")
        committee(run, "withpulley.com", order="1", full_name="Charlie Jacobson", email="charlie@withpulley.com",
                  email_risk="A", email_validated_at="2026-09-08", employer_domain="withpulley.com", lead_id=lid(97))
        committee(run, "withpulley.com", order="2", full_name="Chad Ackerman", title="Head of Design",
                  priority="Second wave", email="chad@withpulley.com", domain_accept_all="yes",
                  bounceban_result="deliverable", employer_domain="withpulley.com")
        C.write_csv(C.work(run, "07-crm-committee.csv"),
                    [{"company_key_final": "withpulley.com", "email": "charlie@withpulley.com", "checked": "yes", "hs_contact_id": "c1"},
                     {"company_key_final": "withpulley.com", "email": "chad@withpulley.com", "checked": "yes"}],
                    A.CRM_COMMITTEE_FIELDS)
        rows, _, tier1 = label(run)
        self.assertEqual(rows[lid(97)]["action"], "Contact now")
        quiet(L.run_label, run, None, True)
        quiet(A.main, ["--run", run])
        imp = C.read_csv(A.paths(run, C.load_run(run))[1])
        self.assertEqual([r["Email"] for r in imp], ["chad@withpulley.com"])
        self.assertEqual(imp[0]["Contact owner"], "Jesse Kinzer")
        self.assertIn("catch-all, deliverable per BounceBan", imp[0]["Priority"])


class Determinism(unittest.TestCase):
    def test_label_twice_is_identical(self):
        run = run_rb2b([rb2b(i, f"Person {i}", t, f"Co {i % 3}", email=f"p{i}@co{i % 3}.com")
                        for i, t in enumerate(["CTO", "Owner", "Recruiter", "Cashier", "", "VP Marketing"], start=1)])
        company(run, "name:co 0", company_key_final="co0.com", domains="co0.com", **GOOD)
        company(run, "name:co 1", company_key_final="co1.com", domains="co1.com", us_company="yes",
                employees_best="1771", size_tier="C")
        triage(run, "name:co 2", company_name="Co 2", employees_best="30", us_company="yes", triage="Drop",
               drop_code="CANNOT_BUY", why="tiny")
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            quiet(L.run_label, run, a)
            quiet(L.run_label, run, b)
            for n in ("05-qualified.csv", "05-company-rollup.csv", "06-tier1.csv"):
                self.assertTrue(filecmp.cmp(os.path.join(a, n), os.path.join(b, n), shallow=False), n)
        quiet(L.run_label, run)
        self.assertEqual(checks.gate7(run).fails, [])
        override(run, "company", "co0.com", "employees_best", "130")
        self.assertTrue(any("stale" in f for f in checks.gate7(run).fails))


if __name__ == "__main__":
    unittest.main()
