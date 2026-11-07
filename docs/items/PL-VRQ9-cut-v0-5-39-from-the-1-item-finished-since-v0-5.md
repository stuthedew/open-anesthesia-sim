---
id: PL-VRQ9
title: Cut v0.5.39 from the 1 item finished since v0.5.38
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1646
verify: grep -q "^version = \"0.5.39\"" pyproject.toml
---

**Problem.** Cut v0.5.39 from the 1 item finished since v0.5.38

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.39 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> One item, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 33 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `data/`, `tests/reference/` and `docs/MODEL.md` resolve to the same trees at the v0.5.38 tag and here. The item merged in `#1645`, before the v0.5.38 cut landed, so its change is inside the v0.5.38 tag and v0.5.38's notes now point here. A simulator branch that adds a long docstring or comment holds until a commit after it carries a `Prose-review:` trailer, and close-out step 8 tells a session to record one (`PL-W04Z`). **It finishes no feature**, and closes no generator head. **It is not a Gate 2 entry**, and the gate stands at 238 of 246 cleared, as at the v0.5.38 tag. `PL-VRQ9`, the cut, ships in no release under `PL-KRS6`.
