---
id: PL-5HM5
title: The bookmark dialog's refusal of a repeated MAC target names the crossing by a Python repr, '(<RecordedQuantity.VESSEL_RICH: 'vessel_rich'>, 0.8)', and the repeated-instant refusal names its instant with no unit
priority: P3
effort: S
status: ready
classes: ux
touches: src/anesthesia_sim/app/bookmarks.py, tests/unit/test_bookmarks.py
added: 2026-10-17
payoff: a learner who marks the same MAC target or instant twice is told which mark in the dialog's own words, not in a Python repr or a unitless number
verify: grep -q 'def test_the_repeated_mac_target_refusal_is_pinned_whole' tests/unit/test_bookmarks.py
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

A learner reads a Python enum repr where the dialog's own words would be
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
learner only after they repeat a mark.

**Done when.** Both refusals name their key in the reader's terms: the instant
with its unit in seconds, and the MAC target as its multiple and compartment, as
`without_mac_target` does. Both messages are pinned whole in
`tests/unit/test_bookmarks.py`.
