---
id: PL-XCYB
title: A provenance check must refuse to answer in a shallow checkout, not answer wrongly
priority: P2
effort: S
status: done
classes: defect, infra
feature: public-history
milestone: v0.2.8
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests, subprojects/docket/README.md, docs/items
added: 2026-08-30
closed: 2026-08-30
pr: 90
verify: uv run pytest subprojects/docket/tests/test_vcs.py subprojects/docket/tests/test_checks.py -q
---

**Problem.** A web session's checkout is shallow. Measured on `main` at
`9feab98` on 2026-08-30: `git rev-parse --is-shallow-repository` returns
`true`, and `git rev-list --count origin/main` reports 192 commits where
`ROADMAP.md` records 214. Every `commit:` hash recorded before the graft point
therefore fails `git rev-parse --verify`, and a check that reads that failure
as "this hash does not exist" reports sound provenance as broken.

Found while handing off PL-ZQ9C (record an item's pull request, so provenance
survives squash-merge). Checking 40 recorded hashes in this container returned
eight unresolvable, including `bc5f823` three times - all of them real commits
that a full clone resolves.

**Why it matters.** This is the failure mode the two provenance items are
about to build. PL-68XK (check that every recorded commit hash resolves) is
specified as a reachability test, and PL-ZQ9C's approach is to assert that some
commit on main carries `(#N)` in its subject. Both are true statements about a
full clone and both go wrong in the same direction here: they would fail loudly
against correct data, in exactly the environment most sessions run in, which
trains a reader to ignore the check.

`ROADMAP.md` already records this trap for a different measurement - the
v0.1.0/v0.2.0 tag gap, where a shallow checkout made `main` look like it had
three unrelated roots - and keeps the superseded reasoning precisely because
"a shallow checkout will produce it again for anyone who repeats the
measurement". It has now produced it again.

**Where.** `subprojects/docket/src/docket/vcs.py`, which owns the discipline of
saying nothing when git cannot answer, and `checks.py`, which consumes it.

**Approach.** A shallow checkout is worse than a bare one, and the existing
discipline does not cover it: in a bare checkout git cannot answer and the
check stays silent, while in a shallow checkout git answers confidently and is
wrong. So `vcs.py` needs to detect the condition -
`git rev-parse --is-shallow-repository` - and any provenance check must
downgrade to "cannot determine" rather than "failed" when it holds. Say so in
the output, so a reader knows the difference between a check that passed and a
check that declined.

**Do not** unshallow the checkout as the fix. That would make `docket check`
fetch the network on a path that today runs from a bare tree, which is the
property `vcs.py` was written to preserve.

**In v0.2.8's frozen list.** Added after the freeze under the rule the project
owner stated on 2026-08-30: a freeze closes new scope, not the completeness of
a fix. This is not new scope - it is what `PL-ZQ9C` (record an item's pull
request, so provenance survives squash-merge) needs in order to ship a check
that is right. Recorded in `ROADMAP.md` beneath that list, with what it
completes.

**Done when.** `docket check` run in a shallow checkout reports that it cannot
verify recorded provenance, rather than reporting it invalid; a test covers the
shallow case explicitly; and the behaviour in a full clone is unchanged.


**Closed 2026-08-30**, retroactively: the work landed in pull request 90
(`1561b2a`) alongside PL-ZQ9C, which it was deliberately paired with, and the
`status` was never moved off `ready`. Verified against the "Done when" above
rather than assumed - `_check_provenance` records a declined history as a check
that did not run and judges no item, `test_a_shallow_clone_declines_and_says_why`
covers the shallow case explicitly, the full-clone path is unchanged, and this
item's own `verify:` command passes (65 tests). The gap that let a finished item
sit open is PL-3CBS (docket has no way to notice that an open item's work
already landed on main).
