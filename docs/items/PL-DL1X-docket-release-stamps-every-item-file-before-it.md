---
id: PL-DL1X
title: docket release stamps every item file before it bumps the version, so a failure in the bump leaves the store recording a release that did not happen
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-08-31
closed: 2026-09-01
pr: 156
verify: uv run pytest subprojects/docket/tests/test_cli.py -k unstamped
---

**Problem.** `cmd_release` writes the store before it writes anything else:
the `write_item` loop that stamps `milestone:` onto every shipping item runs
first, and `bump_version` runs after it. `bump_version` raises on a version
file that is missing or has no `version` field, and nothing catches it. Hit
while exercising PL-8HJ2 in a scratch repository: the run traced back out of
`bump_version`, and the item file was already stamped `milestone: v0.2.6` for
a release whose version had not moved. The second run then reported "Nothing
to release: no finished work since 0.2.5", because the work it would have
shipped now claims to have shipped already.

**Why it matters.** The recovery is manual and easy to get wrong - unpick the
stamp from every item the failed run touched, with nothing recording which
ones those were. A stamp left behind is a provenance error of the kind the
release path exists to prevent: an item claiming a release it did not go out
in, which the notes for that release do not list.

Rare in the real repository, since `pyproject.toml` is present and well-formed
there. Not rare in the case the tool is most likely to meet a bad version file:
a project adopting docket for the first time.

**Where.** `cmd_release` in `subprojects/docket/src/docket/cli.py`, the block
after the dry-run return.

**Done when.** A release either records everything or records nothing: the
version bump is proved possible before the store is written (read and validate
the version file first, then stamp, then write), and a test covers a version
file `bump_version` will reject, asserting the items come out unstamped.

**Triaged 2026-08-31.** P2, `defect`/`infra`, `dev-tooling`. The `verify:`
command keys on `unstamped` because the Done-when already names that word as
the assertion; `-k stamp` was rejected as the key, since it selects the
existing `test_stamping_records_the_release_without_touching_anything_else`
and would pass today against no work at all.

`dev-tooling` rather than `release-roadmap-seam` deliberately, even though it
was found while exercising `PL-8HJ2`, which carries that feature. Nothing here
touches `ROADMAP.md` or the seam between the release and the roadmap - it is
ordering inside `cmd_release` between two writes - and grouping it there would
make `docket status` report a feature by a name that does not describe a third
of it.

Not admitted to v0.2.8's frozen list: `PL-8HJ2` (`make release` stops mid-way
on the ROADMAP table) is `done` and its own claim holds without this. Neither
new scope for that entry nor its completion, so `ROADMAP.md`'s "What the freeze
closes" sends it to the queue.

**Admitted to v0.2.8's frozen list, 2026-08-31, reversing the paragraph
above,** under the scope test now recorded in `ROADMAP.md`'s "What the freeze
closes": the release script is machinery the release's goal names, so a defect
in it is inside the frozen scope whether or not `PL-8HJ2`'s own claim survives
without the fix. The paragraph above answers the completion question
correctly; that is no longer the question.


**Worked 2026-09-01.** The proof and the write are now separate operations.
`bump_version` is replaced by `prepare_bump`, which reads the version file,
raises on everything it can reject - absent, or carrying no version field -
and returns a `PreparedBump` holding the path and the exact text to put there.
`cmd_release` prepares before the stamping loop and calls `bump.write()` after
it, so a rejected version file returns 1 with nothing written and the failure
named, instead of a traceback out of a half-written store.

The order the Done-when specifies, then, with the validation and the write
unable to disagree: a separate `check_bumpable` would have put the rule that
decides bumpability in two places, and the one that runs first would not be
the one that writes. What remains after preparing is an I/O failure on the
write itself, which no ordering inside one process removes.

**Two tests, both keyed `unstamped`** and both watched failing against the old
code first: a version file with no version field, and no version file at all -
the second being the state a project adopting docket meets. Each asserts exit
1, the failure named in the output, `milestone:` absent from the item file,
and (for the first) that no release notes were written.

**No `milestone:` stamped on this item by hand,** deliberately, and this is
the item that makes the case: `unreleased()` selects `done` items with no
`milestone`, so a hand-stamped one is skipped by the release that actually
ships it. Leaving the field empty is what lets `docket release` stamp it when
v0.2.8 is cut - which is the semantics this fix exists to defend. `PL-HXYY`
(what `milestone:` means on an open gate entry) carries the general question.
