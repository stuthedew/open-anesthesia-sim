---
id: PL-W312
title: When the whole preferences file is refused, its notice gives the reason in the file's own words, such as 'its keys are wrong: missing [...], not known [...]', where the price notices now use the user's
priority: P3
effort: S
status: done
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/preferences.py, tests/unit/test_preferences.py, docs/INTERFACE.md
deferred-from: v0.7.0 - not safety or science, and no user sees a wrong value from it: the notice still says the change will not be kept, only in the file's words; the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-27
closed: 2026-11-28
pr: 2367
filed-pr: 2332
payoff: a user whose preferences file is refused is told in plain words what was wrong and what to do, instead of reading the file's key names
tests: tests/unit/test_preferences.py::test_a_document_that_cannot_be_checked_entry_by_entry_turns_saving_off, tests/unit/test_preferences.py::test_a_file_from_a_newer_build_is_not_read_and_never_overwritten, tests/unit/test_preferences.py::test_two_prices_for_one_agent_turn_saving_off
reenters: PL-VT87
---

**Problem.** When the whole preferences file is refused, its notice gives the reason in the file's own words, such as 'its keys are wrong: missing [...], not known [...]', where the price notices now use the user's

The text is built in `_from_document` in `src/anesthesia_sim/app/preferences.py`, for example `f"its keys are wrong: missing {missing}, not known {unknown}"`, which prints the file's key names as Python lists. `unsaved_preferences_notice` puts the reason after "This change lasts only until the application closes, because".

**Why it matters.** A user reads JSON key names in Python's list notation, and learns neither what went wrong in the terms of the View nor what to do next. `PL-VT87` rewrote each refused price's reason in the words the agent cost View uses, checking each refusal against NUREG-0700 guideline 2.7.3-1, which asks that a refusal say what to do next. This text was outside that item's inventory.

**Reproduced 2026-11-28.** `grep -n "its keys are wrong" src/anesthesia_sim/app/preferences.py` finds the line in `_from_document`. The other reasons raised there, such as "its document is not a JSON object" and "its prices is not a list", are worded the same way.

**Done when.** For each reason `_from_document` raises, a test that refuses the whole file shows a notice that says, in the words the agent cost View uses, what was wrong and what the user can do, with no key name in Python's list notation. The wording is checked against a published plain-language guide, and the guide is named here.

**Generator check.** A re-entry of `PL-VT87` (closed 2026-11-27): the same rewrite of a refusal into the user's words, at a sibling text that its inventory did not list. `PL-VT87`'s own pull request, #2332, filed it.

**Fixed 2026-11-28.** The notice for a file that cannot be used at all now
says, in order, what happened, the reason in the agent cost View's words, what
that means for the reader's settings, what the reader can do, and last the
file's path. It reads "The application could not use your preferences file,
because the file has no agent prices. None of your saved settings is in use,
and the application does not save changes you make now, so the file stays as it
is. To use your saved settings again, correct the file or move it out of its
folder, then restart the application. The file is ...". A file that a newer
version saved ends instead with "To use your saved settings, open the newer
version of the application. To start again without them, move the file out of
its folder, then restart this version." Each next step ends in a restart,
because the application reads its preferences only at launch.

No reason that `_from_document` or `PreferencesStore.load` raises opens with
an "its" that has no noun to point at. Each names the file or the setting it
is about. A
missing setting is named as the View names it ("agent prices", "axis top",
"choice of how agent amounts are shown", "version"), through
`_DOCUMENT_KEY_WORDS`. A setting that the View has no name for is named as the
file writes it, in quotes, because that is the only name the reader can find
in the file. No reason prints a Python list. `PreferencesStore.save` now
raises "saving is off for this session." followed by the launch notice, so the
unsaved-change notice repeats the reason and the next step.

**Sources, read 2026-11-28.** Microsoft's Windows error-message guidelines
(https://learn.microsoft.com/en-us/windows/win32/uxguide/mess-error): a message
gives "a problem, cause, and solution", should "Describe the problem in terms
of user actions or goals", and should "Avoid putting full file paths and URLs
in the main instruction", so the path comes last. Nielsen Norman Group's
error-message guidelines
(https://www.nngroup.com/articles/error-message-guidelines/): "Offer
constructive advice". The plain-language guide named for the "Done when" is
digital.gov's plain-language guide, "Writing for understanding"
(https://digital.gov/guides/plain-language/writing/), which asks for the
active voice. That is why the opening sentence names the application as the
one that could not use the file. NUREG-0700 Rev. 3 guideline 2.7.3-1, as
`.claude/rules/sources-and-docstrings.md` quotes it, asks that an error
message "state the error and possible subsequent operations".

**Regression check.** Run against the code before the fix (the new
`tests/unit/test_preferences.py` with `src/anesthesia_sim/app/preferences.py`
from 7a9db9f0 on `PYTHONPATH`): 21 of 87 tests fail. The "an unknown key" case
of `test_a_document_that_cannot_be_checked_entry_by_entry_turns_saving_off`
fails with `AssertionError: assert 'the preferen...left as it is' ==
'The applicat...erences.json.'`.

**Docs checked at close-out.** `docs/INTERFACE.md` § "A cost at the reader's
price" (a new paragraph says what the notice holds and in what order, and
names the tests), `docs/MODEL.md` (no mention of the preferences file),
`docs/VERIFICATION.md` (none), `docs/PARAMETERS.md` (none), `README.md` (none),
and the module docstring of `src/anesthesia_sim/app/preferences.py` (two
bullets updated).
