"""Tests for the 2026-09-28 fix round (reviewer R1 to R8, live test T1 to T10, minors).
One test per behavior change; names say which item they cover."""
import json
import os
import subprocess
import sys
import unittest

from helpers import (A, AS_OF, C, GOOD, L, SCRIPTS, classify, committee, company, crm_company, crm_contact,
                     label, lid, new_run, normalize, override, person, quiet, rb2b, run_csv, run_rb2b, triage)
import ats_count
import checks


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def norm_csv(text, *extra):
    d = new_run("ql-in-")
    p = os.path.join(d, "list.csv")
    write(p, text)
    run = new_run()
    return run, p, lambda *more: quiet(normalize.main, ["--run", run, "--adapter", "csv", "--input", p,
                                                        "--touch-type", "list_member", "--as-of", AS_OF, *extra, *more])


class R1Titles(unittest.TestCase):
    def test_buyer_titles(self):
        cases = {"Director of IT": "Primary: technology/product", "VP of IT": "Primary: technology/product",
                 "Director, IT": "Primary: technology/product", "Engineering Director": "Primary: technology/product",
                 "Product Director": "Primary: technology/product", "Technology Director": "Primary: technology/product",
                 "Director of Software Development": "Primary: technology/product",
                 "Head of Recruiting": "Primary: recruiting/people",
                 "Director of Strategy": "Primary: operations/transformation",
                 "Founding Engineer": "Secondary influencer", "Product Owner": "Secondary influencer",
                 "Executive Assistant to the CEO": "Excluded title", "Senior Recruiter, Agency": "Excluded title",
                 "Assistant Director of IT": "Primary: technology/product"}
        for t, g in cases.items():
            self.assertEqual(classify.classify_title(t)[0], g, t)

    def test_research_buyer_role_yes_beats_the_title_table(self):
        run = run_rb2b([rb2b(1, "Ann Lee", "Chief of Everything", "Acme", email="ann@acme.com")])
        company(run, "name:acme", company_key_final="acme.com", domains="acme.com", **GOOD)
        person(run, lid(1), works_there="confirmed", buyer_role="yes")
        rows = label(run)[0]
        self.assertNotIn("UNRELATED_TITLE", rows[lid(1)]["reason_codes"])


class R2TinyNeedsEvidence(unittest.TestCase):
    def row(self, **facts):
        run = run_rb2b([rb2b(2, "Bob Roe", "CEO", "Tinyco", email="bob@tinyco.com")])
        company(run, "name:tinyco", company_key_final="tinyco.com", domains="tinyco.com", us_company="yes",
                employees_best="8", employees_text="8", employees_source="LinkedIn", **facts)
        person(run, lid(2), works_there="confirmed", buyer_role="yes")
        return label(run)[0][lid(2)], run

    def test_hiring_not_checked_is_not_a_drop(self):
        r, run = self.row(size_tier="A", hiring_checked="not_checked")
        self.assertNotIn("TINY_NO_BUDGET", r["reason_codes"])
        self.assertNotEqual(r["action"], "Drop")
        self.assertEqual(checks.gate2(run).fails, [])

    def test_knowledge_size_is_not_a_drop(self):
        r, _ = self.row(size_tier="C", hiring_checked="ats_api", open_roles_total="0", open_tech_roles="0",
                        open_tech_roles_us="0")
        self.assertNotIn("TINY_NO_BUDGET", r["reason_codes"])

    def test_counted_and_checked_is_a_drop(self):
        r, run = self.row(size_tier="A", hiring_checked="ats_api", open_roles_total="0", open_tech_roles="0",
                          open_tech_roles_us="0")
        self.assertEqual((r["primary_code"], r["action"]), ("TINY_NO_BUDGET", "Drop"))
        self.assertEqual([f for f in checks.gate2(run).fails if "TINY" in f], [])


class R3SoftCodeAtLiveDeal(unittest.TestCase):
    def test(self):
        run = run_rb2b([rb2b(50, "Mia Sol", "Marketing Coordinator II", "Pulley", email="mia@withpulley.com"),
                        rb2b(51, "Ned Ash", "Accountant", "Pulley", email="ned@withpulley.com")])
        company(run, "name:pulley", company_key_final="withpulley.com", domains="withpulley.com", **GOOD)
        person(run, lid(50), works_there="confirmed")
        person(run, lid(51), works_there="confirmed", buyer_role="no")
        crm_company(run, "withpulley.com", hs_company_id="1", match_type="domain", owner_name="Kent Richeson",
                    owner_active="yes", open_deals="1", open_deal_summary="Q4 embedded team")
        rows = label(run)[0]
        self.assertEqual(rows[lid(51)]["action"], "Tell account owner")
        self.assertIn("Kent Richeson", rows[lid(51)]["next_step"])
        self.assertEqual(rows[lid(50)]["action"], "Drop")  # coordinator is a hard exclusion
        self.assertEqual([f for f in checks.gate2(run).fails if "Drop" in f], [])


class R4LedgerParallel(unittest.TestCase):
    def test_no_lost_rows(self):
        run = new_run()
        C.save_run(run, {"caps": C.DEFAULT_CAPS})
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        cmd = [sys.executable, os.path.join(SCRIPTS, "ledger.py"), "add", "--run", run, "--stage", "S6",
               "--vendor", "moltsets", "--endpoint", "x", "--charged", "1", "--result", "hit"]
        for _ in range(4):
            ps = [subprocess.Popen(cmd, stdout=subprocess.DEVNULL, env=env) for _ in range(5)]
            [p.wait() for p in ps]
        self.assertEqual(len(C.read_csv(os.path.join(run, "cost-ledger.csv"))), 20)


class R5NameOnlyOwner(unittest.TestCase):
    def test_import_owner_falls_back(self):
        run = run_rb2b([rb2b(10, "Eve Hill", "CTO", "Pulley", email="eve@withpulley.com")])
        company(run, "name:pulley", company_key_final="withpulley.com", domains="withpulley.com", **GOOD)
        person(run, lid(10), works_there="confirmed", buyer_role="yes", email_found="eve@withpulley.com",
               email_risk="A", email_validated_at="2026-09-01")
        crm_company(run, "withpulley.com", hs_company_id="99", match_type="name", owner_name="Kent Richeson",
                    owner_active="yes")
        crm_contact(run, lid(10), match_type="none")
        label(run)
        quiet(A.main, ["--run", run])
        imp = C.read_csv(A.paths(run, C.load_run(run))[1])
        self.assertEqual([r["Contact owner"] for r in imp], ["Jesse Kinzer"])


class R6Dates(unittest.TestCase):
    TEXT = "Name,Email,Company,Title,Registered\nAmy Ng,amy@foo.com,Foo,CTO,{a}\nBen Ox,ben@bar.com,Bar,CTO,{b}\n"

    def dates(self, a, b, *flags):
        run, _, go = norm_csv(self.TEXT.format(a=a, b=b))
        go(*flags)
        return [r["touch_date"] for r in C.read_csv(C.work(run, "01-canonical.csv"))]

    def test_month_first_inferred(self):
        self.assertEqual(self.dates("09/25/2026", "03/04/2026"), ["2026-09-25", "2026-03-04"])

    def test_flag_reads_ambiguous_dates(self):
        self.assertEqual(self.dates("03/04/2026", "05/06/2026", "--date-format", "mdy"), ["2026-03-04", "2026-05-06"])

    def test_ambiguous_or_mixed_stops(self):
        for a, b in (("03/04/2026", "05/06/2026"), ("25/09/2026", "09/25/2026"), ("2026-09-01", "03/04/2026")):
            with self.assertRaises(SystemExit):
                self.dates(a, b)

    def test_baserow_csv_export_is_refused(self):
        for text in ("Name,Title,Company Name,Last Seen At,Last Captured URL,Lead Type\nA B,CTO,X,2026-09-01,/,Buyer\n",
                     "Name,Title,First Seen At,Last Seen At,Referrer\nA B,CTO,03/09/2026,2026-09-21,x\n"):
            run, p, go = norm_csv(text)
            with self.assertRaises(SystemExit) as e:
                go()
            self.assertIn("JSON", str(e.exception))


class R7RepeatedIds(unittest.TestCase):
    def test_overlapping_pages(self):
        r = rb2b(7, "Jo Park", "CTO", "Acme")
        run = run_rb2b([r, dict(r)])
        self.assertEqual(len(C.read_csv(C.work(run, "01-canonical.csv"))), 1)
        dupes = C.read_csv(C.work(run, "01-dupes.csv"))
        self.assertEqual(dupes[0]["merge_key"], "repeat of the same record id")
        self.assertFalse([f for f in checks.gate1(run, "S2").fails if "source rows" in f])

    def test_same_file_name_in_two_folders(self):
        x, y = new_run("ql-x-"), new_run("ql-y-")
        write(os.path.join(x, "list.csv"), "Name,Email,Company,Title\nA One,a@a.com,A,CTO\n")
        write(os.path.join(y, "list.csv"), "Name,Email,Company,Title\nB Two,b@b.com,B,CTO\n")
        run = new_run()
        quiet(normalize.main, ["--run", run, "--adapter", "csv", "--input", os.path.join(x, "list.csv"),
                               os.path.join(y, "list.csv"), "--touch-type", "list_member", "--as-of", AS_OF])
        self.assertEqual(len(C.read_csv(C.work(run, "01-canonical.csv"))), 2)


class R8CompanyKeys(unittest.TestCase):
    def test_same_name_different_domains_split_and_shared_domain_is_only_flagged(self):
        run, _, go = norm_csv("Name,Email,Organisation,Position\nAna Ruiz,ana@acme.com,Acme,CTO\n"
                              "Raj Rao,raj@acme.io,Acme,VP Engineering\nNick Parker,nick@cvglobal.co,CV,CTO\n"
                              "Fabio Criales,fabio@cvglobal.co,CV Christian Vision,COO\n")
        go()
        canon = {r["full_name"]: r for r in C.read_csv(C.work(run, "01-canonical.csv"))}
        self.assertEqual(canon["Ana Ruiz"]["company_key"], "name:acme@acme.com")
        self.assertEqual(canon["Raj Rao"]["company_key"], "name:acme@acme.io")
        # different names are never merged on a shared email domain (it may be stale): flagged instead
        self.assertEqual(canon["Nick Parker"]["company_key"], "name:cv")
        self.assertEqual(canon["Fabio Criales"]["company_key"], "name:cv christian vision")
        self.assertIn("cvglobal.co", canon["Nick Parker"]["key_note"])


class Minors(unittest.TestCase):
    def test_unicode_company_names_are_kept(self):
        self.assertEqual(C.norm_company_name("Café Ñu"), "cafe nu")
        self.assertEqual(C.norm_company_name("华为"), "华为")
        self.assertEqual(C.norm_company_name("JPMorgan Chase & Co."), "jpmorgan chase")
        run, _, go = norm_csv("Name,Email,Company,Title\nLi Wei,li@huawei.cn,华为,CTO\n")
        go()
        r = C.read_csv(C.work(run, "01-canonical.csv"))[0]
        self.assertEqual((r["company_name_raw"], r["company_key"]), ("华为", "name:华为"))

    def test_ats_us_detection(self):
        self.assertFalse(ats_count.is_us("Toronto, ON, CA", False, True))
        self.assertTrue(ats_count.is_us("San Francisco, CA", False, True))
        self.assertTrue(ats_count.is_us("Wilmington, DE", False, True))
        self.assertFalse(ats_count.is_us("Remote - Americas", False, False))
        self.assertTrue(ats_count.is_us("2 Locations", False, True))
        self.assertFalse(ats_count.is_us("2 Locations", False, False))

    def test_label_needs_as_of(self):
        run = run_rb2b([rb2b(4, "Dee Fox", "CTO", "Sigco")])
        d = C.load_run(run)
        d.pop("as_of")
        C.save_run(run, d)
        with self.assertRaises(SystemExit):
            quiet(L.run_label, run)

    def test_packet_name_has_no_path_characters(self):
        self.assertEqual(C.packet_name("AC/DC: Tours"), "AC DC Tours - Lead Packet.md")

    def test_campaign_wording(self):
        run, p, go = norm_csv("Name,Email,Company,Title\nA B,a@x.com,X,CTO\n")
        quiet(normalize.main, ["--run", run, "--adapter", "csv", "--input", p, "--touch-type", "event_attended",
                               "--campaign", "Fall Summit", "--as-of", AS_OF])
        quiet(classify.main, ["--run", run])
        self.assertTrue(C.read_csv(C.work(run, "02-pass1.csv"))[0]["intent_phrase"].startswith("Attended Fall Summit"))


class T1Tier1Size(unittest.TestCase):
    def test_smaller_tier1_scaled_budget_and_skip_state(self):
        rs = [rb2b(20 + i, f"P{i} Q", "CTO", f"Co{i}", email=f"p@co{i}.com") for i in range(4)]
        run = run_rb2b(rs)
        for i in range(4):
            company(run, f"name:co{i}", company_key_final=f"co{i}.com", domains=f"co{i}.com", **GOOD)
            person(run, lid(20 + i), works_there="confirmed", buyer_role="yes", email_found=f"p@co{i}.com",
                   email_risk="A", email_validated_at="2026-09-01")
        C.save_run(run, dict(C.load_run(run), caps={"deepline": [1.0, "credit"], "hirebase": [25.0, "credit"],
                                                    "moltsets": [9.0, "token"]}))
        _, _, tier1 = quiet(L.run_label, run, None, False, None, 2)
        self.assertEqual(C.load_run(run)["tier1_max"], 2)
        # 4 Contact now companies: all stay (and label.py says stop and ask), projections scale to the caps
        self.assertEqual(float(tier1[0]["projected_deepline"]), 0.25)
        C.write_csv(C.work(run, "06-enrich-skipped.csv"),
                    [{"company_key_final": t["company_key_final"], "reason": "budget"} for t in tier1],
                    ["company_key_final", "reason"])
        g = checks.gate1(run, "S6")
        self.assertFalse([f for f in g.fails if "packet" in f or "committee" in f])
        self.assertTrue(any("enrichment skipped" in w for w in g.warns))


class T2Caps(unittest.TestCase):
    def test_caps_command_logs_the_change(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme")])
        quiet(__import__("ledger").main, ["caps", "--run", run, "--deepline", "2", "--approved-by", "JK"])
        self.assertEqual(C.load_run(run)["caps"]["deepline"][0], 2.0)
        with open(C.work(run, "00-run-log.md"), encoding="utf-8") as f:
            self.assertIn("approved by JK", f.read())


class T3NewSinceLastRun(unittest.TestCase):
    def test_timestamp_since_and_exclude_prior(self):
        rows = [rb2b(1, "A B", "CTO", "Acme", seen="2026-09-25T19:41:04Z"),
                rb2b(2, "C D", "CTO", "Beta", seen="2026-09-25T20:00:00Z"),
                rb2b(3, "E F", "CTO", "Gamma", seen="2026-09-26T08:00:00Z")]
        src = os.path.join(new_run("ql-in-"), "rows.json")
        write(src, json.dumps(rows))
        run = new_run()
        quiet(normalize.main, ["--run", run, "--adapter", "rb2b-baserow", "--input", src, "--as-of", AS_OF,
                               "--since", "2026-09-25T19:41:05Z"])
        self.assertEqual({r["lead_id"] for r in C.read_csv(C.work(run, "01-canonical.csv"))}, {lid(2), lid(3)})
        run2 = new_run()
        quiet(normalize.main, ["--run", run2, "--adapter", "rb2b-baserow", "--input", src, "--as-of", AS_OF,
                               "--exclude-prior", run])
        self.assertEqual({r["lead_id"] for r in C.read_csv(C.work(run2, "01-canonical.csv"))}, {lid(1)})
        self.assertEqual(C.load_run(run2)["excluded_prior"], 2)

    def test_prior_dir_skips_test_runs(self):
        root = new_run("ql-prior-")
        t = os.path.join(root, "2026-09-28 qualify-leads test run", "x")
        os.makedirs(t)
        C.write_csv(os.path.join(t, "old.csv"), [{"company": "Pulley", "domain": "pulley.com"}], ["company", "domain"])
        self.assertEqual(classify.build_prior(root), [])


class T5LabelFixes(unittest.TestCase):
    def test_not_us_is_not_also_unknown(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme")])
        company(run, "name:acme", **dict(GOOD, us_company="no"))
        r = label(run)[0][lid(1)]
        self.assertEqual(r["primary_code"], "NOT_US")
        self.assertNotIn("INS_US_UNKNOWN", r["reason_codes"])

    def test_wrong_domain_without_research_domains(self):
        run = run_rb2b([rb2b(605, "Capri Smith", "CEO", "Pri Del Rey", email="capri@rainbowshops.com",
                             website="https://pridelrey.com")])
        company(run, "name:pri del rey", us_company="yes", employees_best="1", size_tier="A")
        self.assertEqual(label(run)[0][lid(605)]["email_status"], "Wrong domain")

    def test_need_text_cuts_at_a_word(self):
        self.assertEqual(L.clip("2026-01 funding: $28M strategic round led by Ten Eleven Ventures", 40),
                         "2026-01 funding: $28M strategic round")

    def test_sources_capped_at_300(self):
        long = "; ".join(f"https://example.com/{'a' * 90}{i}" for i in range(4))
        out = A.cap_sources(long)
        self.assertLessEqual(len(out), 300)
        self.assertEqual(out.count("https://"), 2)  # whole URLs only, never a cut one
        self.assertTrue(out.endswith("1"))

    def test_rank_puts_strength_before_verdict(self):
        run = run_rb2b([rb2b(603, company="Great Clips"),
                        rb2b(596, "Chris Morris", "Therapy Specialist", "Mainstay")])
        company(run, "name:great clips", company_key_final="greatclips.com", **dict(GOOD, open_tech_roles_us="1",
                open_tech_roles="1"))
        company(run, "name:mainstay", company_key_final="mainstaymedical.com", **GOOD)
        person(run, lid(596), works_there="likely", buyer_role="no")
        rows = label(run)[0]
        self.assertEqual(rows[lid(596)]["account_strength"], "Strong")
        self.assertLess(int(rows[lid(596)]["rank"]), int(rows[lid(603)]["rank"]))

    def test_reason_text_uses_the_number_and_never_cuts_a_sentence(self):
        run = run_rb2b([rb2b(597, "K R", "Sales", "Knock"), rb2b(594, company="Project Return")])
        company(run, "name:knock", us_company="yes", employees_best="45", employees_text="Knock unit small; parent large",
                size_tier="A", can_buy="no")
        triage(run, "name:project return", company_name="Project Return Peer Support Network", employees_best="40",
               us_company="yes", triage="Drop", drop_code="STRUCTURAL_NO_NEED",
               why="County funded peer support nonprofit with no tech, product, or design need, and no software budget of any kind")
        rows = label(run)[0]
        self.assertIn("(about 45 people)", rows[lid(597)]["why"])
        self.assertTrue(rows[lid(594)]["why"].endswith("nonprofit with no tech."))


class T6Boards(unittest.TestCase):
    def test_workable_and_adp_parsers(self):
        wk = {"jobs": [{"title": "Senior Software Engineer", "locations": [{"city": "New York", "region": "New York",
                                                                          "country": "United States"}]},
                       {"title": "Data Engineer", "locations": [{"city": "Cape Town", "country": "South Africa"}]}]}
        r = ats_count.count("workable", wk)
        self.assertEqual((r["open_tech_roles"], r["open_tech_roles_us"]), (2, 1))
        adp = {"jobRequisitions": [{"requisitionTitle": "Software Developer",
                                    "requisitionLocations": [{"nameCode": {"shortName": " Omaha, NE, US"}}]}]}
        self.assertEqual(ats_count.count("adp", adp)["open_tech_roles_us"], 1)

    def test_bad_board_is_not_checked_not_a_crash(self):
        out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "ats_count.py"), "--ats", "ashby", "--file",
                              "/nonexistent/board.json"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(json.loads(out.stdout)["hiring_checked"], "not_checked")


class T8OneEmailStatus(unittest.TestCase):
    def test_committee_status_matches_the_csv_and_bounceban_file(self):
        run = run_rb2b([rb2b(9, "Andrew Jebasingh", "CEO", "SiteVue", email="")])
        company(run, "name:sitevue", company_key_final="sitevue.ai", domains="sitevue.ai", **GOOD)
        person(run, lid(9), works_there="confirmed", buyer_role="yes")
        crm_contact(run, lid(9), hs_contact_id="1", match_type="name", email="andrew@sitevue.ai",
                    contact_owner="Jonathan Gonzalez", contact_owner_active="yes")
        committee(run, "sitevue.ai", order="1", full_name="Andrew Jebasingh", email="andrew@sitevue.ai",
                  email_risk="A", email_validated_at="2026-09-01", employer_domain="sitevue.ai", lead_id=lid(9))
        committee(run, "sitevue.ai", order="2", full_name="Markus Hay", email="markus@sitevue.ai",
                  domain_accept_all="yes", bounceban_result="pending", employer_domain="sitevue.ai")
        C.write_csv(C.work(run, "07-bounceban.csv"), [{"email": "markus@sitevue.ai", "bounceban_result": "deliverable"}],
                    A.BOUNCEBAN_FIELDS)
        rows = label(run)[0]
        ctx, facts = A.company_context(run)
        m = {x["full_name"]: x for x in A.committee_status(run, C.parse_date(AS_OF), ctx, facts)}
        self.assertEqual(m["Andrew Jebasingh"]["email_status"], rows[lid(9)]["email_status"])
        self.assertEqual(m["Andrew Jebasingh"]["email_status"], "From HubSpot")
        self.assertEqual(m["Markus Hay"]["email_status"], "Verified, catch-all domain")

    def test_ledger_accepts_pending(self):
        run = new_run()
        C.save_run(run, {"caps": C.DEFAULT_CAPS})
        rc = quiet(__import__("ledger").main, ["add", "--run", run, "--stage", "S6", "--vendor", "deepline",
                                               "--endpoint", "bounceban_verify_bulk", "--charged", "0.3",
                                               "--result", "pending"])
        self.assertEqual(rc, 0)


class T9Rules(unittest.TestCase):
    def test_msp_is_a_peer_vendor_unless_confirmed_recruiting_buyer(self):
        run = run_rb2b([rb2b(1, "Avion Bryant", "Senior Network Engineer", "Stronghold Data"),
                        rb2b(2, "Zach Bishop", "Director of Talent Acquisition", "Stronghold Data")])
        company(run, "name:stronghold data", company_key_final="strongholddata.com", sells_staffing_or_dev="yes",
                sells_why="Joplin MSP and Microsoft stack development", **GOOD)
        person(run, lid(1), works_there="confirmed", buyer_role="no")
        person(run, lid(2), works_there="confirmed", buyer_role="yes")
        rows = label(run)[0]
        self.assertEqual(rows[lid(2)]["primary_code"], "COMPETITOR_STAFFING")  # default: excluded
        override(run, "company", "strongholddata.com", "peer_buys_recruiting", "yes")
        rows = label(run)[0]
        self.assertNotIn("COMPETITOR_STAFFING", rows[lid(2)]["reason_codes"])  # confirmed recruiting buyer
        self.assertIn("COMPETITOR_STAFFING", rows[lid(1)]["reason_codes"])      # not a buyer: still a peer vendor

    def test_systems_engineer_is_not_a_tech_role(self):
        rx = C.tech_role_regex()
        self.assertIsNone(rx.search("Systems Engineer (Product Development)"))
        self.assertIsNotNone(rx.search("Software Systems Engineer"))

    def test_engineering_leader_is_not_ambiguous(self):
        self.assertEqual(classify.classify_title("Director of Engineering")[2], "no")
        self.assertEqual(classify.classify_title("Systems Engineer")[2], "yes")

    def test_hiring_sources(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Omega"), rb2b(2, "C D", "CTO", "Delta")])
        company(run, "name:omega", **dict(GOOD, hiring_checked="hirebase", open_roles_total="", open_tech_roles="",
                                          open_tech_roles_us=""))
        company(run, "name:delta", **dict(GOOD, hiring_checked="linkedin_jobs", open_roles_total="0",
                                          open_tech_roles="0", open_tech_roles_us="0"))
        rows = label(run)[0]
        self.assertEqual((rows[lid(1)]["hiring_status"], rows[lid(1)]["open_tech_roles_display"]),
                         ("Unknown", "Hirebase: no match"))
        self.assertEqual(rows[lid(2)]["hiring_status"], "No open roles found")

    def test_big_parent_is_an_open_item_not_a_drop(self):
        run = run_rb2b([rb2b(482, "Jack Anderson", "Director of Engineering", "Rocket Money")])
        company(run, "name:rocket money", **dict(GOOD, parent_name="Rocket Companies", parent_employees="14000",
                                                 parent_centralized="yes"))
        person(run, lid(482), works_there="confirmed", buyer_role="yes")
        r = label(run)[0][lid(482)]
        self.assertEqual((r["verdict"], r["primary_code"], r["action"]), ("Possible match", "OPEN_PARENT", "Review"))


class T10Lows(unittest.TestCase):
    def test_social_gaps_not_profiled_and_known_large_goes_to_triage(self):
        d = new_run("ql-in-")
        p = os.path.join(d, "leads.csv")
        fields = ["name", "title", "company", "linkedinUrl", "reactions", "comments", "replies", "distinctPosts",
                  "distinctExecs", "lastSeenAt"]
        C.write_csv(p, [dict(name="Kim Yu", title="VP Engineering", company="JPMorgan Chase & Co.",
                             linkedinUrl="https://linkedin.com/in/kimyu", reactions="1", lastSeenAt="2026-08-11"),
                        dict(name="Lee Ho", title="CTO", company="Acme", linkedinUrl="https://linkedin.com/in/leeho",
                             reactions="1", lastSeenAt="2026-08-24")], fields)
        run = new_run()
        quiet(normalize.main, ["--run", run, "--adapter", "social", "--input", p, "--as-of", AS_OF])
        quiet(classify.main, ["--run", run])
        self.assertEqual(C.load_run(run)["profile"]["zero_days"], [])
        comp = {c["company_key"]: c for c in C.read_csv(C.work(run, "02-companies.csv"))}
        self.assertEqual(comp["name:jpmorgan chase"]["triage_first"], "yes")


class ShipFixes(unittest.TestCase):
    """Final integration round, items 1 to 9."""

    def test_1_linkedin_jobs_passes_gate_2(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Delta")])
        company(run, "name:delta", **dict(GOOD, hiring_checked="linkedin_jobs"))
        label(run)
        self.assertFalse([f for f in checks.gate2(run).fails if "hiring_checked" in f])

    def test_2_social_rows_without_linkedin_keep_distinct_ids_across_exports(self):
        d = new_run("ql-in-")
        fields = ["name", "title", "company", "linkedinUrl", "reactions", "lastSeenAt"]
        for n, who in (("a.csv", "Jo Park"), ("b.csv", "Al Chu")):
            C.write_csv(os.path.join(d, n), [dict(name=who, title="CTO", company="Acme", reactions="1",
                                                  lastSeenAt="2026-09-02")], fields)
        run = new_run()
        quiet(normalize.main, ["--run", run, "--adapter", "social", "--input", os.path.join(d, "a.csv"),
                               os.path.join(d, "b.csv"), "--as-of", AS_OF])
        self.assertEqual(len(C.read_csv(C.work(run, "01-canonical.csv"))), 2)

    def test_3_stale_domain_never_rekeys_and_no_email_row_joins_the_name(self):
        run, _, go = norm_csv("Name,Email,Company,Title\nPat Lee,pat@oldco.com,Acme Robotics,CTO\n"
                              "Sam Ray,sam@oldco.com,OldCo,CTO\nKim Yu,kim@acme.com,Acme,CTO\nLee Ho,,Acme,COO\n"
                              "Ann Fox,ann@beta.com,Beta,CTO\nBo Gray,bo@beta.io,Beta,CEO\nCy Dunn,,Beta,CFO\n")
        go()
        c = {r["full_name"]: r for r in C.read_csv(C.work(run, "01-canonical.csv"))}
        self.assertEqual(c["Pat Lee"]["company_key"], "name:acme robotics")
        self.assertIn("oldco.com", c["Pat Lee"]["key_note"])
        self.assertEqual(c["Lee Ho"]["company_key"], c["Kim Yu"]["company_key"])  # one domain: joins the name
        self.assertEqual(c["Cy Dunn"]["company_key"], "name:beta")                 # split name: stays, flagged
        self.assertIn("several domains", c["Cy Dunn"]["key_note"])
        quiet(classify.main, ["--run", run])
        comp = {x["company_key"]: x for x in C.read_csv(C.work(run, "02-companies.csv"))}
        self.assertIn("oldco.com", comp["name:acme robotics"]["collision_flag"])
        _, roll, _ = label(run)
        self.assertTrue(any("oldco.com" in x["collision"] for x in roll if x["company_key_final"] == "name:acme robotics"))

    def test_4_paid_sources_say_likely(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme", page="https://midwestern.com/survey",
                             referrer="https://l.facebook.com/"),
                        rb2b(2, "C D", "CTO", "Beta", referrer="https://syndicatedsearch.goog/")])
        p = {r["lead_id"]: r["intent_phrase"] for r in C.read_csv(C.work(run, "02-pass1.csv"))}
        self.assertIn("from Facebook, likely an ad", p[lid(1)])
        self.assertEqual(p[lid(2)], "Arrived from Google search partners (likely an ad) at the homepage")
        self.assertFalse(any("Clicked" in x for x in p.values()))

    def test_5_budget_below_plan_warns_in_label_and_ledger(self):
        rs = [rb2b(20 + i, f"P{i} Q", "CTO", f"Co{i}", email=f"p@co{i}.com") for i in range(4)]
        run = run_rb2b(rs)
        for i in range(4):
            company(run, f"name:co{i}", company_key_final=f"co{i}.com", domains=f"co{i}.com", **GOOD)
            person(run, lid(20 + i), works_there="confirmed", buyer_role="yes", email_found=f"p@co{i}.com",
                   email_risk="A", email_validated_at="2026-09-01")
        C.save_run(run, dict(C.load_run(run), caps={"deepline": [1.0, "credit"], "hirebase": [25.0, "credit"],
                                                    "moltsets": [60.0, "token"]}))
        quiet(L.run_label, run)
        short = C.load_run(run)["budget_short"]
        self.assertTrue(short and short[0].startswith("deepline"))
        out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "ledger.py"), "check", "--run", run,
                              "--vendor", "deepline", "--projected", "0.25"], capture_output=True, text=True)
        self.assertIn("below plan", out.stdout)

    def test_5b_default_caps_fit_a_full_tier1_without_warning(self):
        roll = [{"company_key_final": f"co{i}.com", "company_name": f"Co{i}", "best_action": "Contact now",
                 "account_strength": "Strong", "tech_roles_all": "3", "best_intent": "Low",
                 "freshest_need_days": 9999, "crm_state": "not_found", "newest_touch": ""} for i in range(8)]
        tier1, over, short = L.select_tier1(roll, caps=C.DEFAULT_CAPS)
        self.assertEqual((len(tier1), over, short), (8, False, []))
        self.assertEqual((tier1[0]["projected_deepline"], tier1[0]["projected_moltsets"]), ("1.25", "7.50"))

    def test_6_tier1_max_ceiling(self):
        run = run_rb2b([rb2b(1, "A B", "CTO", "Acme")])
        with self.assertRaises(SystemExit):
            quiet(L.run_label, run, None, False, None, 9)

    def test_7_exclude_prior_needs_a_folder_and_all_excluded_stops(self):
        src = os.path.join(new_run("ql-in-"), "rows.json")
        write(src, json.dumps([rb2b(1, "A B", "CTO", "Acme")]))
        base = ["--adapter", "rb2b-baserow", "--input", src, "--as-of", AS_OF]
        with self.assertRaises(SystemExit):
            quiet(normalize.main, ["--run", new_run()] + base + ["--exclude-prior"])
        first = new_run()
        quiet(normalize.main, ["--run", first] + base)
        with self.assertRaises(SystemExit) as e:
            quiet(normalize.main, ["--run", new_run()] + base + ["--exclude-prior", first])
        self.assertIn("already in the prior run", str(e.exception))

    def test_8_two_digit_years_stop(self):
        run, _, go = norm_csv("Name,Email,Company,Title,Registered\nAmy Ng,amy@foo.com,Foo,CTO,9/25/26\n")
        with self.assertRaises(SystemExit) as e:
            go("--date-format", "mdy")
        self.assertIn("two-digit years", str(e.exception))

    def test_9_structural_no_need_needs_a_business_model_reason(self):
        self.assertTrue(L.structural_reason_ok("Museum; no software product; IT run by an outside vendor"))
        self.assertFalse(L.structural_reason_ok("No tech hiring need found"))
        self.assertFalse(L.structural_reason_ok("Accounting firm with no tech hiring need found"))
        self.assertFalse(L.structural_reason_ok(""))


if __name__ == "__main__":
    unittest.main()
