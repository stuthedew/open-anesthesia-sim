---
id: PL-CBDX
title: Read every simulator diff merged unread since 2026-09-23 against the safety-critical standard, since the review hold was clicked through rather than read
priority: P1
effort: M
status: done
classes: safety
feature: review-hold
milestone: v0.5.12
touches: docs/items, src/anesthesia_sim
added: 2026-09-25
closed: 2026-09-26
pr: 1043
payoff: any wrong or misleading clinical value an unread merge put on screen since 2026-09-23 is found and filed, or the record says none was
verify: grep -q '^\*\*Reviewed\.\*\*' docs/items/PL-CBDX-*.md
not-delegable: the work is a read of merged diffs against the safety-critical standard; no command can prove a diff was read well, and the brief asks for a clean-context session on the strongest model
---

**Problem.** Read every simulator diff merged unread since 2026-09-23 against the safety-critical standard, since the review hold was clicked through rather than read

The owner's answer of 2026-09-25 under `PL-SQTR` confirmed that pull requests `bin/docket arm` held for review were armed in the browser without being read. So every merged diff since 2026-09-23 that touches `src/`, `tests/` outside `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/` or `README.md` reached `main` with no read against the safety-critical standard.

**Why it matters.** This is the one path by which an unread merge could have put a wrong or misleading clinical value on screen, and `CLAUDE.md`'s standard assumes a clinician could act on one.

**Done when.** A fresh session, with a clean context and the strongest model, has read each such diff against `CLAUDE.md`'s safety-critical clinical-output standard and filed each finding with `bin/docket new`. It then adds a section to this brief whose first line is `**Reviewed.**` alone, followed by one line per pull request read, with what it found, or that it found nothing. The verify reads that line, anchored at the start of a line so it cannot match its own text in the frontmatter, which the first form did (caught by `make check`'s `--verify` sweep on 2026-09-25, before any push).

**Generator check.** A one-off, from `PL-SQTR`'s owner-raised finding: a human step was skipped, and no record was misread.

**Scope as read** (2026-09-26, `origin/main` at `a0ac88c4`). "Since 2026-09-23"
is taken from 00:00 UTC, the earlier and so wider of UTC and the owner's
Central time. `git log origin/main --since=2026-09-23T00:00:00Z` over `src/`,
`tests/`, `docs/MODEL.md` and `README.md` names 13 squash merges. Only `#959`
touches a simulator path: no merge in the window changed `src/`,
`src/anesthesia_sim/data/` or `README.md` at all. The other twelve change only
`tests/unit/` files that import no `anesthesia_sim` module, which is the line
`tools/workflow_paths_check.py` draws between apparatus and product tests,
applied to each file at its merge commit. So those twelve were screened for the
one way an apparatus change reaches a displayed value, by loosening a check
that holds the product, and were not read line by line. Two such checks moved
in the window, and both held. `tools/doc_check.py`'s `check_bound_families`,
which binds § "Minimum displayed outputs" to its tests, is byte-identical from
`c03ae7a3` to `a0ac88c4`. `tools/contrast_check.py`'s `KNOWN_SHORTFALLS` was
empty before and after `#996`. The six release cuts in the window (`#931`,
`#946`, `#957`, `#980`, `#989`, `#1003`) change `pyproject.toml` and `uv.lock`
by the project's own version line only, so no dependency moved. The four
product merges just before the window (`#905`, `#908`, `#911`, `#912`, all
2026-09-22 in both time zones) predate the hold `PL-WNCT` added and are outside
it.

**Reviewed.**
- `#959` (`PL-QYBW`, `PL-H5DV`): the chart keeps one linear percent axis topped at 3 MAC. It changes `docs/MODEL.md` and two test docstrings and no code. It was read in full against the tree, with every figure it wrote re-measured by an independent script, not re-run from `PL-H5DV`'s. The axis is `3.0 × MAC` in `chart_axis_top_percent`. The axis reads "% of 1 atm" and "×MAC", partial pressure rather than amount. The chart draws six compartments. Muscle spans 24.8–48.4 px and fat 1.47–3.67 px at 1 h. Fat holds 19.5–21.3% of stored agent at 1 h and 30.3–33.4% at 3 h. Fat overtakes muscle at 4.64–7.46 h. The docstrings' 0.0167 %/px is sevoflurane's 6.0% over 360 px. No copy of "scaled by the alveolar peak" is left. One finding, `PL-8YBS`: a table row states fat's 1 h span as "under 4 px" without the 1 MAC dial it holds at; it is 6.1–11.0 px at the maximum dial. No displayed value is affected.
- `#1016` (`PL-FX5Q`): apparatus tests only (`test_branch_id_check.py`, `test_docket_digest_hook.py`). Nothing.
- `#999` (`PL-MB3F`): apparatus tests only. Its `Makefile` edit runs `doc_check` under `uv run` and drops no product gate. Nothing.
- `#998` (`PL-Y1W0`): apparatus test only (`test_pr_body_check.py`). Nothing.
- `#996` (`PL-KNHX`, `PL-TP75`): apparatus test only. `contrast_check` now refuses a stale shortfall entry, a tightening, and excuses no contrast gap. Nothing.
- `#991` (`PL-J9S0`): apparatus tests only (`test_branch_id_check.py`, `test_docket_branch_guard.py`). Nothing.
- `#975` (`PL-GHHW`, `PL-PXZ3`): apparatus test only (`test_left_behind_check.py`). Nothing.
- `#970` (`PL-58JD` and four more): apparatus tests only. It moves `doc_check`'s gate-disposition check into docket and leaves `check_bound_families` untouched. Nothing.
- `#938` (`PL-1PBV`): apparatus tests only (`test_branch_id_check.py`, `test_generator_check.py`, `test_pr_title_check.py`). Nothing.
- `#937` (`PL-J6HP`, `PL-B60Q`): apparatus test only (`test_doc_check.py`), roadmap gate facts. `check_bound_families` untouched. Nothing.
- `#933` (`PL-9RFP`): apparatus test only (`test_doc_check.py`), verify's git reads. Nothing.
- `#932` (`PL-R808`): apparatus test only (`test_left_behind_check.py`). Nothing.
- `#924` (`PL-7TVT` and five more): apparatus test only (`test_open_pull_requests.py`). Nothing.
