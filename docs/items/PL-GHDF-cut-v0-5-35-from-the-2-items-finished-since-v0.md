---
id: PL-GHDF
title: Cut v0.5.35 from the 2 items finished since v0.5.34
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1636
verify: grep -q "^version = \"0.5.35\"" pyproject.toml
---

**Problem.** Cut v0.5.35 from the 2 items finished since v0.5.34

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.35 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Two items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 33 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `data/`, `tests/reference/` and `docs/MODEL.md` resolve to the same trees at the v0.5.34 tag and here. Both items merged in `#1627` and `#1634` after v0.5.34's cut was written and before it landed, so their changes are inside the v0.5.34 tag and are described here. `possessive_section_check` and two `doc_check` readers number a docstring finding from the source rows, so a backslash-newline or a `\n` escape no longer moves it to the wrong line (`PL-PV73`). A blind re-measure found 21.7% of the long prose written under close-out step 8 awkward, against a 30% bar, so the step is kept (`PL-J6CK`). **It finishes no feature**, and closes no generator head. **None is a Gate 2 entry**, and the gate stands at 238 of 246 cleared, as at the v0.5.34 tag. `PL-GHDF`, the cut, ships in no release under `PL-KRS6`.
