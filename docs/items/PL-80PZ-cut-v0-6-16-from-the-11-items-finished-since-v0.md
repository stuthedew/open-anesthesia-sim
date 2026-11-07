---
id: PL-80PZ
title: Cut v0.6.16 from the 11 items finished since v0.6.15
status: done
resource: release-train
added: 2026-11-05
closed: 2026-11-05
pr: 2043
verify: grep -q '^## Current baseline: v0.6.16' ROADMAP.md
---

**Problem.** Cut v0.6.16 from the 11 items finished since v0.6.15

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.16 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 11 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: every id in v0.7.0's Required scope is now closed, the six of entry 12 among them, but Gate 3 still has `PL-SP6H` open, and v0.7.0 is cut only after the project owner has test-driven `main`. v0.7.0 and v0.8.0 are given to milestone sections. **No code, equation, model parameter or stored value changed, and no run can differ**: `core/` (`8186a8c`), `data/` (`c3fbdbc`), `tests/reference/` (`545a009`) and `.github/` (`fefd203`) resolve to the same trees at the v0.6.15 tag and here. `src/` moved only in comments and docstrings in `app/chart_frame.py` and `app/unconditional_set.py`, which `tools/ast_identity.py` confirms, so the trajectories were not re-measured. **It finishes two features**, `reader-first-prose` and `repo-copy-edit`, and closes one generator head, `PL-HGZS`, spent. **None is a Gate 3 entry**, and the gate stands at 87 of 90 cleared, as at the v0.6.15 tag. `PL-80PZ`, the cut, ships in no release under `PL-KRS6`.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** § "Current baseline: v0.6.16" carried these sentences until then. The restructure keeps in the baseline what the release holds and why v0.7.0 is not yet cut, and moves the rest to the release item.

> The release item is `PL-80PZ`, whose `resource: release-train` keeps it out of every later release. `bin/docket release` again reported the missed apparatus-inflow prediction for 2026-10-26 to 2026-11-01, one P1 apparatus filing outside the generator tier. `PL-7LMM` already records that week's miss.
