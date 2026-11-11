---
id: PL-MH1H
title: Cut v0.6.18 from the 6 items finished since v0.6.17
status: done
resource: release-train
added: 2026-11-11
closed: 2026-11-11
pr: 2132
verify: grep -q '^## Current baseline: v0.6.18' ROADMAP.md
---

**Problem.** Cut v0.6.18 from the 6 items finished since v0.6.17

**Handoff, 2026-11-11.** The cut is committed: the version is 0.6.18, the
notes are in `docs/releases/v0.6.18.md`, and six items are stamped.
`ROADMAP.md` has the v0.6.18 row and baseline section. v0.6.17's notes have
a pointer for `#2111`. `make check` passed except the documentation test,
which the pointer fixed.

After the cut, `#2103` and `#2118` merged on `main` and were merged into
this branch. `#2103` makes the bookmarks and the branch control Views that
any Area can hold. It changes `src/`, the three Workspace files under
`src/anesthesia_sim/data/workspaces/`, `docs/MODEL.md` and `README.md`. Its
items (`PL-9YPR`, `PL-QKDV`, `PL-5XVQ`) and `PL-BVC5` from `#2118` are
closed but not stamped, so the tag will ship them and the v0.6.19 notes will
name them. The baseline section is now wrong in three places. It says that no
stored value changed. It says that the tag ships one interface change that
the notes do not name. Its tree table gives `src/`, `data/`, `docs/MODEL.md`
and `README.md` the hashes from before the merge. The same session then rewrote the section to match the merged tree.
