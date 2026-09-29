#!/usr/bin/env python3
"""Render an exec content idea bank (markdown + CSVs) from one data source, then lint it.

Usage:
  python3 build_bank.py init  <project_dir> --exec "Matt Johnson"   # scaffold .build/
  python3 build_bank.py build <project_dir>                          # render + lint

Data lives in <project_dir>/.build/ (dot folder, hidden from Obsidian):
  config.json  person name ("exec"), channels, audience label, project link, source
               shortcodes, pillars, lead magnets, top 20, banned words
  ideas.txt    one block per idea (format below); edit this, never the rendered tables
  prose.md     the note's prose with placeholders the build fills in:
               {{STAGE_MIX}} {{PILLARS}} {{LEAD_MAGNETS}} {{TOP20}} {{IDEA_BANK}}

ideas.txt format:
  #P P1                 start pillar P1 (must exist in config.pillars)
  @ short-key           start an idea; key is stable, referenced by config.top20
  T: topic
  I: post idea (what it teaches or shows)
  H: LinkedIn hook (first line, real copy)
  G: Instagram angle (format + angle); omit when config.channels has no "instagram"
  S: Give | Proof | Belief | Ask
  C: none | ps LM-01 | ask LM-01      (ask = comment/DM keyword CTA; ps = soft P.S.)
  V: service (must be in config.services)
  R: source, may use shortcodes from config.sources, e.g. {M} all-hands 2026-09-11

IDs are assigned by order inside each pillar (P1-01, P1-02...). Once a bank is shared,
append new ideas at the END of a pillar so published IDs never shift.

Exit code 1 on hard failures (schema, dashes, banned words, broken references).
Trope-pattern hits are printed as warnings for a human or reviewer to judge.
"""
import collections, csv, json, os, re, sys

STAGES = ("Give", "Proof", "Belief", "Ask")
TARGET = {"Give": 60, "Proof": 20, "Belief": 12, "Ask": 8}
COLS = ["ID", "Topic", "Post idea", "LinkedIn hook (first line)", "Instagram angle",
        "Stage", "Lead magnet / CTA", "Service", "Source"]
LMH = ["ID", "Name (keyword)", "Hormozi type", "What it is", "Buyer problem it solves",
       "Bigger problem it reveals", "Service", "Build effort", "Status", "Source"]
LM_FIELDS = ["id", "name", "keyword", "type", "what", "problem", "reveals",
             "service", "effort", "status", "source"]
TROPES = [r"didn't [^.;]*; ", r"; you have", r"isn't [^.;]*, it's", r"\bnot about\b",
          r"Here's the thing", r"Let that sink in", r"game[- ]changer", r"\bdelve\b",
          r"You're right to", r"That instinct is right", r"in today's fast-paced"]
DEFAULT_BANNED = ["broker", "staffing firm"]

CONFIG_SKELETON = {
    "exec": "PERSON NAME",
    "channels": ["linkedin", "instagram"],
    "audience_label": "buyer",
    "project_link": "[[00 - readme]]",
    "note_title": "01 - Content Idea Bank",
    "date": "YYYY-MM-DD",
    "tags": ["content-strategy", "executive-social", "linkedin", "instagram"],
    "services": ["Scoped", "Embedded", "Recruiting", "Brand"],
    "banned": DEFAULT_BANNED,
    "banned_allow": ["30 days"],
    "sources": {
        "{A}": "[[01 - LinkedIn Audit]]",
        "{V}": "[[02 - Vault Themes and Assets]]",
        "{M}": "[[03 - Meetings - Exec Voice]]",
        "{S}": "[[04 - Sales Calls - Buyer Pain]]",
        "{K}": "[[05 - Slack Mining]]"
    },
    "pillars": [
        {"id": "P1", "name": "", "promise": "", "why": "", "evidence": "", "service": ""}
    ],
    "lead_magnets": [
        {"id": "LM-01", "name": "", "keyword": "", "type": "Reveal a problem (tool)",
         "what": "", "problem": "", "reveals": "", "service": "", "effort": "Low",
         "status": "Net-new", "source": ""}
    ],
    "top20": [{"key": "", "why": ""}]
}

PROSE_SKELETON = """## How to use this

(Hormozi method in 4 bullets; how the social team picks from the bank.)

{{STAGE_MIX}}

## What the research says

(8-12 cited bullets.)

## Content pillars

{{PILLARS}}

## Lead magnet catalog

{{LEAD_MAGNETS}}

## Start here: top 20

{{TOP20}}

## The idea bank

{{IDEA_BANK}}

## Recurring series

## Profile fixes

## Guardrails and open questions
"""


def die(errors):
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)


def init(proj, exec_name):
    b = os.path.join(proj, ".build")
    os.makedirs(b, exist_ok=True)
    cfg = dict(CONFIG_SKELETON, exec=exec_name)
    for name, body in (("config.json", json.dumps(cfg, indent=2) + "\n"),
                       ("prose.md", PROSE_SKELETON),
                       ("ideas.txt", "#P P1\n\n@ example-key\nT: \nI: \nH: \nG: \nS: Give\nC: none\nV: Brand\nR: \n")):
        p = os.path.join(b, name)
        if os.path.exists(p):
            print("exists, skipped:", p)
            continue
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        print("wrote", p)


def parse_ideas(path):
    rows, pillar, cur = [], None, None
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if line.startswith("#P "):
                pillar = line[3:].strip()
            elif line.startswith("@ "):
                cur = {"pillar": pillar, "key": line[2:].strip(), "line": n}
                rows.append(cur)
            else:
                m = re.match(r"^([TIHGSCVR]): ?(.*)$", line)
                if m and cur is not None:
                    cur[m.group(1)] = m.group(2).strip()
    return rows


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def build(proj):
    b = os.path.join(proj, ".build")
    cfg = json.load(open(os.path.join(b, "config.json"), encoding="utf-8"))
    prose = open(os.path.join(b, "prose.md"), encoding="utf-8").read()
    rows = parse_ideas(os.path.join(b, "ideas.txt"))
    errors, warnings = [], []

    pillars = collections.OrderedDict((p["id"], p) for p in cfg["pillars"])
    lms = collections.OrderedDict((l["id"], l) for l in cfg["lead_magnets"])
    srcmap = cfg.get("sources", {})
    services = set(cfg["services"])
    ig = "instagram" in [c.lower() for c in cfg.get("channels", ["linkedin", "instagram"])]
    required = "TIHGSCVR" if ig else "TIHSCVR"
    cols = COLS if ig else [c for c in COLS if c != "Instagram angle"]

    def src(s):
        for k, v in srcmap.items():
            s = s.replace(k, v)
        return s

    counters, keys, used_lms = collections.Counter(), {}, set()
    for r in rows:
        where = f"ideas.txt line {r['line']} ({r['key']})"
        missing = [f for f in required if not r.get(f)]
        if missing:
            errors.append(f"{where}: missing or empty fields {missing}")
            continue
        if r["pillar"] not in pillars:
            errors.append(f"{where}: pillar {r['pillar']} not in config")
        if r["S"] not in STAGES:
            errors.append(f"{where}: stage {r['S']!r} not in {STAGES}")
        if r["V"] not in services:
            errors.append(f"{where}: service {r['V']!r} not in config.services")
        if r["key"] in keys:
            errors.append(f"{where}: duplicate key")
        c = r["C"].split()
        if c == ["none"]:
            r["CTA"] = "None (pure give)"
        elif len(c) == 2 and c[0] in ("ask", "ps") and c[1] in lms:
            kw = lms[c[1]]["keyword"]
            used_lms.add(c[1])
            r["CTA"] = (f"{c[1]}: comment {kw}" + (f" (IG: DM {kw})" if ig else "") if c[0] == "ask"
                        else f"{c[1]} as a soft P.S. ({kw})")
        else:
            errors.append(f"{where}: bad CTA {r['C']!r} (use none | ps LM-xx | ask LM-xx with an LM in config)")
            r["CTA"] = r["C"]
        if r["S"] == "Ask" and not r["C"].startswith("ask"):
            errors.append(f"{where}: Ask stage needs an 'ask LM-xx' CTA")
        counters[r["pillar"]] += 1
        r["ID"] = f"{r['pillar']}-{counters[r['pillar']]:02d}"
        r["SRC"] = src(r["R"])
        keys[r["key"]] = r
        for fld in ("T", "I", "H", "G", "SRC", "CTA"):
            if "|" in r.get(fld, ""):
                errors.append(f"{where}: pipe character in {fld} breaks the table")
    if errors:
        die(errors)

    for lid in lms:
        if lid not in used_lms:
            warnings.append(f"lead magnet {lid} is never referenced by an idea")

    total = len(rows)
    stage = collections.Counter(r["S"] for r in rows)
    pct = lambda n: round(100 * n / total) if total else 0
    for s in STAGES:
        if abs(pct(stage[s]) - TARGET[s]) > 6:
            warnings.append(f"stage mix: {s} is {pct(stage[s])}% (target {TARGET[s]}%)")

    stage_mix = (f"**Stage mix.** Every idea carries a Stage. Target: 60% Give, 20% Proof, 12% Belief, 8% Ask. This bank holds "
                 + ", ".join(f"{stage[s]} {s} ({pct(stage[s])}%)" for s in STAGES[:-1])
                 + f", and {stage['Ask']} Ask ({pct(stage['Ask'])}%), {total} ideas in all.")
    pillar_tbl = md_table(["#", "Pillar", f"Promise to the {cfg.get('audience_label', 'buyer')}", f"Why {cfg['exec'].split()[0]} can own it", "Evidence", "Leads to"],
                          [[p["id"], p["name"], p["promise"], p["why"], src(p["evidence"]), p["service"]] for p in pillars.values()])
    lm_rows = [[l["id"], f"{l['name']} ({l['keyword']})", l["type"], l["what"], l["problem"],
                l["reveals"], l["service"], l["effort"], l["status"], src(l["source"])] for l in lms.values()]
    lm_tbl = md_table(LMH, lm_rows)

    top_lines = []
    for i, t in enumerate(cfg.get("top20", []), 1):
        if t["key"] not in keys:
            die([f"top20 key {t['key']!r} not found in ideas.txt"])
        r = keys[t["key"]]
        top_lines.append(f"{i}. **{r['ID']}** {r['T']} ({r['S']}): {t['why']}")
    tstage = collections.Counter(keys[t["key"]]["S"] for t in cfg.get("top20", []))
    top_lines.append("\nMix: " + ", ".join(f"{tstage[s]} {s}" for s in STAGES) + ".")

    def cells(r):
        c = [r["ID"], r["T"], r["I"], r["H"], r.get("G", ""), r["S"], r["CTA"], r["V"], r["SRC"]]
        return c if ig else c[:4] + c[5:]
    bank = [f"{total} ideas across {len(pillars)} tables. Per pillar: "
            + ", ".join(f"{pid} {counters[pid]}" for pid in pillars) + "."]
    for pid, p in pillars.items():
        bank.append(f"\n### {pid}: {p['name']}\n")
        bank.append(md_table(cols, [cells(r) for r in rows if r["pillar"] == pid]))

    body = (prose.replace("{{STAGE_MIX}}", stage_mix).replace("{{PILLARS}}", pillar_tbl)
                 .replace("{{LEAD_MAGNETS}}", lm_tbl).replace("{{TOP20}}", "\n".join(top_lines))
                 .replace("{{IDEA_BANK}}", "\n".join(bank)))
    left = re.findall(r"\{\{[A-Z_0-9]+\}\}", body)
    if left:
        warnings.append(f"unfilled placeholders: {left}")
    front = "---\ntags:\n" + "".join(f"  - {t}\n" for t in cfg["tags"]) + \
            f"type: reference\nstatus: draft\nproject: \"{cfg.get('project_link', '[[00 - readme]]')}\"\ndate: {cfg['date']}\n---\n\n"
    md = front + body.strip() + "\n"

    # ---- lint the rendered note ----
    hard = []
    if re.search("[—–]", md):
        hard.append(f"em/en dashes found: {len(re.findall('[—–]', md))}")
    if re.search("[“”‘’]", md):
        warnings.append("curly quotes found (fine in Obsidian, but keep one style)")
    for word in cfg.get("banned", DEFAULT_BANNED):
        for m in re.finditer(re.escape(word), md, re.I):
            line = md[md.rfind("\n", 0, m.start()) + 1: md.find("\n", m.end())]
            if not any(a.lower() in line.lower() for a in ("never", "do not", "don't", "avoid")):
                hard.append(f"banned word {word!r} in line: {line[:160]}")
    for pat in TROPES:
        for m in re.finditer(pat, md, re.I):
            warnings.append(f"trope {pat!r}: ...{md[max(0, m.start() - 50): m.end() + 50].replace(chr(10), ' ')}...")
    for a in cfg.get("banned_allow", []):
        n = len(re.findall(re.escape(a), md))
        if n:
            warnings.append(f"{a!r} appears {n}x: allowed only as a do-not-use note, check each")
    if hard:
        die(hard)

    out_md = os.path.join(proj, cfg["note_title"] + ".md")
    exp = os.path.join(proj, "Exports")
    os.makedirs(exp, exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(exp, "Content Idea Bank.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Pillar"] + cols)
        for r in rows:
            w.writerow([f"{r['pillar']}: {pillars[r['pillar']]['name']}"] + cells(r))
    with open(os.path.join(exp, "Lead Magnet Catalog.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(LMH)
        w.writerows(lm_rows)

    flags = collections.defaultdict(list)
    first = cfg["exec"].split()[0].lower()
    for r in rows:
        s = " ".join((r["T"], r["I"], r["H"], r["SRC"])).lower()
        for tag in ("needs client ok", "verify", f"needs {first}", "confirm speaker"):
            if tag in s:
                flags[tag].append(r["ID"])
    print(f"wrote {out_md} and 2 CSVs")
    print(f"total {total} | per pillar " + ", ".join(f"{p} {counters[p]}" for p in pillars))
    print("stage " + ", ".join(f"{s} {stage[s]} ({pct(stage[s])}%)" for s in STAGES))
    print(f"lead magnets {len(lms)} | used {len(used_lms)}")
    for tag, ids in flags.items():
        print(f"flag '{tag}': {len(ids)} -> {', '.join(ids)}")
    for w_ in warnings:
        print("WARN:", w_)


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("init", "build"):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "init":
        name = sys.argv[sys.argv.index("--exec") + 1] if "--exec" in sys.argv else "EXEC NAME"
        init(sys.argv[2], name)
    else:
        build(sys.argv[2])
