---
id: PL-2M4X
title: PL-J45M's verify and touches name tests/unit/test_docket_digest_hook.py, a shell-hook test file that cannot exercise release.py, so its pytest half proves the wrong tree and a worker would edit the wrong file
priority: P3
effort: S
status: ready
classes: defect
feature: release-roadmap-seam
touches: docs/items
added: 2026-09-16
verify: bin/docket check && grep -q 'subprojects/docket/tests/test_release.py' docs/items/PL-J45M-*.md
---

**Problem.** PL-J45M's verify and touches name tests/unit/test_docket_digest_hook.py, a shell-hook test file that cannot exercise release.py, so its pytest half proves the wrong tree and a worker would edit the wrong file

**Found 2026-09-16 while closing `PL-VFD8` and `PL-188T`**, which had the same
wrong path and were corrected as part of that work.
`tests/unit/test_docket_digest_hook.py` tests `.claude/hooks/docket-digest.sh`
end to end against real git fixtures; its own docstring says the digest itself
"is `bin/docket digest`, tested with the rest of that package". It imports no
`docket` module and holds no `release_offer` test, so the pytest half of
`PL-J45M`'s command cannot fail for the reason the item is about. The release
tests are in `subprojects/docket/tests/test_release.py`.

**Not vacuous, which is why this is `S` rather than urgent.** The command's
second half - `! grep -q "supported = plan.beat != IMPLEMENT or plan.own_scope
is not None" subprojects/docket/src/docket/release.py` - is a real
specification and still exits 1 today, so the command as a whole fails
correctly. What is wrong is the half the skill's paired shape exists for: "the
pytest half proves the file's suite healthy", and here it proves a different
suite's health. `touches` is the more expensive half of the error - a worker
commissioned on `PL-J45M` would be told its test file is the shell-hook one,
and `docket verify` reads `touches` to decide whether a delegated branch
exceeded its commission.

**Done when** `PL-J45M`'s `touches` and `verify` name
`subprojects/docket/tests/test_release.py`, the command has been run and
watched fail for the right reason, and the `! grep` half is left exactly as
written - it is what keeps the item from reading as closeable while
`_release_due`'s positional classifier stands.

**Why it matters.** `touches` is read by two mechanisms that act on it without
a reader in the loop. `bin/docket verify` audits a delegated branch's diff
against it, so a worker who edits the file the item is actually about -
`subprojects/docket/tests/test_release.py` - is reported as having exceeded its
commission, while one who edits the shell-hook test it names is not. And
`bin/docket concurrent` answers from it, so every collision prediction this
item takes part in is made against a file nobody will touch. The `verify:`
half is the cheaper error of the two, because a command that proves the wrong
tree still fails for its own reason here and so is not silently green - but it
proves nothing about `release.py`, which is the whole subject of `PL-J45M`.

**Triaged `P3`, at `PL-J45M`'s own band.** Repairing the metadata ahead of the
item it describes buys nothing: `PL-J45M` (the positional `_release_due`
classifier) is `P3` and not near the top of the queue, and the skill's rule is
that a wrong `verify:` is repaired as its item is started. This is filed so
that the repair is not re-derived at that moment.
