---
id: PL-4YDJ
title: Git path reads outside changed_path_args take git's C-quoted spelling of an unusual path for the path: about 15 --name-only, ls-tree and diff reads across vcs.py, claims.py, verify.py, pr_title_check.py and doc_check.py ask for no -z, the fact PL-JTCQ, PL-MR8Z and PL-PXT7 each misread at their own readers
status: untriaged
added: 2026-10-12
root-cause-of: PL-JTCQ, PL-MR8Z, PL-PXT7
generator: spent - every member was found by a sweep or a review and none in use, and no tracked path is one git quotes, so ordinary work cannot meet one
misread: How git spells a path in its output, and when it quotes one
---

**Problem.** Git path reads outside changed_path_args take git's C-quoted spelling of an unusual path for the path: about 15 --name-only, ls-tree and diff reads across vcs.py, claims.py, verify.py, pr_title_check.py and doc_check.py ask for no -z, the fact PL-JTCQ, PL-MR8Z and PL-PXT7 each misread at their own readers

**Filed 2026-10-12 at the triage pass, as the head `PL-JTCQ`'s brief asked
for.** Unless told otherwise git prints a path holding a byte above 0x7f, a
tab, a double quote or a backslash in double quotes with C-style escapes
(git-config's `core.quotePath`); `-z` prints every path as it is. Three items
misread that one fact at different readers: `PL-PXT7` (`contrast_check`'s file
listing, done 2026-10-12), `PL-MR8Z` (verify's quoted diff header, ready) and
`PL-JTCQ` (`_commits_by_landing`, `_baseline`, `_deleted_paths`). No head's
`misread:` states it: `PL-PVW2`'s is which spelling of a repeated predicate is
the answer, and `PL-4W2L`'s, where `PL-MR8Z` is attributed, is whether a diff
weakens its tests. `git grep` for `--name-only` and `ls-tree` lines without
`-z` under `subprojects/docket/src`, `tools` and `.claude/hooks` gave 52 lines
on 2026-10-12, a count of lines rather than of reads, all latent since no
tracked path is one git quotes.

**Generator.** `spent`: every member was found by a sweep or a review, none in
use, and no tracked path is one git quotes, so ordinary work cannot meet one.
Recorded for the audit; the members are worked at their own bands.
