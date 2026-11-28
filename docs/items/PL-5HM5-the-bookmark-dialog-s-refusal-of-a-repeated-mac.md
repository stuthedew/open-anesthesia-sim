---
id: PL-5HM5
title: The bookmark dialog's refusal of a repeated MAC target names the crossing by a Python repr, '(<RecordedQuantity.VESSEL_RICH: 'vessel_rich'>, 0.8)', and the repeated-instant refusal names its instant with no unit
priority: P3
effort: S
status: done
classes: ux
touches: src/anesthesia_sim/app/bookmarks.py, tests/unit/test_bookmarks.py
added: 2026-10-17
closed: 2026-11-27
pr: 2342
payoff: a user who marks the same MAC target or instant twice is told which mark in the dialog's own words, not in a Python repr or a unitless number
tests: tests/unit/test_bookmarks.py::test_the_repeated_instant_refusal_is_pinned_whole, tests/unit/test_bookmarks.py::test_the_repeated_mac_target_refusal_is_pinned_whole, tests/unit/test_bookmarks.py::test_the_repeat_refusal_names_the_mark_that_repeats
---

**Problem.** The bookmark dialog's refusal of a repeated MAC target names the crossing by a Python repr, '(\<RecordedQuantity.VESSEL_RICH: 'vessel_rich'>, 0.8)', and the repeated-instant refusal names its instant with no unit

**Evidence (measured 2026-10-17, while `PL-79PK` pinned the banner
refusals).** `BookmarkSet.__post_init__` passes each mark's key to
`_refuse_repeats` in `app/bookmarks.py`, which formats it with `{key!r}`.
`SimulationView` shows the refusal word for word in the bookmark dialog's
notice. Marking the same MAC target twice prints:

```
a compartment and a height is marked once: a second MAC target naming (<RecordedQuantity.VESSEL_RICH: 'vessel_rich'>, 0.8) would be a row no run could stop at on its own account
```

A user reads a Python enum repr where the dialog's own words would be
"0.8 ×MAC on the vessel_rich compartment", the form `without_mac_target`'s
refusal already uses. Marking one instant twice prints "a second time
bookmark naming 600.0", with no "s". The opening "a compartment and a
height is marked once" also reads oddly, since the subject is plural.

**Why it matters.** `.claude/rules/sources-and-docstrings.md` says a refusal
names what was refused in the reader's terms. This one names it in the code's
terms, at the moment the reader is trying to see which mark they repeated.

**Where.** `src/anesthesia_sim/app/bookmarks.py`: `_refuse_repeats` and its
two callers in `BookmarkSet.__post_init__`.

**Suggested fix.** Let each caller pass a function that names a key in the
reader's terms (the instant with its unit, and the height and compartment as
`without_mac_target` does), and pin both messages whole in
`tests/unit/test_bookmarks.py`. `PL-79PK` pinned the repeated-instant message
as it stands, in `test_the_repeated_instant_refusal_is_pinned_whole`, so that
test changes with the fix. It left the MAC-target message unpinned.

**Suggested triage.** Product lane, P3, effort S; class `ux`. It reaches a
user only after they repeat a mark.

**Done when.** Both refusals name their key in the reader's terms: the instant
with its unit in seconds, and the MAC target as its multiple and compartment, as
`without_mac_target` does. Both messages are pinned whole in
`tests/unit/test_bookmarks.py`.

**Checked 2026-11-22** against `d4e8200`: still applies. `_refuse_repeats` in `app/bookmarks.py` still formats the key with `{key!r}`, so a repeated MAC target still prints the enum repr. A repeated instant now prints "naming 600" rather than "600.0", because instants are whole seconds since #2180, but it still has no unit, as `test_the_repeated_instant_refusal_is_pinned_whole` pins it.

**Done 2026-11-27.** Both refusals now name their mark as the marks list's row does. Marking 600 s twice gives "each instant is marked once, and 10m already has a time bookmark, so a second would stop a run at the same place as the first". Marking a target twice gives "each height on a compartment is marked once, and 0.80 ×MAC on Vessel-rich already has a MAC target, so a second would stop a run at the same place as the first". `_refuse_repeats` takes, from each caller, the key that makes a mark distinct and a function that states the mark. The time is stated by `format_elapsed`, and the target by the new `_stated_height`, which renders the height with `render_mac_multiple` and names the compartment from `run_series.COMPARTMENT_NAMES`. The removal refusal and the missing-reading refusal use `_stated_height` too, so each says 0.80 ×MAC where it said 0.8 ×MAC.

Two choices differ from the brief, and both follow NUREG-0700 Rev. 3, guideline 1.3.3-4, p. 1-39: "Labels should be worded consistently, so that the same item is given the same label whenever it appears" (full text from https://www.osti.gov/servlets/purl/1644018, read 2026-11-27). The done-when asked for the instant "in seconds". The marks list and the run clock show 600 s as "10m", so the refusal does too. The brief suggested the form of `without_mac_target`, which printed the raw height, 0.8. The row prints 0.80, and `render_mac_multiple`'s docstring says why that pair reads as two quantities. The grammar the brief noted is fixed: the sentence now opens "each instant is marked once" and "each height on a compartment is marked once".

The refusal says what is already true and why a second mark adds nothing. It names no next step, because the mark the user asked for is already in the list. It does not suggest removing and re-adding the mark to rename it, because the module that raises it cannot read the Remove button's label (`dashboard_frame` imports `bookmarks`), and a copied label would be a second record of it.

Tests: `tests/unit/test_bookmarks.py::test_the_repeated_instant_refusal_is_pinned_whole`, `::test_the_repeated_mac_target_refusal_is_pinned_whole`, and `::test_the_repeat_refusal_names_the_mark_that_repeats`, which builds a set of three targets so that a message built from the wrong entry reads differently.

Documents checked: `docs/INTERFACE.md` (no passage quotes these refusals; unchanged), `README.md`, `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md` (none names these messages; unchanged).
