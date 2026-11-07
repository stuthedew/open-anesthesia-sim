---
id: PL-2FHP
title: Cut v0.6.6 from the 7 items finished since v0.6.5
status: done
resource: release-train
added: 2026-10-25
closed: 2026-10-25
pr: 1795
verify: grep -q '^## Current baseline: v0.6.6' ROADMAP.md
---

**Problem.** Cut v0.6.6 from the 7 items finished since v0.6.5

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.6 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Seven items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `tests/reference/` and `README.md` resolve to the same trees at the v0.6.5 tag and here. `docs/MODEL.md` moved only by four `derived:` markers, HTML comments that no reader sees, which tie its step-count figures to `MAXIMUM_ELAPSED_SIMULATION_TIME_S` and `MINIMUM_SIMULATION_STEP_S`. A new monthly `restated-constants` job in `drift.yml` moves each limit in `core/supported_ranges.py` and names each test that fails without reading the limit by name (`PL-0Z0F`), and `tools/doc_check.py` reads a number grouped with spaces as one number (`PL-NH53`). The `[models]` table and its one reader, `docket.model_choice`, decide which model and effort `bin/docket next`, the headless worker and the model-document review use (`PL-0XDM`), and the table no longer excludes any model, since Fable was only the example of a stale model named outside one home (`PL-J9VC`). The sweep of Gate 3's 24 open entries dropped none and corrected six records (`PL-F2NX`), and `CLAUDE.md` now says to wait on a long run only as a tracked background task with a scheduled check-in (`PL-D1FD`). `docs/ARCHITECTURE.md`, `docs/maintainer.md` and `docs/apparatus.md` are rewritten in plain English with no fact dropped (`PL-TPS7`). **It finishes `one-home-for-constants` and `gate-staleness-sweep`**, and closes no generator head. **None is a Gate 3 entry**, and the gate stands at 22 of 46 cleared, as at the v0.6.5 tag. `PL-2FHP`, the cut, ships in no release under `PL-KRS6`.
