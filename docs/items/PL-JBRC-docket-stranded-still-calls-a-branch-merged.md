---
id: PL-JBRC
title: docket stranded still calls a branch merged when one of its commits is only docket record output, which converges byte-for-byte with the base
priority: P2
effort: M
status: blocked
blocked-by: PL-R808
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-06
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_branch_whose_only_landed_commit_is_docket_record_output_is_not_merged' subprojects/docket/tests/test_vcs.py
---

**Problem.** `PL-5TRV` narrowed `orphaned`'s merge verdict from "the base holds
some of what this branch introduced" to "the base took one of this branch's
commits **whole**", because two sessions running `bin/docket record` write
byte-identical lines and each then holds content the other landed. That closes
the observed case (`#372`) and leaves one shape open: a branch one of whose
commits is *entirely* `docket record` output. Every path of that commit agrees
with the base by convergence rather than by merge, so it reads as a commit the
base took whole, and a branch also carrying a wholly outstanding commit is
reported as having had its pull request merged while it is live.

**Why it matters.** The recovery the `docket` skill prescribes for that section
deletes the branch ref and restarts it on `main`, so a false verdict there
discards the head an open pull request was raised against. That is the same
harm `PL-5TRV` records, reached by a narrower route.

**Why it is not already impossible.** The skill tells a session to let a
`record` write ride a commit it is already making rather than compose one for
it (`PL-QTSB`), which is what keeps the shape rare - but that is prose a session
follows, not a rule anything enforces, and `make fix` runs `bin/docket record`
on its own.

**Approach, and the open question.** Three candidates, and the choice is the
work:

- **Discount a commit whose whole diff is `pr:` lines** when deciding whether
  the base took it whole, the way `branches_in_flight` already discounts a
  commit whose whole diff sits inside `docs/items/` (`PL-X3WZ`). Cheapest, and
  it reuses a reading the module already makes.
- **Require the wholly landed commit to be older than the wholly outstanding
  one**, which is the true shape - a merge takes a prefix and the push comes
  after. Does not help here on its own: a `record` commit is usually the older
  of the two.
- **Match a squash subject on the base against the branch's leading ids**,
  which is the signal `docket record`'s own recovery already reads. Strongest
  and the largest; it fails for a branch whose commits carry no id.

**Done when.** A branch whose only wholly landed commit is `docket record`
output is not reported as having had its pull request merged, with a regression
test in that shape.

**Found.** `PL-5TRV`'s own fix, 2026-09-06, as the residual case its docstring
and `subprojects/docket/README.md` both name.

**Blocked on `PL-R808` 2026-09-12**, by the workflow-lane consolidation the
project owner approved. This item is a false positive of the *content*
comparison in `vcs.orphaned` / `_base_blobs`, and `PL-VV4D` has since decided
that the comparison is replaced by an exact `refs/pull/<n>/head` test built in
`tools/`. Working this one now means patching the heuristic that is about to be
replaced - and the cluster it belongs to runs at r = 1.05, generating more work
than it closes, precisely because each such patch lets the next shape through.

It is blocked rather than merged. Its brief carries an observation the others
do not, and the `PL-6ZQY` sweep refuted 56 of 62 proposed merges on exactly
that ground - the surviving brief did not cover what it was said to absorb. So
nothing here is folded into anything; this item simply stops being startable
until the exact check exists.
