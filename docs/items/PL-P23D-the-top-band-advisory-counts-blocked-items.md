---
id: PL-P23D
title: The top-band advisory counts blocked items, which cannot answer 'what next' and are added by the checker's own blocker-band rule
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.3.4
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py
added: 2026-09-03
closed: 2026-09-03
pr: 269
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_top_band_padded_with_blocked_items_is_not_overfull' subprojects/docket/tests/test_checks.py
---

**Problem.** The top-band advisory counted every item in the band, blocked ones
included. `docket.toml` says what the limit is for — "past this, the top band
stops answering 'what next?' at a glance" — and a blocked item is not a choice a
session can make, so counting it measures something other than what the limit
means.

**Why it matters.** Two of the project's own rules make this reachable without
anybody over-prioritizing anything, which is what turns a mis-measure into an
advisory nobody can act on:

- `checks.py` refuses to seat a `safety`- or `science`-classed item below `P1`,
  and every `P1` this project holds carries one of those classes. So no item in
  the band can be demoted to drain it.
- `_check_blocked_band` refuses a `P1` that waits on a `P2`, and correctly:
  whatever gates safety-classed work is that work's schedule. So gating a
  safety item on a `feature` item *raises the blocker into the band* rather
  than lowering the blocked item out of it.

Worked example, 2026-09-03: `PL-ZRSP` (plot the F_A/F_I ratio) was blocked on
`PL-DR1Z` (record the control-input timeline) per `PL-9K7K`, `PL-DR1Z` was
raised `P2` → `P1` because the checker requires it, and the band went to
thirteen — one past the limit, with twelve members class-pinned there and the
thirteenth a `feature, ux` item that arrived by dependency. Nothing could be
demoted, so the advisory would have fired in every session from then on.
`CLAUDE.md` names that exact failure: an advisory firing every run that nobody
can act on trains a session to skim the output where a real one also appears.

**Where.** `subprojects/docket/src/docket/checks.py`, the size branch of
`_check_band_shape` (the two advisories below it, on open decisions and on
process work, are ratios within the band and are left alone).

**Done when.** The size advisory counts only startable items, says how many
blocked ones it did not count, and a test holds it.

**Worked.** `startable = [item for item in top if item.status != "blocked"]`,
counted against the limit, with the held-back number named in the message so the
band's real size is still visible. Measured on this store: thirteen in the band,
nine startable, four blocked — so the advisory correctly stops firing. The test
was watched failing first against the unmodified checker.

`docket triage` states the same rule back to a session, and it counted the band
the other way, so it moved with the advisory - "holding 3 startable of the 12"
rather than "holding 3 of the 12". Two numbers for one rule is worse than either
of them, and that line is read at exactly the moment somebody is deciding what
band to put an item in.

Deliberately narrow: `_top_band` itself is unchanged, so a band consisting only
of blocked items is still that band rather than silently falling through to the
next one. The two advisories below the size branch - open decisions, and process
work outnumbering product - are ratios within the band and were left alone.

**Found.** 2026-09-03, closing `PL-9K7K` — the fix for one item's ordering
surfaced it immediately, which is the sense in which it was already live.
