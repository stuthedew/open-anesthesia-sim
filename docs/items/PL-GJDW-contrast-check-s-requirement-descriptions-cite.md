---
id: PL-GJDW
title: contrast_check's requirement descriptions cite simulation_view line numbers, and all eight are wrong
priority: P2
effort: S
status: done
classes: defect, docs
feature: dev-tooling
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
added: 2026-09-04
closed: 2026-09-06
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_every_requirement_names_a_symbol_that_exists' tests/unit/test_contrast_check.py
---

**Problem.** Each `Requirement` in `tools/contrast_check.py` carries a prose
description naming where the colour pair is used, and several cite line
numbers into `src/anesthesia_sim/app/simulation_view.py`. Checked
2026-09-04 against `origin/main` plus the `PL-CC23` diff, every one of the
eight cited lines points at something unrelated:

| Cited | What is actually there |
| --- | --- |
| `:320`, `:336`, `:346`, `:356` (slider tracks) | comments in the theme and legend regions |
| `:406`, `:417`, `:678` (halted notice, status word, disclaimer) | a border comment, a bare `)`, a drawing-order comment |
| `:736` (agent-accounting status word) | `*self._wash_in_control_mark_series` |

They are not off by the size of one diff - they are off by hundreds of lines,
so they were already stale before `PL-CC23` touched the file. Nothing
validates them.

**Why it matters.** This is the *documentation of a safety check* being
wrong. `.claude/rules/ui-color.md` treats a colour pair that carries meaning
as an encoding, and these descriptions are how a reviewer finds the code a
declared pair is defending. A reviewer who follows one lands on an unrelated
line and has no way to tell whether the requirement still covers anything -
which is worse than no citation, because it looks authoritative. It also
makes the check's own coverage unauditable: whether every WARNING-on-PANEL
site is really covered cannot be answered from the file.

**Approach.** Two halves, and the second is the one that lasts.

Replace the line numbers with symbol names - the method or attribute the
colour is set on, as the `PL-CC23` edit did for the WARNING/PANEL entry
(`_off_scale_text`, `_build_agent_accounting_panel`). A symbol survives every
edit that does not rename it, where a line number survives none.

Then make it decidable, per `CLAUDE.md`'s "find the decidable part and put it
in code": a cited symbol either exists in the named module or it does not, and
that is a `grep` the check can run on itself. `tools/doc_check.py`'s
dangling-citation check is the worked example of exactly this rule for `docs/`
and is the thing to model it on - it decides whether a cited path exists and
never whether the sentence around it is true. The judgment half here - whether
the named symbol is really where that colour matters - stays with the reviewer.

**Done when.** No requirement description cites a line number; each names a
symbol that exists; and `make check` fails when one does not.

**Rechecked a day later, folded in from `PL-84XD` at triage 2026-09-05.**
The same tuple was read line by line on 2026-09-05 and the count had grown
rather than settled: nine entries cite `simulation_view.py:NNN` - `:208`,
`:242-244`, `:320`, `:336`, `:346`, `:356`, `:406`, `:417`, `:619`, `:622`,
`:653`, `:678`, `:682`, `:731` - and not one lands on what its entry claims.
`:682` is cited as "the run-status word while running" and is the
control-mark series list; `:406` is cited as the educational-use disclaimer
and is a comment about agent render styles; `:731` is cited as an accounting
status word and is a chart gridline colour.

Three entries already cite by symbol - `_build_agent_accounting_panel`,
`_off_scale_text`, `_build_new_case_dialog` - which is the form to convert
the rest to, and the evidence that the form works. `PL-84XD` also proposed
that `contrast_check.py` refuse a criterion matching `simulation_view.py:` followed
by a digit outright, so the rotting form cannot come back; prefer that to a
convention if it is a few lines, per `CLAUDE.md`'s rule on moving the
decidable half out of a session's head.
