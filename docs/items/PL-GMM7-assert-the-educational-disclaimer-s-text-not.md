---
id: PL-GMM7
title: Assert the educational disclaimer's text, not just that its line executes
priority: P2
effort: S
status: ready
classes: test
feature: dev-tooling
touches: tests/unit/test_simulation_view.py
added: 2026-08-30
verify: uv run pytest tests/unit/test_simulation_view.py -k disclaimer
---

**Problem.** The educational disclaimer at `app/simulation_view.py:393-401` —
"Educational simulation only. This idealized model is not a clinical
prediction, monitoring, or dosing tool." — has no test. 573 tests and 98%
coverage, and the one string that constitutes the project's regulatory posture
is unprotected. Coverage does not help here and actively misleads: the line
executes whenever the view is built, so the percentage looks fine while nothing
asserts a word of the content.

**Why it matters.** It is a stated release criterion twice over —
`docs/MODEL.md:1363` ("the interface contains the educational and non-clinical
warning") and `ROADMAP.md`'s v0.1.0 definition of done ("the user interface
states that this is an educational model, not a clinical prediction") — and
both are checked by a person reading the screen. A refactor that moves the
panel, an edit that softens the wording, or a layout change that drops the
control passes the whole suite. This is the single string that separates an
educational tool from something a user could take as clinical, and it is the
one presentation element with no automated guard at all.

**Where.** `app/simulation_view.py:393-401`;
`tests/unit/test_simulation_view.py`.

**Scope note — checked, not assumed.** PL-41YP (assert every required displayed
output reaches the rendered view) does **not** cover this. That item's Decided
scope is `docs/MODEL.md`'s "Minimum displayed outputs", a fifteen-bullet list of
concentration and time values that does not include the disclaimer. This stays
a separate item, but the assertion should land in the same test module PL-41YP
builds, so the required-output checks and the required-warning check sit
together.

**Class note.** Captured with a suggested `safety` class; filed as `test` to
match PL-41YP and the `core-guard-coverage` items, which are the project's
existing precedent for a coverage gap on a safety-relevant path. The shipped
string is correct today; what is missing is the guard against regression.

**Done when.** A test asserts the disclaimer's exact text is present in the
rendered view, and it fails if the control is removed, moved out of the
rendered tree, or reworded.
