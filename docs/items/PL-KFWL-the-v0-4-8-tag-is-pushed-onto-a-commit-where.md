---
id: PL-KFWL
title: The v0.4.8 tag is pushed onto a commit where the release was never cut, so doc_check errors on main for every session
status: untriaged
added: 2026-09-07
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

**Resolved on the tag side, 2026-09-07, by the second disposition rather than
the first: `v0.4.8` was deleted from the remote, not cut.** `git ls-remote
--tags origin` no longer returns it, `origin/main` is unmoved at `b03a7d0`,
`pyproject.toml` still reads `0.4.7`, and `python3 tools/doc_check.py check`
is back to 0 errors and 0 advisories. So the release was never cut and no
longer claims to have been; the version table is consistent again because the
tag withdrew, not because a row was added.

**One consequence worth knowing, because it costs a session an hour
otherwise.** A clone that fetched while the tag existed keeps it: `git fetch`
does not delete a local tag whose remote is gone, so `doc_check` went on
reporting the error here after the remote was already clean - the same shape
as `PL-YGF3` and `PL-F48B`, arrived at by a deleted tag instead of a rewritten
history. The repair is to delete that one tag by name, never a prune:

    git tag -d v0.4.8

`git fetch --tags --force` does not do it either; `--force` updates a tag, it
does not remove one the remote dropped, and `--prune-tags` implies `--prune`,
which `.claude/hooks/no-prune-guard.sh` refuses for good reason.

**What is left of this item is the guard, and it is the whole of it now.**
Nothing refused the tag going first, and nothing would refuse the next one.
`bin/docket release` checks that the *previous* release is tagged; no check
runs the other way, so a tag ahead of its cut passes every guard the project
has and lands as a version-table error in `doc_check` - a true error naming
the wrong cause, since the table was not wrong, the tag was. **Done when** is
therefore the second clause only: a tag with no release behind it is refused
or reported by name.

