---
id: PL-K88Z
title: Inventory every second copy of a shared fact across the tree, sorted by the four shapes (a value copied, state with two writers, a rule made in several places, configuration restated), and file each finding under one-source-of-truth
priority: P2
effort: M
status: ready
classes: planning
feature: one-source-of-truth
touches: ROADMAP.md
added: 2026-10-19
payoff: the one-source-of-truth row is sized from a count of every second copy, so its scope is measured rather than guessed
verify: grep -q 'Inventoried 2026-' ROADMAP.md
---

**Problem.** Inventory every second copy of a shared fact across the tree, sorted by the four shapes (a value copied, state with two writers, a rule made in several places, configuration restated), and file each finding under one-source-of-truth

**Why it matters.** Step 2 of `PL-2LB5` (the one-source-of-truth design round). The project owner chose on 2026-10-19 to run this inventory before v0.6.0 ships and to scope the fixes as their own roadmap row after it (`ROADMAP.md` planned-milestone item 43). The inventory decides how large that row is, so it comes first.

**Approach.** Deterministic tools first, the session's judgment last, per `CLAUDE.md` § "Prefer deterministic tooling over repeated model work":
1. **A value copied.** Read the baselines of `tools/literal_home_check.py` and `tools/fact_home_check.py`. Then list every number in `docs/MODEL.md` and `README.md` that restates a value in `src/anesthesia_sim/data/` or in code, with its home.
2. **State with two writers.** List each displayed or derived run state in `src/anesthesia_sim/app/` and every path that writes it. `PL-X7D5` is the pattern of one writer.
3. **A rule made in several places.** Run pylint's duplicate-code check (`R0801`) over `src/`, `tools/` and `subprojects/docket/`. List every range or predicate checked by hand where a checked type or a home already exists.
4. **Configuration restated.** List the Python version, paths, commands and timeouts that appear in more than one of `pyproject.toml`, `.github/workflows/`, the `Makefile`, `docket.toml` and the docs.

Sort each finding by shape. File it under `one-source-of-truth`, unless one of the four check items (`PL-JS6P`, `PL-WM5P`, `PL-VWXL`, `PL-SH0W`) will burn it down as part of its baseline. Leave out the two copies that must stay copies: a test's expected value, and a published value restated beside its citation.

**Done when.** Each of the four shapes has a dated count in this brief, each finding is filed or named in the baseline of the check item that will remove it, and `ROADMAP.md` planned-milestone item 43 carries the resulting size in a sentence that begins "Inventoried 2026-".
