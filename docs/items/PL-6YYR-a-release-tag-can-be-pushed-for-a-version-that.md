---
id: PL-6YYR
title: A release tag can be pushed for a version that was never cut, and nothing detects it: v0.4.8 tags main at version 0.4.7 with no release notes and no ROADMAP row
priority: P2
effort: M
status: done
classes: defect, infra
feature: release-process
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py, tools/doc_check.py, .claude/skills/docket/SKILL.md
added: 2026-09-07
closed: 2026-09-26
pr: 1065
verify: grep -q 'def test_a_tag_ahead_of_its_own_cut_is_named' tests/unit/test_doc_check.py && grep -q 'def test_the_printed_tag_line_refuses_before_the_release_has_merged' subprojects/docket/tests/test_release.py && uv run pytest -q subprojects/docket/tests/test_release.py
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

**Triage note, 2026-09-07.** Not a duplicate of the four items that captured
the same `v0.4.8` event. `PL-BKDP` and `PL-KFWL` were the instance and are
closed; `PL-B1DQ` was dropped as the fifth capture of one symptom, and its drop
reason parks exactly this idea here so it would not be lost with the item -
*"`bin/docket release` already refuses to cut while the previous release is
untagged, and the inverse - a tag naming a version no release cut - is equally
decidable and currently guarded by nothing at the moment somebody tags."*
`PL-LT77` is the withdrawal of such a tag and `PL-PNW6` is a later release
re-using its number; this item is the guard none of them carry.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and it was never
partly overtaken - but one of its four bullets was false on the day it was
filed.** Nothing has landed: `release.py`'s only tag rule is `is_untagged` at
`:135`, which judges the *previous* release; no code anywhere dereferences a
tag and reads the commit's `version` or its notes file
(`grep -rn 'refs/tags\|rev-parse.*\^{}\|describe --contains' tools/ subprojects/docket/src/ .github/workflows/`
returns nothing); the skill's tag block still carries the ordering as
surrounding prose; and the item's own `verify:` test does not exist.

**The false bullet is "it cannot be discovered from the tree. Nothing in
`make check` reads tags".** `make check` runs `tools/doc_check.py check`
(`Makefile:191`), which reads `git tag` through `docket.vcs.tags` and errors on
any `vX.Y.Z` tag with no completed row in the version table - and that code was
present at the observed commit `b03a7d0`, having landed in `c57f1ea` on
2026-08-31. The residue is real but narrower, and should be restated as such:
`tags()` reads `git tag --list`, so an **unfetched** tag is invisible, and the
check matches the tag name against the roadmap table rather than against the
commit's own `version` and notes file - which is the miss this item is actually
about.

**Probable duplicate of `PL-KFWL`** (the v0.4.8 tag pushed onto a commit where
no release was cut), which reaches the same guard from the instance rather than
the rule. Read both before starting either.

**Clause (b) landed with `PL-YKSD`, 2026-09-22.** `tools/doc_check.py`'s
`_check_tag_versions` reads every release tag's own `pyproject.toml` and fails
on one declaring another version, naming the tag, the commit it peels to and
the version that tree declares, so a tag pushed ahead of its cut is now
reported across all release tags. What is left is (a), the refusal in
`bin/docket release`, and (c), the tag block. The strongest form of (c) is a
guard in the command itself rather than a sentence beside it: the block's
`git tag -a vX.Y.Z origin/main` tags whatever `origin/main` is when it runs,
which before the merge lands is the commit before the release - `v0.5.3`'s
instance - so the block should run the tag only after `git show
origin/main:pyproject.toml` declares that version. Refused before the push
rather than reported by `doc_check` after it. Captured on `PL-YKSD`'s branch
and folded in here rather than filed apart, since it is this clause.

**Closed 2026-09-26 under `PL-QHCW`.** Clause (b) is now the cut check in
`doc_check`, which fails a tag ahead of or behind its cut whatever version its
tree declares. Clause (c) is the tag block's lookup: before the merge it names
nothing and `git tag` refuses the empty name
(`test_the_printed_tag_line_refuses_before_the_release_has_merged`), which is
the refusal before the push this brief asked for, without a second read of
`pyproject.toml`. Clause (a), a second refusal inside `bin/docket release`, is
declined for `PL-YKSD`'s reason: a second copy of the tag read is free to drift
from the one `doc_check` holds. `verify:` is rewritten from (a)'s test to (b)'s
and (c)'s.
