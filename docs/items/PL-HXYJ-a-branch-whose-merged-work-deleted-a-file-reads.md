---
id: PL-HXYJ
title: A branch whose merged work deleted a file reads as unmerged again once the base writes a file at that path, and bin/docket stranded then reports the merged deletion as work left behind: _Landings.deletions tests the base's tip, which decays (found working PL-2CL5)
priority: P2
effort: S
status: done
classes: defect
feature: landing-deletions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.7.0 - found 2026-11-11 after the freeze; apparatus, and it changes no displayed value, so the release does not wait on it
added: 2026-11-11
closed: 2026-11-11
pr: 2091
payoff: a merged branch that deleted a file stays merged when the file is written again, so stranded does not report the deletion as lost work
verify: grep -q 'def test_a_deletion_the_base_took_stays_landed_after_the_path_is_written_again' subprojects/docket/tests/test_vcs.py
---

**Problem.** A branch whose merged work deleted a file reads as unmerged again once the base writes a file at that path, and bin/docket stranded then reports the merged deletion as work left behind: _Landings.deletions tests the base's tip, which decays (found working PL-2CL5)

**Reproduced 2026-11-11** in a scratch repository. A branch adds `a.txt` and deletes `old.txt`, and the base squash-merges it. `_unlanded_refs` then lists the branch as taken. After the base commits a new `old.txt`, the same call lists the branch as unlanded, and `_Landings.deletions` puts `old.txt` in its outstanding half.

**Why it matters.** A merged branch reads as in flight again, and `bin/docket stranded` reports the merged deletion as work left behind. Recovering it would delete the file the base wrote since.

**Done when.** A deletion the base made since the fork stays landed after a later commit writes a file at that path, and `test_a_deletion_the_base_took_stays_landed_after_the_path_is_written_again` in `subprojects/docket/tests/test_vcs.py` pins it.

**Generator check.** A member of `PL-2CL5`, the head for what `PL-927J`'s single landing test left unread: a deletion. Found by that head's own work.

**Built, 2026-11-11.** `_deleted_since` reads the paths the base's commits deleted since the fork, from the walk `_written_since` makes. `_Landings._deletions` counts a deletion as landed where the base's tip lacks the path or one of those commits deleted it. `PL-2CL5` has the design.
