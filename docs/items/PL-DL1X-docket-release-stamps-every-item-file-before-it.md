---
id: PL-DL1X
title: docket release stamps every item file before it bumps the version, so a failure in the bump leaves the store recording a release that did not happen
status: untriaged
added: 2026-08-31
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
