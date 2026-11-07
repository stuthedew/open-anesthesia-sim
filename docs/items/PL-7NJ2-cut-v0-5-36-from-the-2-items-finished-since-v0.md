---
id: PL-7NJ2
title: Cut v0.5.36 from the 2 items finished since v0.5.35
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1638
verify: grep -q "^version = \"0.5.36\"" pyproject.toml
---

**Problem.** Cut v0.5.36 from the 2 items finished since v0.5.35

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.36 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Two items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 33 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `data/`, `tests/reference/` and `docs/MODEL.md` resolve to the same trees at the v0.5.35 tag and here. Both items merged in `#1637` after the v0.5.35 tag. The harness fetches the default branch at depth 50 and the session-start hook unshallows it, so `vcs.py`, `checks.py`, `cli.py`, `render.py`, docket's README, the stop hook and `docs/apparatus.md` no longer call a shallow clone the normal case or say `--depth 1`, and `tools/doc_check.py` no longer says the workflows' checkout is shallow (`PL-2H0K`). Of 16 quoted strings compared with the pages' markdown, four in three passages had drifted and are corrected (`PL-124X`). **It finishes no feature**, and closes no generator head. **None is a Gate 2 entry**, and the gate stands at 238 of 246 cleared, as at the v0.5.35 tag. `PL-7NJ2`, the cut, ships in no release under `PL-KRS6`.
