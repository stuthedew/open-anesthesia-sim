---
id: PL-W21J
title: Give the elimination comparison a test-only open-circuit driver, so washout can be validated rather than only measured
priority: P1
effort: M
status: done
classes: science, test
feature: numerical-domain
touches: tests/reference/test_published_wash_in.py, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-07
verify: uv run pytest tests/reference/test_published_wash_in.py && grep -q 'def test_five_minute_elimination_ratio_without_rebreathing_against_published_human_measurement' tests/reference/test_published_wash_in.py
---

**Problem.** `tests/reference/test_published_wash_in.py` now compares modelled
`F_A/F_A0` at five minutes of elimination against all four Yasuda cohorts, and
the comparison misses every one of them by +1.0 to +5.0 published SD. Most of
that is apparatus rather than physiology, measured on 2026-09-06: this model
always rebreathes, so through an elimination the inspired fraction settles near
`V_A/(V_A + FGF)` of the alveolar one - 0.29 at the highest supported flow, and
measured at 0.30 to 0.32 at five minutes - and `F_A/F_A0` has no denominator
term to divide that out, so agent coming back from the circuit is counted as
though it had come back out of the patient. Holding `F_I` at zero instead moves
sevoflurane, isoflurane and desflurane from +3.67, +4.02 and +1.02 SD to -0.25,
+0.54 and -2.40 SD.

**Why it matters.** The published protocols measured mixed expired
concentrations and reported agent recovered against agent taken up, which needs
the whole expirate collected rather than returned to the subject, so their
elimination ran at an inspired fraction at or near zero. The model cannot be
set to that at any supported fresh gas flow, so the one comparison this
repository has in the elimination direction is a regression band rather than a
validation. With a non-rebreathing mode it would be a validation, and the
result would be worth having in both outcomes: it would either put two of the
three agents inside the published spread or turn desflurane's -2.40 SD into a
real disagreement about tissue return to explain.

**Approach, decided by the project owner on 2026-09-06: the test-only
open-circuit driver.** Two candidates were costed. A *supported* non-rebreathing
mode is the more capable and was not taken: it changes the model boundary rather
than a fixture, and it adds a mode the interface would then have to make
visible, which `CLAUDE.md` treats as a human-factors cost in its own right. The
driver answers the scientific question - whether this model's tissue return
reproduces a human elimination once the apparatus difference is removed - at the
price of validating a condition the shipped simulator cannot be put in. That
price is the thing the module has to say plainly wherever it states the result,
in the same breath as the number.

**Name whatever it adds for what it does, never for what it is hoped to show.**
`PL-0M32` records what the alternative cost: `PL-HB58`'s `verify:` named a test
`..._matches_published_human_measurement`, the comparison turned out not to
match, the test shipped as `..._against_...`, and the item then looked exactly
like one nobody had started. A name has to survive either outcome - and both
outcomes are live here, since the diagnostic already puts sevoflurane and
isoflurane inside the published spread (-0.25 and +0.54 SD) and desflurane 2.40
SD outside it on the *other* side.

**Where.** `tests/reference/test_published_wash_in.py` for the driver and the
comparison, and `docs/MODEL.md` § "Published wash-in validation test" for the
restatement. Nothing under `src/` moves - that is what choosing the driver over
a supported mode means.

**Done when.** The elimination comparison can be run at an inspired fraction of
zero from `tests/reference/`, the module and `docs/MODEL.md` both say that the
condition is a diagnostic the shipped simulator cannot be put in, and the
comparison against the four published cohorts is restated as whatever it then
turns out to be.

**Triaged `ready` rather than `needs-decision`, because the decision was taken
while the pass was running.** This item was triaged on 2026-09-06 as a question
between a supported non-rebreathing mode and a test-only driver; `#415` landed
the project owner's answer into the brief above before the triage merged, so
the question is closed and only the work remains. The fields follow that
answer: nothing under `src/` moves, so `touches` names the test module and
`docs/MODEL.md` alone, `classes` is `science, test` rather than `science,
feature`, and the size drops from `L` to `M`.

The `verify:` command names the test at the condition rather than at the
result, which is what the brief above asks for: `..._without_rebreathing_...`
survives either outcome, where `..._matches_...` would not. Run 2026-09-06
before the work: exit 1, with the module's 57 tests passing and the test
absent.

**Retitled 2026-09-06, after `#415` decided the approach** (project owner). The
old title - "Give the model a non-rebreathing elimination mode" - promised a
change under `src/`, which the driver route explicitly does not make, so a
session meeting it in `bin/docket next` would open an item whose brief refuses
what its title offers. The purpose clause is unchanged, because it is still
what the work is for.
