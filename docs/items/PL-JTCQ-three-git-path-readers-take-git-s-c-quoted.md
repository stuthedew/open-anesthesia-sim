---
id: PL-JTCQ
title: Three git path readers take git's C-quoted spelling of an unusual path for the path - vcs._commits_by_landing reads log --name-only and doc_check._baseline reads ls-tree, both without -z, and doc_check._deleted_paths unsets quotePath but not -z - so orphaned misses a commit that only adds a non-ASCII file, and the resident-size baseline drops a non-ASCII rule file; latent
status: untriaged
added: 2026-10-06
---

**Problem.** Three git path readers take git's C-quoted spelling of an unusual path for the path - vcs._commits_by_landing reads log --name-only and doc_check._baseline reads ls-tree, both without -z, and doc_check._deleted_paths unsets quotePath but not -z - so orphaned misses a commit that only adds a non-ASCII file, and the resident-size baseline drops a non-ASCII rule file; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.vcs` and `tools/doc_check.py`. Unless told otherwise, git prints a path
holding a byte above 0x7f, a tab, a double quote or a backslash in double
quotes with C-style escapes (git-config's `core.quotePath`); `-z` prints every
path as it is, ended by a NUL. `_commits_by_landing` reads `git log
--name-only` without `-z` and compares each path with `_landing_split`'s sets,
which are read with `-z`. `_baseline` reads `git ls-tree -r --name-only` with
neither. `_deleted_paths` sets `core.quotePath=false`, which leaves a quote or
a backslash still quoted.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15, in
scratch repositories. A commit pushed to a branch after its pull request merged,
adding only `docs/café.md`, was not reported by `orphaned`, which gave no
branch, while the same commit adding `docs/cafe.md` was reported; git printed
the first path as a quoted string of octal escapes. `_resident_baseline` gave
an empty set at `main` for a tree whose one rule file is `.claude/rules/naïve.md`,
where the working-tree measurement read it. `_deleted_paths` keyed a file named
with a double quote by its quoted spelling; no answer changes there, since
`_is_path_citation` refuses those characters. Latent: no tracked path is one
git quotes.

**Re-confirmed 2026-10-11** on main at `16a20a4f`, in a scratch repository:
`git log --name-only` and `git ls-tree -r --name-only` print
`.claude/rules/naïve.md` as `".claude/rules/na\303\257ve.md"`, and
`_resident_baseline` answers `('main', ())` for a tree holding it.

**Generator check.** Not a member of `PL-R417`: one path per record, read whole
in the wrong spelling. Not `PL-TFF9`, the deleted path `_landing_split` leaves
unclassified, nor `PL-MR8Z`, verify's quoted diff header. `PL-PXT7`, open,
holds the same omission in `contrast_check`'s file listing.

**Why it matters.** `orphaned` feeds `stranded` and the digest's left-behind
line, where a commit it never sees is work lost with no report, and the
baseline is what the resident-size measurement compares against. Each answers
from a partial reading without saying so, which the apparatus floor refuses.
Latent until a tracked path holds a byte git quotes.

**Done when.** The three readers ask git for `-z` output and split at NUL, as
`listed_paths` does, pinned by a test with a non-ASCII path for each of the
first two.

**Generator question, open at the 2026-10-11 triage pass; left untriaged for it.**
`PL-JTCQ`, `PL-MR8Z` and `PL-PXT7` misread one fact no head states: git prints an
unusual path C-quoted unless `-z` is given. `PL-MR8Z`'s own Generator check named
the fact at two items; this is the third. About 15 `--name-only` and `ls-tree`
reads without `-z` remain across `vcs.py`, `claims.py`, `verify.py`,
`pr_title_check.py` and `doc_check.py`, all latent, since no tracked path is one
git quotes. It may instead be a post-close instance of `PL-PVW2`, which put `-z`
into `changed_path_args`. **Leaning: a `spent` head**, on `PL-R417`'s reasoning,
filed as its own item naming all three, since this item's fix covers only its own
three readers; settle it before triaging this item. If ordinary: P3, M, `defect`.
