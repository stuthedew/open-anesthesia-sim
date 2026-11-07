---
id: PL-XMCT
title: Cut v0.6.1 from the 9 items finished since v0.6.0
status: done
resource: release-train
added: 2026-10-24
closed: 2026-10-24
pr: 1719
verify: grep -q '^## Current baseline: v0.6.1' ROADMAP.md
---

**Problem.** Cut v0.6.1 from the 9 items finished since v0.6.0

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.1 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Nine items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, was not yet scoped when it was cut, and v0.7.0 and v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/`, `tests/reference/`, `docs/MODEL.md` and `README.md` resolve to the same trees at the v0.6.0 tag and here, and only `.github/` moved. All nine merged after the v0.6.0 tag. The generator ranking and its pause went to the docket skill's triage mode (`PL-6VJ3`), the pull request procedure to a new `pull-request` skill (`PL-S2NL`), and the spend-reset procedure and the housekeeping rule's detail to the docket skill's start and capture modes (`PL-Z90G`), each leaving one sentence in `CLAUDE.md` that names its moment; `PL-SN2Z` measured that the docket skill starts on the requests that name its moment. **It finishes `skill-routing` and `worker-instructions`**, and closes no generator head. **None is a gate entry**: Gate 3 froze later, when v0.7.0 was scoped. `PL-XMCT`, the cut, ships in no release under `PL-KRS6`.
