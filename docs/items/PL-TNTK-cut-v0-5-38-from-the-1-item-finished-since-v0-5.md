---
id: PL-TNTK
title: Cut v0.5.38 from the 1 item finished since v0.5.37
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1644
verify: grep -q "^version = \"0.5.38\"" pyproject.toml
---

**Problem.** Cut v0.5.38 from the 1 item finished since v0.5.37

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.38 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> One item, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 33 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `data/`, `tests/reference/` and `docs/MODEL.md` resolve to the same trees at the v0.5.37 tag and here. The item merged in `#1643`, before the v0.5.37 cut landed, so its change is inside the v0.5.37 tag and v0.5.37's notes now point here. `tools/doc_quotes.toml` records each quotation, and `tools/doc_quote_check.py` checks it against both the quoting file and the page (`PL-S7LT`). **It finishes no feature**, and closes no generator head. **It is not a Gate 2 entry**, and the gate stands at 238 of 246 cleared, as at the v0.5.37 tag. `PL-TNTK`, the cut, ships in no release under `PL-KRS6`.
