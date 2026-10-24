---
id: PL-K88Z
title: Inventory every second copy of a shared fact across the tree, sorted by the four shapes (a value copied, state with two writers, a rule made in several places, configuration restated), and file each finding under one-source-of-truth
priority: P2
effort: M
status: done
classes: planning
feature: one-source-of-truth
touches: ROADMAP.md
added: 2026-10-19
closed: 2026-10-24
pr: 1712
payoff: the one-source-of-truth row is sized from a count of every second copy, so its scope is measured rather than guessed
verify: grep -q 'Inventoried 2026-' ROADMAP.md
---

**Problem.** Inventory every second copy of a shared fact across the tree, sorted by the four shapes (a value copied, state with two writers, a rule made in several places, configuration restated), and file each finding under one-source-of-truth

**Why it matters.** Step 2 of `PL-2LB5` (the one-source-of-truth design round). The project owner chose on 2026-10-19 to run this inventory before v0.6.0 ships and to scope the fixes as their own roadmap row after it (`ROADMAP.md` planned-milestone item 43). The inventory decides how large that row is, so it comes first.

**Approach.** Deterministic tools first, the session's judgment last, per `CLAUDE.md` § "Prefer deterministic tooling over repeated model work":
1. **A value copied.** Read the baselines of `tools/literal_home_check.py` and `tools/fact_home_check.py`. Then list every number in `docs/MODEL.md` and `README.md` that restates a value in `src/anesthesia_sim/data/` or in code, with its home.
2. **State with two writers.** List each displayed or derived run state in `src/anesthesia_sim/app/` and every path that writes it. `PL-X7D5` is the pattern of one writer.
3. **A rule made in several places.** Run pylint's duplicate-code check (`R0801`) over `src/`, `tools/` and `subprojects/docket/`. List every range or predicate checked by hand where a checked type or a home already exists.
4. **Configuration restated.** List the Python version, paths, commands and timeouts that appear in more than one of `pyproject.toml`, `.github/workflows/`, the `Makefile`, `docket.toml` and the docs.

Sort each finding by shape. File it under `one-source-of-truth`, unless one of the four check items (`PL-JS6P`, `PL-WM5P`, `PL-VWXL`, `PL-SH0W`) will burn it down as part of its baseline. Leave out the two copies that must stay copies: a test's expected value, and a published value restated beside its citation.

**Done when.** Each of the four shapes has a dated count in this brief, each finding is filed or named in the baseline of the check item that will remove it, and `ROADMAP.md` planned-milestone item 43 carries the resulting size in a sentence that begins "Inventoried 2026-".

## Inventory, 2026-10-19

Counted on `main` at `4be43813`. Each shape gives its count, the items filed for it, and the findings left for one of the four check items to remove. Those findings are listed here as that check item's starting baseline. Test expected values and published values restated beside their citations are left out, as the brief says.

**1. A value copied: 93 already baselined, plus the numbers in `docs/MODEL.md` and `README.md`, which this run did not count.**
- `tools/literal_home_check.py` holds 34 bare literals: 29 layout literals in `src/anesthesia_sim/app/` and 5 in `core/`. `tools/fact_home_check.py` holds 59 second readers: 49 duplicate module-level names, 6 git readers and 4 GitHub API readers. Both checks refuse growth, but no open item drained either baseline. Filed: `PL-4X5B` (the 29 app literals), `PL-LGDV` (the 59 second readers), and `PL-M85T` (the 5 core class defaults that restate data-file values and are held equal only by tests).
- The numbers that `docs/MODEL.md` and `README.md` restate from `src/anesthesia_sim/data/` or from code were not counted. The survey of them did not finish inside this run's budget. `PL-JS6P` (the doc_check rule that ties those numbers to their homes) must enumerate them as its first baseline, so this part of the row's size is still unmeasured.

**2. State with two writers: 2 of the 20 run-state surfaces outside `RunView` have two writers, and 5 surfaces are not under `PL-X7D5`'s guard.**
- Filed, because both were reproduced offscreen: `PL-BM6X` (the branch panel's refusal notice outlives its case) and `PL-P58M` (a halted run keeps the old playback rate in the readout row, which the guard's `FRAME_WIDGETS` exempts).
- `PL-WM5P`'s baseline, inferred from reading the code and not run: the bookmark editor's notice (`BookmarkDialog.notice`, six writers through `SimulationView._bookmarks_notice`, cleared only by the next mark edit); `NewCaseDialog`'s elapsed-time text, written once while the run may still be running; the `AreaFrame` pin label and its "pinned run absent" notice, not restated on a halt; `ForkPanel`, `BookmarksPanel` and `BookmarkDialog`, which `PL-5JTH`'s guard checks for presence and not for value; and the `_readout_row` exemption itself.

**3. A rule made in several places: 14 duplicate blocks from pylint, and 51 hand re-checks in 18 mechanisms, of which 34 are high-confidence.**
- `PL-VWXL`'s baseline: pylint 4.1.3 `R0801` at the default 4 lines, over `src`, `tools` and `subprojects/docket/src`, finds 14 blocks. Five copy the baseline scaffolding between `fact_home_check.py` and `literal_home_check.py`. Four copy the `main()` argument parsing of `core_vocabulary_check.py`, `fact_home_check.py`, `import_boundary_check.py` and `source_tier_counts.py`. Three copy the pull request discovery logic between `pr_record_check.py` and `pr_title_check.py`. One is a dialog's keep button in `qt_widgets.py` and `workspace_tabs.py`. One is in `core/blood.py` and `core/tissue.py`: both call the same helper with the same arguments, so it is not a second copy of the rule, and clearing it means editing `core/`.
- Filed for the hand re-checks: `PL-84G1` (circuit volume against stored agent, in `core/`), `PL-YHWH` (three rules restated in `core/parameters.py` and `core/run_definition.py`), `PL-F9TC` (the app re-checks quantities that core owns), `PL-TSXD` (whether an item is open, decided by hand at 19 sites), and `PL-JT7Y` (pull request numbers read by hand at 4 sites). Not filed, as low-confidence or documented as deliberate: the payload validators in `core/parameters.py`, which raise `ValueError` for Pydantic; `core/tissue.py`'s own perfusion-fraction guard; `core/matrix_exponential.py`'s finite-state loop; the controller's window clipping; the app's 0 control floors; and the bool and int checks in `layout/serialization.py`.

**4. Configuration restated: 30 facts are stated in more than one file, 7 are already enforced by a check, and 3 have copies that disagree.**
- Filed for the disagreements: `PL-M81V` (a hook comment gives the old `requires-python`), `PL-58MP` (`docs/apparatus.md` and the README overstate how CI and `make check` match), and `PL-YN5B` (a stale CI step in a test fixture). `ruff check --no-cache` differs on purpose, and the Makefile records why.
- `PL-SH0W`'s baseline is the 23 facts that agree but that no check enforces. Five concern versions: the application's 3.14 target in ruff, mypy, `.python-version` and the README; the uv 0.12.5 minimum in `pyproject.toml`, the README and `docs/worker.md`; mutmut 3.8.0 in `pyproject.toml` and `docs/mutation-testing.md`; the `actions/checkout`, `setup-python`, `setup-uv` and `upload-artifact` pins, repeated across workflows; and `libegl1` in the workflows, the README and `docs/ARCHITECTURE.md`. Four concern paths: the test trees in `pyproject.toml`, `docket.toml` and `tools/ignore_check.py`; the protected paths in `docket.toml`, `CLAUDE.md` and `docs/worker.md`; and the apparatus and simulator path lists in `CLAUDE.md` and two rules. Six concern commands: the whole-suite run in the Makefile and `drift.yml`; `uv sync --locked --dev` in eight places; `ruff format --check`; `mypy`; the eight `ast` tools listed in `docs/apparatus.md`; and the `requires-python` lower bound restated in `drift.yml`. Two concern timeouts: the CI job's 15 minutes restated in `tools/main_ci_status.py`, and the 30 s quote-fetch timeout restated in `drift.yml`.

Captured outside the feature: `PL-BYHS` (`ROADMAP.md` still describes Flet as a dependency).

**Worked.** The four check items' baselines are listed in this brief under each shape. They are not written into `PL-JS6P`, `PL-WM5P`, `PL-VWXL` or `PL-SH0W`, because those files are outside this item's `touches`. Those items are `blocked-by` this one and can read the lists here. The four surveys ran in four subagents, and their results were checked only by a spot-read of `core/blood.py` and `core/tissue.py` and of the two baselines. Shape 1's count of restated documentation numbers is missing, because its survey did not finish inside the run's budget. That is recorded above and in `ROADMAP.md`, not estimated. pylint is not a project dependency, so it was run once through `uvx`. The brief named no threshold, so `R0801` ran at its default of 4 similar lines.
