---
id: PL-K4BN
title: Backfill the eight pr: numbers origin/main is owed, and stop the group being 8 of the 13 advisories every session now reads past
priority: P3
effort: S
status: done
classes: housekeeping
feature: commit-provenance
milestone: v0.5.3
touches: docs/items
added: 2026-09-22
closed: 2026-09-22
pr: 886
payoff: the eight advisories that were 8 of 13 in make docket clear, so the section a session skims again contains only findings that need judgment
verify: test "$(grep -l "^pr:" docs/items/PL-2JRC-*.md docs/items/PL-44DG-*.md docs/items/PL-G7ST-*.md docs/items/PL-J3WK-*.md docs/items/PL-JYTJ-*.md docs/items/PL-PBP5-*.md docs/items/PL-PHK4-*.md docs/items/PL-T5K1-*.md | wc -l)" = 8
---

**Problem.** Backfill the eight pr: numbers origin/main is owed, and stop the group being 8 of the 13 advisories every session now reads past

**Problem.** Eight items are marked `done` on `origin/main` and record no `pr`.
`bin/docket check` reports each as its own advisory, so the group is **8 of the
13** advisories `make docket` printed on 2026-09-22 - the largest single block,
and all of it one deterministic command.

The advisory's own wording is why they accumulated: it says `docket record`
"writes it - and every other number the base is owed - in one pass", and to
"let it ride the commit you are already making rather than composing one". That
is right while commits are flowing, and it silently becomes wrong once nobody
has a commit in hand. Six of the eight merged between 21:35 and 00:36 on
2026-09-21/22, in a window where every session that could have carried them had
already pushed. A session arriving after that reads eight advisories it is told
not to act on by themselves.

That is `CLAUDE.md`'s routed-around test rather than a tidiness complaint: an
advisory block nobody acts on trains a session to skim the section where a real
one is printed, and the same run also carried the stale-slug advisory
(`PL-843V`), the closed-thread advisory in `docs/WORKING_NOTES.md`, and two
`payoff`/recommendation advisories that do need judgment.

**What `pr` is for.** `bin/docket release` reads it to write release notes, and
`docket check` recovers a closed item's pull request from the newest squash
subject naming its id. Recorded now, from merge commits that exist; the
recovery gets harder, not easier, with time.

Recorded, and verified against `origin/main`'s squash subjects:

| Item | `pr` | Squash subject on `origin/main` |
| --- | --- | --- |
| `PL-JYTJ` | 881 | `PL-JYTJ: cut v0.5.2, and prove core's only movement docstring-only (#881)` |
| `PL-J3WK`, `PL-PBP5` | 882 | `PL-J3WK, PL-PBP5: close the make check / CI gate seam in both directions (#882)` |
| `PL-PHK4`, `PL-T5K1` | 883 | `PL-PHK4, PL-T5K1: audit the instruction set's dated assertions, on a 90-day threshold (#883)` |
| `PL-G7ST` | 884 | `PL-G7ST: correct PL-M7W1's #880 section ... (#884)` |
| `PL-44DG` | 885 | `PL-44DG: count the two resident payloads the size gauge could not see (#885)` |
| `PL-2JRC` | 880 | `PL-2JRC: triage the untriaged captures standing in the queue on 2026-09-21 (#880)` |

Two subjects lead with two ids each, which is the one-id-grammar rule working:
`docket check` attributes a rider to the pull request whose subject names it,
so `PL-PBP5` and `PL-T5K1` recover correctly rather than landing on their own
capture commits.

**Not a proposal to change the advisory.** Whether the "let it ride" wording
should say something different when the group passes some size is a real
question and not this item's; it is left open deliberately rather than answered
in a housekeeping pass.
