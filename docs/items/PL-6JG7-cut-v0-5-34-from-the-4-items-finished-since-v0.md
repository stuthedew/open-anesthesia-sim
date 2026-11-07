---
id: PL-6JG7
title: Cut v0.5.34 from the 4 items finished since v0.5.33
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1633
verify: grep -q "^version = \"0.5.34\"" pyproject.toml
---

**Problem.** Cut v0.5.34 from the 4 items finished since v0.5.33

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.34 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Four items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 33 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `data/`, `tests/reference/` and `docs/MODEL.md` resolve to the same trees at the v0.5.33 tag and here. Three of the items merged in `#1629` and `#1630` after v0.5.33's cut was written and before it landed, so their changes are inside the v0.5.33 tag and are described here. `tools/doc_check.py` reads every open item brief for a wrapped clause that renders as a list item, and six open briefs are rewrapped (`PL-XLYK`). The audit asks `docket.model` whether an appended `recurrences:` entry reads as a filing, so it refuses an impossible date that the store already refused (`PL-FYV7`). A line citation, a TeX delimiter or a quoted-source claim inside an indented code block or an HTML comment no longer fails `doc_check`, as one inside a fence already did not (`PL-2B0B`). `.claude/rules/ui-areas.md` describes the built area system and loads on `app/`, `layout/` and `data/workspaces/`, and `docs/ARCHITECTURE.md` drops the prohibition (`PL-ZBBP`). **It finishes two features**, `prose-renders-as-written` and `recorded-not-inferred`, and closes no generator head. **None is a Gate 2 entry**, and the gate stands at 238 of 246 cleared, as at the v0.5.33 tag. `PL-6JG7`, the cut, ships in no release under `PL-KRS6`.
