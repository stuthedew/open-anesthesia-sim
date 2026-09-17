---
id: PL-LBW5
title: Five open items' verify: commands grep a file their own touches does not declare, so bin/docket concurrent gives a wrong answer for work that will certainly edit it
status: untriaged
added: 2026-09-17
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
