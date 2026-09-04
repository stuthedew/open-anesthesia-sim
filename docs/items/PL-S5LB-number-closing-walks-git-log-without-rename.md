---
id: PL-S5LB
title: _number_closing walks git log without rename detection, so an item whose file was renamed after it closed recovers the renaming commit's pull request instead of its own
status: ready
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_renamed_item_file_recovers_its_own_pull_request' subprojects/docket/tests/test_vcs.py
added: 2026-09-04
---

**Problem.** `_number_closing` (`subprojects/docket/src/docket/vcs.py:1053`)
recovers a closed item's pull request by walking `git log` over that item's
file. The walk carries no rename detection, so it stops at the commit that
renamed the file and reports *that* commit's pull request number. An item file
is renamed whenever its title is edited - `docket`'s filenames are slugs of the
title - so this fires on an ordinary edit rather than on anything unusual.

**Why it matters.** The number it recovers is wrong, and `docket record` writes
a recovered number into the item without a human reading it. `pr:` is the only
surviving link from a closed item to the change that implemented it, because
`commit:` was retired (`PL-T63T`) on the grounds that a squash-merge discards
the branch commit while the pull request outlives it. A wrong number is
therefore worse than a missing one: it points a later reader at a change that
did not do the work, and nothing in the store contradicts it. This is the same
class of failure as `PL-GW37` (a rider closure recovering the wrong pull
request, fixed in #285) arriving through a different door - the walk's inputs
rather than its subject parsing.

**Where.** `subprojects/docket/src/docket/vcs.py`, `_number_closing`'s `git log`
invocation; the fix is rename detection on the walk (`--follow`, or the
equivalent that survives the `-1`/`--format` shape already in use).
`subprojects/docket/tests/test_vcs.py` for the regression test.

**Done when.** An item whose file was renamed after the commit that closed it
recovers the pull request that closed it, not the one that renamed it, and a
test in `test_vcs.py` fixes that case. Confirm the fix survives the
`_work_already_on_base` path too, which asks a related question of the same
history.
