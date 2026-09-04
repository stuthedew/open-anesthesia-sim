---
id: PL-GJDW
title: contrast_check's requirement descriptions cite simulation_view line numbers, and all eight are wrong
status: untriaged
added: 2026-09-04
---

**Problem.** contrast_check's requirement descriptions cite simulation_view line numbers, and all eight are wrong

**Why it matters.**

**Where.**

**Done when.**

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
