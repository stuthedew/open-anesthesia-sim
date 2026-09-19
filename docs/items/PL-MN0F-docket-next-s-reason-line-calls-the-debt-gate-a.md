---
id: PL-MN0F
title: docket next's reason line calls the debt gate a 'frozen list', the one wording that never says 'gate', so on this project's configuration no recommendation has ever announced a gate item as a gate item
priority: P2
effort: S
status: done
classes: defect
feature: recommendation-rationale
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_plan.py
added: 2026-09-19
closed: 2026-09-19
pr: 729
verify: grep -qF 'assert "frozen list" not in pick.reason' subprojects/docket/tests/test_plan.py
---

**Problem.** docket next's reason line calls the debt gate a 'frozen list', the one wording that never says 'gate', so on this project's configuration no recommendation has ever announced a gate item as a gate item

**Why it matters.** The project owner reported it from the outside, which is
the only place it was visible: `bin/docket next` "hasn't recommended a gate
item in a while - or at least hasn't called something a gate item if it was"
(2026-09-19). The second clause is what was happening. `docket next` ranked the
gate correctly throughout and has been leading with gate work; it just never
used the word.

Three renderers share one relation, `Scope.placement`, and only one of them was
readable. `placement_line`, which `docket show` prints, says "on the debt gate
recorded under ...". `placement_mark`, which `docket status` prints, draws
`[gate]`. `ROADMAP.md` calls it the debt gate throughout. `recommend`'s own
reason line said "On v0.5.0's **frozen list**, the step the project is on" -
the store's internal name for the recorded list, never the name of the thing
the owner is tracking.

That one is the command that actually hands over the work, and it is the only
one of the three a session runs before picking something up. So the effect was
not a cosmetic inconsistency: the owner had no way to tell gate work from
off-gate work in the only output they see it in, and reasonably concluded the
gate was not being recommended at all.

It fires on the ordinary arrangement, which is why it went unnoticed for so
long. `recommend` has a second clearing branch, used when the gate ships under a
different milestone from the one that recorded it, and that branch has always
said "debt gate". Only the common case - a milestone clearing its own gate,
which is where this project has sat since v0.5.0 was scoped - took the wording
that omitted it.

**Done when.** `recommend`'s `elif scope.clearing:` branch names the debt gate
in the same words `placement_line` uses, and a test pins both the phrase and
the absence of "frozen list", so a later reword cannot quietly drop the noun
again.
