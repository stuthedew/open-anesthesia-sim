---
id: PL-W312
title: When the whole preferences file is refused, its notice gives the reason in the file's own words, such as 'its keys are wrong: missing [...], not known [...]', where the price notices now use the user's
priority: P3
effort: S
status: ready
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/preferences.py, tests/unit/test_preferences.py
deferred-from: v0.7.0 - not safety or science, and no user sees a wrong value from it: the notice still says the change will not be kept, only in the file's words; the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-27
filed-pr: 2332
payoff: a user whose preferences file is refused is told in plain words what was wrong and what to do, instead of reading the file's key names
reenters: PL-VT87
---

**Problem.** When the whole preferences file is refused, its notice gives the reason in the file's own words, such as 'its keys are wrong: missing [...], not known [...]', where the price notices now use the user's

The text is built in `_from_document` in `src/anesthesia_sim/app/preferences.py`, for example `f"its keys are wrong: missing {missing}, not known {unknown}"`, which prints the file's key names as Python lists. `unsaved_preferences_notice` puts the reason after "This change lasts only until the application closes, because".

**Why it matters.** A user reads JSON key names in Python's list notation, and learns neither what went wrong in the terms of the View nor what to do next. `PL-VT87` rewrote each refused price's reason in the words the agent cost View uses, checking each refusal against NUREG-0700 guideline 2.7.3-1, which asks that a refusal say what to do next. This text was outside that item's inventory.

**Reproduced 2026-11-28.** `grep -n "its keys are wrong" src/anesthesia_sim/app/preferences.py` finds the line in `_from_document`. The other reasons raised there, such as "its document is not a JSON object" and "its prices is not a list", are worded the same way.

**Done when.** For each reason `_from_document` raises, a test that refuses the whole file shows a notice that says, in the words the agent cost View uses, what was wrong and what the user can do, with no key name in Python's list notation. The wording is checked against a published plain-language guide, and the guide is named here.

**Generator check.** A re-entry of `PL-VT87` (closed 2026-11-27): the same rewrite of a refusal into the user's words, at a sibling text that its inventory did not list. `PL-VT87`'s own pull request, #2332, filed it.
