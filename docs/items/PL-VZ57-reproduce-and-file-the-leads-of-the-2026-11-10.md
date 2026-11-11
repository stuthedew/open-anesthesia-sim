---
id: PL-VZ57
title: Reproduce and file the leads of the 2026-11-10 root-cause audit that its session did not confirm
priority: P2
effort: M
status: ready
classes: housekeeping
touches: docs/items
added: 2026-11-10
payoff: each lead the audit's reviewers reported is either a filed item or struck with its reason, so none is lost with the session's reply
verify: grep -qE '^[*][*]Leads reproduced,' docs/items/PL-VZ57-*.md
sweep: the leads of the 2026-11-10 root-cause audit that its session did not confirm
---

**Problem.** Reproduce and file the leads of the 2026-11-10 root-cause audit that its session did not confirm

**Where these come from.** On 2026-11-10 a read-only session audited the recorded root-cause items and the recent queue with eight reviewers, one per family. The findings it confirmed are filed: `PL-B8DL`, `PL-0G2P` and `PL-G2WC` (interface tests), `PL-HQPF` (the reference condition label), `PL-95BJ` (the push guard), `PL-XSRG` (published-data tests), `PL-GKG4` (blood flow), `PL-RLRG` (decision records in `docs/MODEL.md`), `PL-YSV3` and `PL-D8L0` (how re-entries and closed heads are counted) and `PL-J2VF` (the documentation quote). Everything below is a reviewer's report that the session did not rerun, unless it says "confirmed". Reproduce each against the tree before filing it. Sharing a family below is not sharing a mechanism.

**Interface.**

- `.claude/rules/ui-color.md` and `tests/integration/test_dark_appearance.py` say the interface uses no tooltips. `setToolTip` appears 12 times under `src/` (count confirmed), in `app/area_layout.py` and `app/workspace_tabs.py` among others, and a tooltip takes the host's colours.
- Units typed where they are used and not read from `DisplayUnit`: "×MAC" in `app/bookmarks.py`, "%" in `app/formatting.py`, and unit strings in `app/qt_chart.py`.
- After a Reset or an agent change fails, the chart goes on showing the discarded run under a banner (`app/dashboard_frame.py`), and the hover readout may read that frame (inferred, not traced).
- The guard `PL-J5GC` built carries 23 exemptions in one list, about 13 of which state run state, and `FRAME_WIDGETS` carries 5.
- The agent cost View's unit selector and price form are in no restatement test.

**Guards.**

- `CLAUDECODE= git fetch --prune`, `bash -c 'gh pr merge ...'` and a `curl` that carries the GitHub token each pass the guards that read a command's text. A force push has no hook.
- Arming auto-merge through the GitHub tool is not compared with what `bin/docket arm` answered (the session's merge guard, since removed by `PL-39Y1`, skipped `enable_pr_auto_merge`), so the hold for the owner's read on a simulator change rests on the session. `PL-HDRN` recorded five of six simulator branches skipping a close-out step.
- `CLAUDE.md` and `docs/maintainer.md` say the repository's hooks do not run in project threads. `thread_hooks.py` has copied them into threads since 2026-10-26.
- `PL-5HQY`'s answer that the wording guard on asks owed no successor rested on no refusals being logged while the hook was wired to tool names that had been renamed (`PL-YN60`). `bin/docket inflow` still prints the line as answered.
- `PL-61FT` (guards that judge a shell command by its text) was closed on a header and a policy and has been re-entered 12 times.
- Nothing enforces a read-only order from the owner.

**Core calculations.**

- Seven items describe error that builds up over steps, or a rounded result compared exactly, and no head names the fact: `PL-D88N`, `PL-XST1`, `PL-9B1M`, `PL-81Q2`, `PL-N559`, `PL-9SL5`, `PL-QVBR`. The input-range fixes of `PL-ZGYX` and `PL-58D7` cannot reach it.
- `tests/unit/test_numerical_envelope_sweep.py` covers three entry points at their corners for one step, from a hand-written list of 16 edges. Its docstring and `docs/MODEL.md` claim more.
- Expected values with no derivation: a pin in `tests/unit/test_coupled_dynamics.py` that is compared with a copy of itself, "0.11 ×MAC" in `tests/unit/test_controller.py`, and "1.0000000000000002" in `tests/unit/test_uptake_system_failure.py`.
- Public functions in `core/` that still take a bare number where a checked type exists, in `circuit.py`, `agent_simulation_validation.py`, `uptake_system.py`, `run_definition.py`, `liquid_agent.py`, `parameters.py`, `matrix_exponential.py` and `exponential_approach.py`.
- The replay of blind reviews (`PL-TBQS`, `PL-TCBJ`) found about two real defects for each of about 19 merged pull requests it replayed. The pull requests it did not replay may hold as many (inferred).
- `PL-WF25` (`docs/MODEL.md` had a MAC direction reversed) is recorded `dropped`, though the error was real and pull request #2054 fixed it.

**Documents.**

- `_names_code` in `tools/doc_check.py` passes a paragraph that names any defined code name or any directory outside `docs/` (confirmed by reading it). `PL-BLN0` (tie document sentences to code) is marked spent on that check and leaves out the prose of `docs/MODEL.md`.
- The numeric-paragraph check holds 34 of 470 paragraphs in `docs/MODEL.md` that state a figure with a unit. § "Required invariants" is held by none (`PL-8LDF`, ready since 2026-08-25).
- `docs/MODEL.md` says "13 to 20% of arterial, against the trace's 2.3 to 3.9%", which matches no test (inferred). It has "3e-15" in a paragraph for a clinician.
- `PL-TDX0`, `PL-KG6S` and `PL-7R8S` read as three different defects in § "Displayed precision", not one item filed three times (from the titles).
- Pull request #2049 restored statements the copy editor had dropped from `docs/MODEL.md` (`PL-F0Q2`). Whether the restructure in #2054 was compared statement by statement in the same way is not known.
- Stale docstrings and comments under `src/` and `tests/`: 20 or more items since 2026-10-25, found by one-time sweeps, with no head.
- Seven items report `ROADMAP.md` contradicting itself: `PL-1BVB`, `PL-8G3F`, `PL-9857`, `PL-S2LW`, `PL-T5R7`, `PL-V82M`, `PL-6590`.

**One source of truth.**

- Copies that both checks pass: `> 100.0` in `core/parameters.py` beside `Percent`; `FreshGasFlow(4.0)` in `core/circuit.py` beside `data/machines/reference_circle_system.json`; 900.0 and 3600.0 in `app/chart_time_base.py` beside `core/units.py`; the length of a currency code in four places; `LEVELS` in `tools/effort_trial.py` and `EFFORT_LEVELS` in `subprojects/docket/src/docket/model_choice.py`.
- Eleven docket functions default `items_dir="docs/items"`, and `cli.py` calls `cut_window` without passing it, so another `--items` may read the wrong store (inferred).
- Shapes neither check reads: a number inside a string, one value under two names, a module-level table, a function default, and anything in tests, shell or YAML.

**Text parsing.**

- The guard `PL-R417` built (statements continued across lines) enrols each reader by hand in `CONTINUED_STATEMENTS`. `PL-J8Q9`, the automatic re-wrap test, closed unbuilt.
- `.claude/hooks/docket_branch_guard.py` treats a failed `git status` as a clean tree. `tools/config_home_check.py` reads a Python list with a pattern.
- Ways to weaken a test that `tools/diff_mutation.py` does not see, beyond `PL-XSRG`: a bare `skip()`, `__test__ = False`, a rename away from `test_`, an early return, and any change to an apparatus test.

**Prose rules.**

- `PL-J1ZM` (prose over-explains) may misname its cause. Its members show decision history and item ids gathering in documents for a reader, and also the opposite defect, private compressed wording (`PL-VGDX`, `PL-2K0K`). The resident rules grew from 8,903 characters to 92,128, and `PL-H76S` records the owner asking for no further rule.
- `docs/prose-review/gold/` is empty. 47 items name `/mnt/project-files`, which is not in the container.

**Queue and branch state.**

- About 19 defect items since 2026-10-17 describe a tool or test that assumes the machine it was written on, such as `PL-PLT9`, `PL-29DJ`, `PL-NQ0M`, `PL-Q508`, `PL-TSH9`, `PL-44R1`, `PL-BT70`, `PL-4WFK`, `PL-TNY6`, `PL-YN60`, `PL-8RGF`, `PL-KW5K`, `PL-TFY2`, `PL-W6JM`, `PL-TQ4J`, `PL-M8Z7`, `PL-D1FD` and `PL-JP35`. No head names the fact. The list was picked from titles.
- After `PL-8QMD` (gate entry dispositions) closed, four items reported the deferral rule again: `PL-YL5R`, `PL-H4TF`, `PL-GW0P`, `PL-8C8W`. One carries `reenters:`.
- Nine open safety or science items are deferred from v0.7.0 on a sentence that says "not live: checked" with a date, and nothing rechecks the sentence: `PL-19W8`, `PL-5C1H`, `PL-5L84`, `PL-86VL`, `PL-FCYQ`, `PL-H94Q`, `PL-JP7P`, `PL-MCQ5`, `PL-RJN9`.
- Of 42 apparatus defects sampled since 2026-10-15, 16 name an earlier fix in prose and carry no `reenters:`. `.claude/skills/docket/modes/triage.md` limits a re-entry of an item that is not a head to 30 days.
- 12 of 29 recurrence records written since 2026-10-15 were withdrawn as wrong matches.
- `PL-4Q9B` (remote refs against local copies) closed as "not one mechanism" and was re-entered five times in the following week.
- 222 of 1,340 `grep`-only `verify:` commands on closed items fail today. `.claude/skills/docket/modes/triage.md` says a closed item's command is a record and is not repaired, so this is not a finding.

**Done when.** Each lead above is reproduced against the tree and then filed, linked to the open item that holds it, or struck here with the reason. A paragraph that opens "**Leads reproduced,**" with its date says which was which.

**Generator check.** Work the owner asked for: the audit of 2026-11-10 looked for root causes that are unrecorded or whose fix did not hold. The leads above are its unconfirmed findings, and each owes its own check when it is filed.

**Checked 2026-11-11:** `PL-39Y1` takes the guard leads above: the pruning fetch, the merge inside `bash -c`, the request that carries the token, the force push and the arming that `bin/docket arm` is not asked about. It removed the merge guard that the arming lead names, and it moves each refusal to GitHub's rules.
