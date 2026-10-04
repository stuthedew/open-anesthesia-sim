---
id: PL-LNDJ
title: docket's front-matter reader keeps a YAML block-scalar header in a field's value and closes the block on any line opening with ---, so reason: >- reads as '>- Duplicate of ...' and a ---y line ends the front matter; live on two dropped items
status: untriaged
touches: subprojects/docket/src/docket/model.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket's front-matter reader keeps a YAML block-scalar header in a field's value and closes the block on any line opening with ---, so reason: >- reads as '>- Duplicate of ...' and a ---y line ends the front matter; live on two dropped items

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`_fold` and `parse_front_matter` read `reason: >-` with its folded lines as ">- Duplicate of PL-LT77..." and ">- Measured 2026-09-04...", live at `docs/items/PL-B1DQ-a-v0-4-8-tag-exists-on-a-commit-whose-pyproject.md`:7 and `docs/items/PL-K1DL-splitting-make-check-by-path-docket-changes.md`:10, both dropped. `FRONT_MATTER_RE` (model.py:32) closes on any line that merely opens with `---`: a block holding `---y` before `status: done` reads status `''` and a body starting `y`, and `unread_front_matter_lines` returns nothing. Not a member of `PL-R417`: each value's extent is read whole. The second is latent.
