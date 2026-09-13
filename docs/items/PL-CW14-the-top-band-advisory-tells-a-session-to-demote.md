---
id: PL-CW14
title: The top-band advisory tells a session to demote work docket check itself pins to P1
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.15
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-03
closed: 2026-09-13
pr: 506
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_an_overfull_top_band_says_how_much_of_it_is_demotable' subprojects/docket/tests/test_checks.py
---

**Problem.** `checks.py:849` raises an advisory when the top band exceeds
`top_band_limit`, and its remedy sentence reads "demote what is not genuinely
next". The same file refuses to seat a `safety`- or `science`-classed item
below P1 (`test_safety_work_may_not_sit_in_a_low_band`). So for most of what
makes this band large, the prescribed action is one `docket check` would reject
as an error.

Measured on the store the moment the advisory first fired, 2026-09-03: P1 held
13 items, and **12 of the 13 carry `safety` or `science`**. The single
unpinned one is `PL-WB0X` (split `simulation_view.py` — formatting and chart
series are not the view's job), which is the top of `docket next` and the
declared blocker of three other items, so it is the last thing anyone would
demote. The advisory therefore names an action that is unavailable on twelve
items and self-defeating on the thirteenth.

**Why it matters.** `CLAUDE.md`: "A check that fires every run without changing
a decision is a defect in the check — it costs attention forever and trains a
session to skim the output where a real advisory also appears." That is the
trajectory here, not a risk of it: the band cannot fall below 12 until two
pinned items close, so this advisory now prints on every `make check` with no
action available to clear it. It sits directly above the `verify:` advisory,
which is the one a session is meant to act on.

The count itself is not the defect and must not be silenced. `docket.toml`'s
`top_band_limit` comment already considered exempting safety-classed items from
the count and rejected it, correctly: "a band that grows to twenty safety items
is a genuine problem a session should be told about". Reporting the split is
not the same as exempting — it is what turns the same number into something a
session can act on or knowingly accept.

**Where.**

- `subprojects/docket/src/docket/checks.py:848-853` — the `len(top) >
  config.top_band_limit` branch and its message. The pin it contradicts is the
  safety-band rule earlier in the same file.
- `subprojects/docket/tests/test_checks.py:420`
  (`test_an_overfull_top_band_is_an_advisory`) — the existing coverage, which
  asserts the advisory fires and says nothing about what it advises.
- `docket.toml` — the `top_band_limit` comment records the decision this fix
  must not undo. Do not change the threshold as part of this.

**Approach.** Message only; leave the threshold and the count alone. Split the
band by whether an item's classes intersect `safety_classes`, and say so:
roughly "P1: 13 items, past the 12 a session can choose between at a glance;
12 are pinned there by a safety or science class, 1 is demotable". Where
nothing is demotable, drop the demotion clause rather than printing advice
nobody can take — the honest message then is that the band is large because
that much safety work is open, which is the debt gate's signal and reads as
one.

**Done when.** The overfull-top-band advisory reports how many of the band are
class-pinned and how many are demotable; it prescribes demotion only when at
least one item is demotable; `test_an_overfull_top_band_says_how_much_of_it_is_demotable`
covers the all-pinned case; `top_band_limit` is unchanged; and `make check`
passes.
