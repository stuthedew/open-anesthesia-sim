---
id: PL-BYN2
title: A project-owner ratification on PL-54V0 exists only on origin/claude/upbeat-rubin-v1dktv, whose session has completed with no pull request open, so the one carrier of that decision is an unmerged branch
priority: P2
effort: S
status: ready
classes: housekeeping
touches: docs/items/PL-54V0-resumed-at-refuses-an-unkeyframed-instant-with.md
added: 2026-09-21
payoff: the owner's ratification stops depending on one unmerged branch surviving, and the gate question it settles stays settled
verify: grep -qF 'project owner, 2026-09-21, ratified' docs/items/PL-54V0-resumed-at-refuses-an-unkeyframed-instant-with.md
---

**Problem.** A project-owner ratification on PL-54V0 exists only on origin/claude/upbeat-rubin-v1dktv, whose session has completed with no pull request open, so the one carrier of that decision is an unmerged branch

**Measured 2026-09-21.** `origin/claude/upbeat-rubin-v1dktv` holds one commit,
`cdbbb5bd`, whose subject records the owner's ratification of the `docs` class
on `PL-54V0`. `main`'s copy of that item contains no ratification. No pull
request is open anywhere in this repository. `bin/docket stranded` does name the
item as edited only on that branch, so the queue is not silent about it - but
the row reads like the five beside it that are merely stale copies (`PL-NPWP`),
and nothing distinguishes a branch carrying a decision of record from one
carrying nothing.

**Why it matters.** This is the failure `PL-KQHN` already cost the project once:
a decision the owner made survives only in a carrier that dies, and a later
session reconstructs it from whatever fragment is left. Here the carrier is a
branch with no pull request, on a forge that deletes merged heads and in a
container that is reclaimed. The ratification also does work no other sentence
does - it records that `docs` was chosen over `safety`, which is what keeps the
current milestone's gate from owing that item a disposition - so losing it does
not merely lose a note, it reopens a settled gate question with nothing to
settle it from.

**Done when.** The ratification is on the default branch's copy of `PL-54V0`.
