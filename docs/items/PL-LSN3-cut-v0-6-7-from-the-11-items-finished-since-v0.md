---
id: PL-LSN3
title: Cut v0.6.7 from the 11 items finished since v0.6.6
status: done
resource: release-train
added: 2026-10-25
closed: 2026-10-25
pr: 1803
verify: grep -q '^## Current baseline: v0.6.7' ROADMAP.md
---

**Problem.** Cut v0.6.7 from the 11 items finished since v0.6.6

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.7 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Eleven items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **No executable statement changed, and no run can differ**: `src/` moved only in its docstrings and comments, which `PL-1K5X` (`#1798`) rewrote in plain English, and with every docstring removed the code of each of its files is identical at the v0.6.6 tag and here. `tests/reference/`, `docs/MODEL.md` and `README.md` resolve to the same trees at both ends. `tools/branch_sweep.py` reads a worker branch whose latest run was reviewed `sent-back` as settled, so `bin/docket next` offers its item again (`PL-W5JR`), and `bin/docket check` treats the worker's own item's passing `verify:` as an advisory for the reviewer rather than an error (`PL-WJJ8`). A new step in both parts of `quality.yml` collects the test modules once per core before pytest runs, which cut a CI-shaped part 1 from 188 s to 163.5 s (`PL-GQCQ`), and `PL-VMMB` keeps a share that holds no test module from failing the job. `bin/docket verify` no longer counts a call of `pytest_ignore_collect` as an added suppression (`PL-3G9M`). `tools/fact_home_check.py` refuses a repository path bound under two names in two apparatus modules, and its seven copies now read their homes (`PL-S08Z`). The pull request email guard writes its refusals to the guards' log (`PL-HHKC`), and `bin/docket check` reads a shipped milestone in `blocked-by` as cleared (`PL-YL5R`). A `focus` key in `docket.toml` ranks the digest's `Top:` line in the product lane (`PL-2CPD`), and the Projects coordinator's rules moved into a docket skill mode (`PL-NZC0`, `#1799`, inside the v0.6.6 tag's span). **It finishes `verify-false-reject` and `workflow-stress-2026-09`**, and closes no generator head. **Two are Gate 3 entries**, `PL-W5JR` and `PL-WJJ8`, and the gate stands at 24 of 46 cleared, from 22 of 46 at the v0.6.6 tag. `PL-LSN3`, the cut, ships in no release under `PL-KRS6`.
