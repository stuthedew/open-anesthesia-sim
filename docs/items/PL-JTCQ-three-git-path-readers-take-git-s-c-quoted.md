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

**Generator check.** Not a member of `PL-R417`: one path per record, read whole
in the wrong spelling. Not `PL-TFF9`, the deleted path `_landing_split` leaves
unclassified, nor `PL-MR8Z`, verify's quoted diff header. `PL-PXT7`, open,
holds the same omission in `contrast_check`'s file listing.

**Done when.** The three readers ask git for `-z` output and split at NUL, as
`listed_paths` does, pinned by a test with a non-ASCII path for each of the
first two.
