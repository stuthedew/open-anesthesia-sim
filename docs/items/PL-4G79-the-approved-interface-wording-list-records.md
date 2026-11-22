---
id: PL-4G79
title: The approved interface wording list records only default runs, so a string shown only after a setting change, with a bookmark or price, or in a halt or failure notice is held by no approved list
priority: P1
effort: M
status: done
classes: defect, safety, test
feature: presentation-safety
touches: tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json
deferred-from: v0.7.0 - not live: checked 2026-11-22, the gap is in the approval test and no wrong or misleading notice wording is known on screen; the forbidden-phrase checks in tests/integration/simulation_view/ still hold these notices
added: 2026-11-11
closed: 2026-11-22
pr: 2227
payoff: A change to the wording of a halt, refusal or failure notice cannot reach a learner until a person has read and approved it.
tests: tests/integration/test_interface_wording.py::test_every_string_the_view_shows_is_on_the_approved_list
---

**Problem.** The approved interface wording list records only default runs, so a string shown only after a setting change, with a bookmark or price, or in a halt or failure notice is held by no approved list

**Found by** `PL-86VL`'s blind review, 2026-11-11. The approved list records
the default run of each agent at fixed times. The notices most likely to carry
a sentence a clinician acts on, such as a halt after a failed Reset
(`PL-MVCF`), a refused setting, or a failure that withholds values, appear
only after an event, so no approved list holds their wording. The forbidden-
phrase checks in `tests/integration/simulation_view/` still apply to
them. Recording them needs a way to bring each state about in the test, as
`tests/integration/test_failed_start_over.py` does for the halt.

**Checked 2026-11-22**, at `d4e8200c`. The gap is still there. The module docstring of `tests/integration/test_interface_wording.py` says it outright: "A string that appears only after a setting changes, with a bookmark or a price, or in a halt or failure notice, is not recorded, and this test does not hold it." Its `RECORDED_POINTS` are fixed times of each agent's default run.

**Why it matters.** The notices that only an event brings up are the ones a learner is most likely to act on: a halt that withholds values, a refused setting, a failed Reset. Their wording can change without any person approving it, because the approval test never sees them. The forbidden-phrase checks still catch the phrases someone listed, but not a new misleading sentence that nobody thought to forbid. No wrong wording is known to be on screen now.

**Done when.** The approved wording list also holds the strings shown after a setting change, with a bookmark set, with a price entered, after a refused setting, and in each halt or failure notice, each brought about by the test itself. A change to any of those strings fails the test until a person approves it.

**Generator check.** A follow-on of `PL-86VL` (the approval test of the interface's wording, closed 2026-11-11), which drew this limit on purpose and stated it in the test's docstring. So it is not a fix that failed to hold, and it is not a re-entry. The misread fact is which strings a learner can be shown, and no head's `misread:` line states it.

**Built 2026-11-22.** `EVENT_POINTS` in `tests/integration/test_interface_wording.py` brings about a fresh gas flow change, a time mark and a MAC mark, a run stopped on a mark, a price set by the reader, a refused setting, a run stopped at the supported length and every halt or failure scenario in `_ONE_STATE_SCENARIOS` except the drawn frame. Each point records only the strings that no default point shows, 139 lines in `approved_interface_strings.json`. With the refused-setting banner's "still running" changed to "still runs", the new test fails with "setting refused, new: 'Setting refused — ... still runs its previous setting.'", and the test before this change passes it (both run 2026-11-22). One finding is filed as `PL-8QFW`: the refused-setting banner shows the core's Python parameter name.

**Documentation checked on 2026-11-22**: `docs/ARCHITECTURE.md`, whose passage on the wording test said event-only strings are not on the list, now says the test records them. No other document names the test or its list.

**Blind review, 2026-11-22, and what changed.** One pass found five things. Four are fixed in the same commit. Every point now builds its dashboard with a case, as the application does, so the Branch View's mark wordings ("Branch here: ..., stopped on your mark" and "..., on your mark") are recorded. New points bring about a mark reached, marks not reached within the supported run length, and compared runs whose marks read "Run N reached", "not yet", "before this branch opened" and "not reached before the simulation error". The setting-change point now also records a delivered-concentration change and one adjustment of two settings over an interval. The loops that step a run are bounded and fail with where the run stood, where they could hang. The fifth, the Area size notices that the run-state scenarios' window brings into thirteen points, is filed as `PL-P6TK`.
