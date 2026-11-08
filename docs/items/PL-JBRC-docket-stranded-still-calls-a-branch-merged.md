---
id: PL-JBRC
title: docket stranded still calls a branch merged when one of its commits is only docket record output, which converges byte-for-byte with the base
priority: P2
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
milestone: v0.4.15
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-06
closed: 2026-09-12
pr: 504
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". No paragraph there named it apart from this entry line, so it rested on the section's opening ground, which is quoted in `PL-36R4`'s brief.

> - PL-JBRC (M) docket stranded still calls a branch merged when one of its commits is only docket record output, which converges byte-for-byte with the base — closed in v0.4.15
