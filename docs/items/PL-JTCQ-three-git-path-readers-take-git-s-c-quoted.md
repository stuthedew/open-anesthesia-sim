---
id: PL-JTCQ
title: Three git path readers take git's C-quoted spelling of an unusual path for the path - vcs._commits_by_landing reads log --name-only and doc_check._baseline reads ls-tree, both without -z, and doc_check._deleted_paths unsets quotePath but not -z - so orphaned misses a commit that only adds a non-ASCII file, and the resident-size baseline drops a non-ASCII rule file; latent
priority: P3
effort: M
status: done
classes: defect
touches: subprojects/docket/src/docket/vcs.py, tools/doc_check.py, subprojects/docket/tests/test_vcs.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-06
closed: 2026-10-18
payoff: orphaned and the resident-size baseline read a non-ASCII path as the path it is, so a commit adding one is not lost from stranded and a rule file is not dropped from the measurement
verify: grep -q 'def test_a_non_ascii_path_is_read_as_git_wrote_it' subprojects/docket/tests/test_vcs.py && grep -q 'def test_the_resident_baseline_reads_a_non_ascii_rule_file' tests/unit/test_doc_check.py
falsifies: assert "-z" not in args
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

**One assertion declared falsified, 2026-10-18.** `falsifies:` names the
guard in `subprojects/docket/tests/test_vcs.py`'s `_log_names`, which refuses
a `--name-only` walk sent with `-z` because the fake modelled only the bare
form. `_commits_by_landing` now sends `-z`, so the fake models that form and
refuses the bare one instead. It is declared on the default branch because
`verify` honours only the base's copy.

[superseded 2026-10-12: answered below, a `spent` head filed as `PL-4YDJ`] **Generator question, open at the 2026-10-11 triage pass; left untriaged for it.**
`PL-JTCQ`, `PL-MR8Z` and `PL-PXT7` misread one fact no head states: git prints an
unusual path C-quoted unless `-z` is given. `PL-MR8Z`'s own Generator check named
the fact at two items; this is the third. About 15 `--name-only` and `ls-tree`
reads without `-z` remain across `vcs.py`, `claims.py`, `verify.py`,
`pr_title_check.py` and `doc_check.py`, all latent, since no tracked path is one
git quotes. It may instead be a post-close instance of `PL-PVW2`, which put `-z`
into `changed_path_args`. **Leaning: a `spent` head**, on `PL-R417`'s reasoning,
filed as its own item naming all three, since this item's fix covers only its own
three readers; settle it before triaging this item. If ordinary: P3, M, `defect`.

**Answered at the 2026-10-12 triage pass: a `spent` head, filed as `PL-4YDJ`**,
with `root-cause-of: PL-JTCQ, PL-MR8Z, PL-PXT7` and the fact as its `misread:`,
how git spells a path in its output and when it quotes one. No head stated it,
and `PL-PVW2`'s fact is a different one. This item stays its own three readers
at its own band; the head carries the rest of the reads.
