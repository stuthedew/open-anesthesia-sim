---
id: PL-LBW5
title: Five open items' verify: commands grep a file their own touches does not declare, so bin/docket concurrent gives a wrong answer for work that will certainly edit it
priority: P3
effort: S
status: ready
classes: defect
feature: verify-command-health
touches: docs/items
added: 2026-09-17
verify: bin/docket check && grep -q '^touches:.*subprojects/docket/tests/test_cli.py' docs/items/PL-L4YG-*.md
---

**Problem.** Five open items' verify: commands grep a file their own touches does not declare, so bin/docket concurrent gives a wrong answer for work that will certainly edit it

**Found while measuring `PL-879R`** (dropped 2026-09-17; its brief has the
method). Counting the open store's `verify:` commands by shape turned up five
whose discriminating clause names a path the item's own `touches` does not
declare:

| Item | `touches` | Its command reads |
| --- | --- | --- |
| `PL-L4YG` | `src/docket/cli.py`, `src/docket/store.py` | `subprojects/docket/tests/test_cli.py` |
| `PL-QS9H` | `tools/`, `app/simulation_view.py`, `.claude/rules/ui-reader.md` | `tests/unit/test_standing_text_check.py` |
| `PL-RWBV` | `docs/items` | `subprojects/docket/tests/test_checks.py` |
| `PL-TCKV` | `docs/worker.md`, `src/docket/verify.py` | `pyproject.toml` |
| `PL-MSFB` | `docs/items/`, `docs/WORKING_NOTES.md` | `docs/items` |

`PL-MSFB` is a trailing-slash artifact and not a finding. The other four are
real: each names a **test file the work will certainly add to**, since the
command greps for the test it owes, and none declares it.

**Why it matters rather than being tidiness.** `bin/docket concurrent` reads
`touches` and nothing else, and the skill is explicit that it "rules work out
and never certifies it" — but an item whose own command names a file it does
not declare is a case where the store already holds the evidence and the answer
is wrong anyway. Two sessions can be told they do not overlap on
`test_checks.py` while both items' commands say they will edit it.

**The decidable half, if it is worth a check at all.** Whether a path named in a
`verify:` clause is covered by the item's `touches` is a string test, and
`PL-XMNC` builds the clause-splitting and path-reading this would need. The
population is four, though, so the honest first step is to fix the four and see
whether a fifth ever arrives — `CLAUDE.md`'s gate is whether it will genuinely
run again, and where the benefit is unclear the answer is no.

**Done when** the four items declare the test files their commands name, or a
reason is recorded for leaving one of them out.

**Grouped under `feature: verify-command-health`** at triage, with `PL-RCQM` -
the same question from the other end: whether every open item's `verify:` command
is one the store can act on. This half is whether the command's paths are
declared; `PL-RCQM`'s is whether the command can run at all.

**Re-pointed by `PL-6TP8`, 2026-09-19.** This is the contract's second
obligation on a command - the paths its discriminating clause reads are
declared in `touches` - and the work is as briefed: the four declare the test
files their commands name.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Partly overtaken by attrition
rather than by work: none of the remediation landed, and the population shrank
because an item closed.** `PL-L4YG` closed 2026-09-19 (#679) with its
`touches` still omitting `subprojects/docket/tests/test_cli.py`, and
`bin/docket concurrent` ranks only open items, so it is out of the harm this
describes. The title's "five" and the problem statement are therefore four,
three of them live findings: `PL-QS9H`, `PL-RWBV` and `PL-TCKV`, each still
`ready` and each still undeclaring the path its own command greps. One
correction to the brief's characterisation: `PL-TCKV`'s undeclared path is
`pyproject.toml`, not a test file.

The enabling work is done and unconsumed: `PL-XMNC` closed 2026-09-17 (#666)
and `verify.py` carries `command_paths` at `:527` and `reads_any` at `:571` -
but `checks.py` never calls either, and `concurrency.py:60-61` still reads
`touches` and nothing else. `PL-RCQM`, the pairing named under
`feature: verify-command-health`, is `dropped`.

**This item's own `verify:` is now unsatisfiable as written**: its second clause
greps `PL-L4YG`'s `touches`, and satisfying it would mean editing a shipped
item's declaration. Re-point it at one of the three open items as part of
starting this.
