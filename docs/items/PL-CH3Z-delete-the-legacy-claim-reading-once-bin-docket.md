---
id: PL-CH3Z
title: Delete the legacy claim reading once bin/docket flight prints legacy refs: 0
priority: P2
effort: S
status: done
classes: defect
feature: claim-record
touches: subprojects/docket/README.md, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/tests/test_claims.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_git_runner.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_vcs.py, tests/unit/test_branch_id_check.py, tools/branch_id_check.py
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
closed: 2026-09-26
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: ! grep -q -i legacy subprojects/docket/src/docket/claims.py && ! grep -q -i legacy tools/branch_id_check.py
---

**Problem.** Delete the legacy claim reading once bin/docket flight prints legacy refs: 0

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

Remove the legacy reading and the CI skip for legacy commits. Starts only once `flight` prints `legacy refs: 0`, which is a fact about the refs rather than a date.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- No legacy reading remains in `claims.py` or `tools/branch_id_check.py`.

**Build order.** After `PL-N162`, `PL-J9S0`.

**Readied 2026-09-26.** `bin/docket flight` on `origin/main` `35532902` prints `legacy refs: 0`, and `PL-N162` and `PL-J9S0` are both done, so the start condition holds and the `blocked-by` edge is cleared.

**Closed 2026-09-26.** The old rule is gone from `claims._events`, which reads
every commit by its trailers alone, and from `claims.work_outside_queue`
(`work_under_record` until now), which no longer skips a commit whose tree
predates the record. Four things went with it, each dead once no hold could
read as legacy: `CUTOVER_MARKER` and `claim`'s refusal on a tree without it,
since a claim written anywhere is now read; `Hold.legacy`,
`Holdings.legacy_refs` and `flight`'s `legacy refs:` line, which could only
ever print 0; `claiming._recorded` and the tie test on one shared commit,
since a recorded claim binds to the one branch its token names; and
`render._reached_by` with `show`'s grouping of the order by commit, for the
same reason. `branch_id_check.ahead_of` reads the order whole. `touches`
widened from three files to the fifteen the deletion reached, because the
`legacy` flag had readers in `claiming`, `render`, `cli` and the CI check's
tests. The tests that modelled a claim by an id-leading subject on a
marker-less tree now record a `Claim:` trailer, as a session would have, and
two regression tests pin the deletion: a commit made before the record claims
nothing and its branch is an `unclaimed:` row (`test_claims`), and CI refuses
such a branch (`test_branch_id_check`). `ROADMAP.md`'s v0.5.10 notes still
describe the reading as pending; they record that cut and were left as they
stand.
