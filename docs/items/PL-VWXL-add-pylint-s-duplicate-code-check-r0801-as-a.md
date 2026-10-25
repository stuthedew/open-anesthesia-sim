---
id: PL-VWXL
title: Add pylint's duplicate-code check (R0801) as a ratchet over src/, tools/ and subprojects/docket/, with a baseline that can only shrink
priority: P3
effort: S
status: ready
classes: refactor, infra
feature: one-source-of-truth
touches: Makefile, pyproject.toml, uv.lock, tools/, tests/unit/, docs/apparatus.md, docket.toml, .github/workflows/quality.yml, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/workspace_tabs.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/validation.py
blocked-by: v0.6.0, PL-K88Z
deferred-from: v0.6.0 - placed on ROADMAP.md's v0.6.x one-source-of-truth row, built after v0.6.0 ships (project owner, 2026-10-19, ratified, PL-2LB5)
added: 2026-10-19
payoff: copied logic fails make check instead of drifting apart
verify: grep -q 'duplicate-code' Makefile
---

**Problem.** Add pylint's duplicate-code check (R0801) as a ratchet over src/, tools/ and subprojects/docket/, with a baseline that can only shrink

**Why it matters.** Step 5 of `PL-2LB5` (the one-source-of-truth design round). Copied logic is the third shape of a second copy. pylint already ships a duplicate-code checker, so this adds a ratchet over an existing tool rather than a new one.

**Done when.** `make check` runs pylint `R0801` over `src/`, `tools/` and `subprojects/docket/`, fails on a duplicate block not in its baseline, and the baseline is at zero.

**Generator check.** Not a re-entry: it is a step of `PL-2LB5` (the one-source-of-truth design round), which widens the closed `PL-4S6C` at the project owner's ask, and no open generator head names this shape.

**Built 2026-10-25, one block left.** `tools/duplicate_code_check.py` runs pylint 4.1.3's `R0801` alone over `src/`, `tools/` and `subprojects/docket/src/`, and `make check` and `quality.yml` run it under `uv run python`. It takes about 8 seconds. Its baseline, `ALLOWED_BLOCKS`, is keyed by the pair of modules and fails when a pair holds more blocks or fewer. Thirteen of the 14 blocks `PL-K88Z` counted are gone, in #1765:

- Nine in five source checks: the scoped `ast` walk, the baseline's overflow and stale-entry logic and their report lines, and the `--root` reading in `main()`. They now live in `tools/check_support.py`.
- Three between `pr_record_check.py` and `pr_title_check.py`: the arguments, the discovery of the branch's pull request, and the unread-trees message. `pr_title_check.py`, which `pr_record_check.py` already imports, holds them.
- One between the new-case dialog in `app/qt_widgets.py` and the Workspace question dialog in `app/workspace_tabs.py`, which now share `lay_out_question`.

**What is left.** The pair `core/blood.py` and `core/tissue.py`: both make the same capacity and room checks when a partition coefficient is written. Removing it means a helper in `core/validation.py`, which is the clinical floor, so it is built with the core batch (`PL-84G1`, `PL-YHWH`, `PL-M85T`, `PL-6YKY`) and this item closes there, with `ALLOWED_BLOCKS` empty.
