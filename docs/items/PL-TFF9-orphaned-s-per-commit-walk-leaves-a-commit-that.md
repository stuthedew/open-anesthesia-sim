---
id: PL-TFF9
title: orphaned's per-commit walk leaves a commit that deletes a file unclassified, since the deleted path is in neither of _landing_split's sets, so a left-behind commit that deletes one file and edits another is never reported as work left behind
status: untriaged
added: 2026-09-25
---

**Problem.** orphaned's per-commit walk leaves a commit that deletes a file unclassified, since the deleted path is in neither of _landing_split's sets, so a left-behind commit that deletes one file and edits another is never reported as work left behind

Found 2026-09-25 by PL-KR69's build, by reading rather than reproducing. `vcs._commits_by_landing` reports a commit as left behind only when every path its `git log --name-only` lists is in `_landing_split`'s outstanding set, and `_landing_split` classifies only the paths whose post-image blob is non-zero, so a deleted path is in neither set. A commit that deletes one file and edits another then fails both `all(...)` tests and is neither reported nor counted as taken whole. A rename git scores below 50% similarity lists as a deletion and an addition, and reads the same way. PL-KR69 kept this walk on git's rename detection for exactly that reason, and did not change its classification.

**Not a recurrence of PL-WNQT**, which `docket new` matched on title words. PL-WNQT is the same walk reporting too much (a later merge editing the file makes a landed commit read as left behind); this is it reporting too little, from a different mechanism.
