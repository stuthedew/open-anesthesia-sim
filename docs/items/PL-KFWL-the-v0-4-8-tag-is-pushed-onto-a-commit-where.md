---
id: PL-KFWL
title: The v0.4.8 tag is pushed onto a commit where the release was never cut, so doc_check errors on main for every session
priority: P2
effort: S
status: done
classes: defect, infra
feature: tag-error-names-its-cause
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-07
closed: 2026-09-26
pr: 1065
verify: grep -q 'def test_a_tag_ahead_of_its_own_cut_is_named' tests/unit/test_doc_check.py && python3 tools/doc_check.py check
---

**Problem.** The v0.4.8 tag is pushed onto a commit where the release was never cut, so doc_check errors on main for every session

Found while closing `PL-GBBZ` (clear the four undeclared prose prerequisites),
which needed `python3 tools/doc_check.py check` as the healthy half of a
`verify:` command and could not use it.

`git ls-remote --tags origin` shows `refs/tags/v0.4.8^{}` at `b03a7d0`, which
is `origin/main` itself. But `pyproject.toml` still reads `version = "0.4.7"`,
`ROADMAP.md`'s version table has no v0.4.8 row, and its "Current baseline"
heading still says v0.4.7. So the tag was pushed onto a commit where `make
release VERSION=0.4.8` was never run.

The effect is that `tools/doc_check.py check` hard-errors on `main`:

    ROADMAP.md: git holds v0.4.8, but no row of the version table marks
    v0.4.8 completed; a release that shipped is one this table has to name

**Why it matters.** `doc_check` gates `make check` and CI, so every session's
close-out sweep is red for a reason unrelated to its own work, and every
session has to read the error to find that out. That is `CLAUDE.md`'s third
compounding-friction test - it sits upstream of everything - and its second:
a check that fires every run without changing a decision trains a session to
skim the output where a real failure also appears.

It also removed a `verify:` shape. The store's standard pairing for a
documentation or queue-store item is `python3 tools/doc_check.py check &&
grep -qF ...`, and that healthy half cannot be used while it fails for an
unrelated reason - `PL-GBBZ` had to pair against `bin/docket show` instead.

**Why the ordering inverted.** The `docket` skill's release mode puts the tag
*after* the merge (`git tag -a v0.4.8 origin/main` once `origin/main` is the
merge commit), and `bin/docket release` refuses to cut a release while the
previous one is untagged. Both rules assume tag-follows-cut. Nothing refuses
the reverse, which is the gap: a tag pushed ahead of its cut passes every
guard the project has and lands the error on `doc_check` instead.

**Where.** `ROADMAP.md`'s version table and "Current baseline" heading;
`pyproject.toml`'s version; whatever in `subprojects/docket/` could notice a
tag with no cut behind it.

**Done when.** `main` is green on `python3 tools/doc_check.py check`, either
by cutting v0.4.8 so the tag has a release behind it or by removing the tag;
and a tag pushed ahead of its own cut is refused or reported by name rather
than surfacing as a version-table error.

**Note.** Cutting v0.4.8 is already live work elsewhere - session
`session_01VSM5P7` is idle on "say the word and I'll run `make release
VERSION=0.4.8`" - so the release half of this belongs to that session. What is
this item's own is the guard: nothing stopped the tag going first.

~~**Resolved on the tag side, 2026-09-07, by the second disposition rather
than the first: `v0.4.8` was deleted from the remote, not cut.**~~ **That is
backwards, and the paragraph it led is struck out because acting on it would
now delete a live release tag.** Corrected 2026-09-19 in `PL-6ZQY`'s
crossing-lane sweep: v0.4.8 was resolved by the **first** disposition - it was
*cut*. `git ls-remote --tags origin` returns `refs/tags/v0.4.8` at
`b340e7f`, whose subject is "PL-BKDP: cut v0.4.8 - the gate that was measuring
itself ... (#440)"; `docs/releases/v0.4.8.md` exists; `ROADMAP.md:71` carries
its Completed row; and `pyproject.toml` reads `0.4.28`, not `0.4.7`. So the
version table is consistent because a row was added, which is the opposite of
what this said.

**What was struck, and why it mattered.** The removed paragraph told a later
session that a clone can keep a tag whose remote is gone, and gave
`git tag -d v0.4.8` as the repair. The general lesson is sound and is
`PL-YGF3`'s; the command is not, because the remote still has that tag. Running
it would leave the clone without a tag `tools/doc_check.py`'s `check_tags`
expects at `:2505`, turning a correct tree into a reported error - the exact
cost the paragraph was written to save, inverted.

**How the wrong account survived:** nothing checks a brief's narrative against
the tree. `python3 tools/doc_check.py check` exits 0 with 0 errors and 0
advisories over this file, because every path and identifier it cites exists;
what had gone false was the tense and the outcome, which no check reads. That
is `PL-6ZQY`'s own argument arriving inside one of its own items.

**What is left of this item is the guard, and it is the whole of it now.**
Nothing refused the tag going first, and nothing would refuse the next one.
`bin/docket release` checks that the *previous* release is tagged; no check
runs the other way, so a tag ahead of its cut passes every guard the project
has and lands as a version-table error in `doc_check` - a true error naming
the wrong cause, since the table was not wrong, the tag was. **Done when** is
therefore the second clause only: a tag with no release behind it is refused
or reported by name.

**Left standing 2026-09-19 by `PL-4Q9B`** (record clone trust and the permitted ref
operations), which closed with the finding that its ten members are not one
mechanism. Its placement on the permissions side is now stale - the rationale was that the v0.4.8 tag was wrong on the remote and no session could move it, and the tag is no longer wrong: remote and this checkout both hold it at `93f1902`, `ROADMAP.md` carries its row, and `doc_check` is green. What is left is this item's own second clause, the guard against a tag pushed ahead of its cut, which is release-process work. Nothing here is blocked on that head; this item stands on
its own merits at its own band.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and it was never
partly overtaken: nothing the `Done when` still asks for has landed.** The
guard is wholly absent - `grep -rn 'ahead of its own cut\|tag_ahead' tools/
subprojects/docket/src/docket/` finds nothing, `bin/docket release` still
checks only the *previous* release's tag (`cli.py:1365`, `is_untagged`), the
condition still surfaces as the generic version-table error at
`tools/doc_check.py:2544`, and the item's own `verify:` fails. What was stale
was the account of how the tag side resolved, corrected above.

**Probable duplicate of `PL-6YYR`** (a release tag can be pushed for a version
that was never cut), which describes the same guard from the other end and
whose own test is equally absent. Whoever starts either should read both and
close them together rather than build the guard twice.

**Grouped as `feature: tag-error-names-its-cause`** (`PL-JKML`'s duplicate
sweep, 2026-09-20, confirmed on independent refutation). `PL-KFWL` and
`PL-LT77` are two causes of one symptom: `doc_check` erroring on `main` in
every session over a release tag, with nothing in the message saying which
cause it is. `PL-KFWL` is a tag pushed onto a commit where the release was
never cut - a real fault in the remote. `PL-LT77` is a tag deleted on the
remote that a warm checkout keeps, because `git fetch --tags` does not prune -
a fault in local state only. The two demand opposite actions from the reader,
and today the error cannot tell them apart. The group closes when it can.

**The guard is built, by `PL-YKSD`, 2026-09-22; closing this is one test.**
`tools/doc_check.py`'s `_check_tag_versions` reports a tag pushed ahead of its
cut by name: the tag, the commit it peels to, and the previous version that
commit's `pyproject.toml` still declares, alongside the version-table error
rather than behind it. What this item's own `verify:` still wants is a test
named `test_a_tag_ahead_of_its_own_cut_is_named` pinning its shape - an
annotated tag on the tip of a `_tagged` checkout, whose version table has no
row for it, so the error is anchored on the bare `ROADMAP.md` rather than a
row. `test_a_tag_whose_pyproject_version_disagrees_is_refused` covers the
row-anchored path only.

**Closed 2026-09-26 under `PL-QHCW`.** `doc_check` holds every tag with notes to
the commit that added them and names that commit when a tag is elsewhere, so a
tag one merge past its cut - which still declares its version, and so passed
the version check - is caught: `test_a_tag_ahead_of_its_own_cut_is_named`. The
v0.4.8 instance itself had already been repaired; its tag sits on its cut,
`b340e7ff`.
