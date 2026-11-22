---
id: PL-PKQC
title: The 10% sensitivity table in docs/MODEL.md is dated the day before the venous pool changed, and two of its rows no longer reproduce to the last digit
priority: P2
effort: S
status: ready
classes: defect
feature: model-spec-accuracy
touches: docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
payoff: the table that says how large a coefficient error the published-data comparison can detect gives the figures the shipped model produces
---

**Problem.** The 10% sensitivity table in docs/MODEL.md is dated the day before the venous pool changed, and two of its rows no longer reproduce to the last digit

**Why it matters.** The table tells a reader how large a coefficient error the published-data comparison can detect. Two of its rows give figures that the model no longer produces, under a date that falls before the venous pool changed.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21.

**What the document says.** § "Published wash-in and elimination validation test" gives a table of "how far each ratio moves when one coefficient is raised by 10%, in units of that ratio's own published SD (from model runs on 2026-09-06)". Two rows read "| Blood:gas | −0.57 to −0.64 | +0.09 to +0.17 |" and "| Vessel-rich tissue:gas | −0.02 to −0.06 | +0.45 to +0.55 |".

**What the tree gives today.** With `StoredParameterChange(parameter, 1.10)` and the test module's own `_wash_in_ratio()` and `_eliminate()`, against each agent's first cohort: blood:gas elimination +0.11 to +0.18, and vessel-rich elimination +0.44 to +0.54, wash-in −0.02 to −0.07. The muscle and fat rows reproduce as printed. The venous pool volume changed on 2026-09-07, the day after the table's date. With the second isoflurane cohort's own SD, which the table's wording does not exclude, blood:gas wash-in reaches −0.52 and vessel-rich elimination +0.65. The conclusions drawn from the table still hold.

The docstring of `tests/reference/test_published_wash_in_and_elimination.py` carries the same table, and its line "+0.45 to +0.55" repeats one figure. A change under `tests/reference/` waits for the project owner's read.

[superseded 2026-11-21] **Why it waits on `PL-SZ6G`** (a run's time as a whole number of seconds). That branch changes the step at which every figure in the table is computed, and it rewrites the test module that holds the table's copy. The table is to give the figures of the tree that ships, so measure once, after that branch merges. A change to an existing line of a test under `tests/reference/` also waits for the project owner's read.

**Done when.** The table and the test module's copy give the figures of the tree that ships, with the date and the words "against each agent's first cohort".

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.

**Checked 2026-11-22** against `d4e8200`: still applies. The table in `docs/VERIFICATION.md` § "Published wash-in and elimination validation test" and its copy in the module docstring of `tests/reference/test_published_wash_in_and_elimination.py` both still give the 2026-09-06 figures, with "+0.09 to +0.17" and "+0.45 to +0.55". The blocker `PL-SZ6G` closed with #2180, so the table can now be measured once on the tree that ships.

**Partly done 2026-11-22**, on `claude/project-thread-v9awbd` from `c0e9861e`. The table in `docs/VERIFICATION.md` § "Which stored values each ratio responds to" now gives the figures of the shipped tree, dated 2026-11-22, and says they are against each agent's first cohort, naming isoflurane's. Two rows changed: blood:gas elimination is now +0.11 to +0.18 (was +0.09 to +0.17), and vessel-rich is now −0.02 to −0.07 for wash-in and +0.44 to +0.54 for elimination (was −0.02 to −0.06 and +0.45 to +0.55). The muscle and fat rows reproduce as printed. The two sentences after the table still hold. The 0.18 and 0.54 coincide with stored values, so a `not-restated:` marker now lists them, in place of the old marker for 0.06.

Measured with this script, run from the repository root as `uv run python sens.py`:

```python
import sys, importlib.util
spec = importlib.util.spec_from_file_location("m", "tests/reference/test_published_wash_in_and_elimination.py")
m = importlib.util.module_from_spec(spec); sys.modules["m"] = m; spec.loader.exec_module(m)
first = {}
for c in m.PUBLISHED_MEASUREMENTS:
    first.setdefault(c.agent_id, c)
for p in m.AGENT_PARAMETER_FIELDS:
    w, e = [], []
    for agent, c in first.items():
        ch = m.StoredParameterChange(p, 1.10, p)
        w.append((m._wash_in_ratio(agent, change=ch) - m._wash_in_ratio(agent)) / c.wash_in_standard_deviation)
        e.append((m._eliminate(agent, change=ch).ratio - m._eliminate(agent).ratio) / c.elimination_standard_deviation)
    print(p, min(w), max(w), min(e), max(e))
```

It printed, per coefficient, wash-in then elimination: blood:gas −0.6429 to −0.5729 and +0.1065 to +0.1759; vessel-rich −0.0655 to −0.0196 and +0.4410 to +0.5410; muscle −0.1545 to −0.0752 and −0.1169 to −0.0936; fat −0.0038 to −0.0015 and −0.0027 to −0.0021.

**What is left: the copy in the test module.** The module docstring of `tests/reference/test_published_wash_in_and_elimination.py` still prints the 2026-09-06 table, and a later docstring in the same file still says "+0.45 to +0.55 published SD per +10%". An edit to an existing line of a test under `tests/reference/` holds its pull request for the project owner's read, so it goes in the later pull request that carries the other `tests/reference/` edits, not in #2237. Recommendation for that pull request: replace the module's copy of the table with a pointer to `docs/VERIFICATION.md` § "Which stored values each ratio responds to", so that one record holds the figures, and change "+0.45 to +0.55" to "+0.44 to +0.54".

Files checked: `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/PARAMETERS.md`, `docs/INTERFACE.md` and `README.md`, by `grep -n "0\.45 to\|0\.09 to\|+0.17"`. No other document printed the table.
