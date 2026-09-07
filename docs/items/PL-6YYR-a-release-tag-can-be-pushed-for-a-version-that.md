---
id: PL-6YYR
title: A release tag can be pushed for a version that was never cut, and nothing detects it: v0.4.8 tags main at version 0.4.7 with no release notes and no ROADMAP row
status: untriaged
added: 2026-09-07
---

**Problem.** Observed on `origin` at 2026-09-07 17:35 UTC:

    refs/tags/v0.4.8^{}                 b03a7d0   = origin/main HEAD
    origin/main:pyproject.toml          version = "0.4.7"
    origin/main:docs/releases/          ...v0.4.6.md, v0.4.7.md - no v0.4.8.md
    origin/main:ROADMAP.md              table ends at v0.4.7, "current baseline"
    bin/docket release --dry-run        "12 finished item(s) since 0.4.7"

`v0.4.8` names a commit that carries no release. Nothing was bumped, no notes
were generated, no `milestone: 0.4.8` was stamped on any of the twelve items,
and the store still believes 0.4.7 is the baseline. The tag asserts a release
that does not exist.

**Why it matters, and why it is worse than the gap it mirrors.**
`bin/docket release` already refuses to cut while the *previous* release is
untagged, because that leaves a span `git describe --contains` cannot resolve.
This is the same failure with the operations reversed, and it is not merely
symmetrical:

- `git describe --contains` now places every commit up to `b03a7d0` in a
  v0.4.8 whose notes describe nothing. The answer is wrong rather than absent,
  which is the silent-wrong-answer case `CLAUDE.md` treats as the strongest
  reason to interrupt.
- The guard does not fire on the way out either. v0.4.7 *is* tagged, so
  `bin/docket release` will cut 0.4.8 happily - and the cut commit lands
  *after* the tag, so the tag would then point at a commit preceding the entire
  release it names. Every statement the release notes make would fall outside
  its own tag.
- It cannot be discovered from the tree. Nothing in `make check` reads tags,
  and the only signal is a `git ls-remote --tags` a session has no reason to
  run.

**Where the old argument does not apply.** The baseline-tag advisory was
removed in v0.3.4 because a local checkout cannot distinguish a release never
tagged from one tagged since the last fetch - a false positive on a stale
clone. This check has no such failure mode, because it is the opposite
direction: a tag that *exists* is a fact, and what is being asserted about it -
that the commit it names carries the matching `version` in `pyproject.toml` and
a `docs/releases/<tag>.md` - is decidable from the fetched tag alone. Absence
of a tag stays unjudgeable; presence of a wrong one does not.

**Where.** `subprojects/docket/src/docket/release.py` for the refusal, and
whichever of `make check` or CI runs with tags fetched for the report - the
rule is small and exact, so it belongs in code rather than in prose:
for each `refs/tags/vX.Y.Z`, the commit it dereferences to must carry
`version = "X.Y.Z"` and a `docs/releases/vX.Y.Z.md`. A tag naming a version
ahead of its commit is the error this item is about; a tag behind is a rewrite
artifact and is `PL-YGF3`'s case.

**How it happened is worth recording**, because the fix has an instruction half.
The `docket` skill hands the project owner three tag commands to paste, and is
explicit that a session must not run them itself (`PL-N936`: a session's tag
push fails in a way that looks like success). What it does not say is that they
are only ever run *after* the cut has merged - the ordering is implicit in the
surrounding prose and was lost when the commands were read on their own.

**Done when.** `bin/docket release` refuses to cut a version whose tag already
exists on a commit that does not carry it, naming the tag and what is missing;
a check reports the same condition across all release tags where they are
available; and the `docket` skill's tag block states the ordering on the block
itself rather than around it.

**Note, 2026-09-07, added on recovery (`PL-1VFK`).** The instance above is
cleared: the `v0.4.8` tag was deleted from `origin`, `git ls-remote --tags
origin` now stops at `v0.4.7`, and `make doc-check` reads `0 errors, 0
advisories`. The finding is unaffected - nothing detected the tag while it
stood, and nothing would detect the next one. `PL-LT77` covers the separate
half, that a deleted tag survives in checkouts which fetched it first.
