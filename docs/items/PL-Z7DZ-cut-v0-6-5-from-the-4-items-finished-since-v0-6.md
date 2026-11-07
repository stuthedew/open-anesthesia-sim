---
id: PL-Z7DZ
title: Cut v0.6.5 from the 4 items finished since v0.6.4
status: done
resource: release-train
added: 2026-10-25
closed: 2026-10-25
pr: 1790
verify: grep -q '^## Current baseline: v0.6.5' ROADMAP.md
---

**Problem.** Cut v0.6.5 from the 4 items finished since v0.6.4

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.5 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Four items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `tests/reference/`, `docs/MODEL.md`, `README.md` and `.github/` resolve to the same trees at the v0.6.4 tag and here. `tools/headless_worker.py` refuses a run before any spend when `bash` is older than 5.2 or `make` is not GNU make 4 or later, so a worker on a host still running GNU Make 3.81 stops with a reason instead of failing `make check` (`PL-44R1`). The docket skill's picking mode gives three rules for builder subagents sharing one container: a scratch subfolder named for each item, long commands in the foreground, and one full suite at a time, run by the parent (`PL-5PL5`, `PL-9K28`, `PL-GH8L`). **It finishes `parallel-builders`**, and closes no generator head. **All four are Gate 3 entries**, and the gate stands at 22 of 46 cleared, from 18 of 46 at the v0.6.4 tag. `PL-Z7DZ`, the cut, ships in no release under `PL-KRS6`.
