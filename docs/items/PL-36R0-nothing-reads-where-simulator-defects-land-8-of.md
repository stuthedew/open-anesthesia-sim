---
id: PL-36R0
title: Nothing reads where simulator defects land: 8 of 87 source files carry 47% of defect- and safety-classed items, the top three are the interface's largest files, and the generator check reads only what fact each item misread
priority: P2
effort: M
status: done
classes: infra, planning
feature: convergence-visibility
touches: subprojects/docket/src/docket/hotspots.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_hotspots.py, subprojects/docket/README.md, docs/features.toml
deferred-from: v0.7.0 - filed after the gate froze; an apparatus reading with no effect on what a learner sees
added: 2026-11-23
closed: 2026-11-24
pr: 2317
filed-pr: 2301
payoff: the files where simulator defects keep landing reach a design review instead of collecting items one at a time
tests: subprojects/docket/tests/test_hotspots.py::test_only_defects_in_simulator_source_files_in_the_window_are_counted, subprojects/docket/tests/test_hotspots.py::test_a_finished_review_covers_its_file_until_three_more_defects_land, subprojects/docket/tests/test_hotspots.py::test_the_cut_names_each_file_owed_a_review_and_how_to_file_one
---

**Problem.** Nothing reads where simulator defects land: 8 of 87 source files carry 47% of defect- and safety-classed items, the top three are the interface's largest files, and the generator check reads only what fact each item misread

**Found 2026-11-23**, answering the owner's request to research how to detect architectural problems and other underlying causes. The repository records which files each item declares in `touches`. Counting defect- and safety-classed items against the 87 Python files under `src/` gives 781 links. The 8 files with the most (9% of files) carry 47% of them. The top three are `src/anesthesia_sim/app/simulation_view.py` (77 items, 2,908 lines), `src/anesthesia_sim/app/dashboard_frame.py` (64 items, 4,604 lines) and `src/anesthesia_sim/app/controller.py` (63 items, 4,435 lines). The two live generator heads, `PL-GJ1W` and `PL-LHCL`, are both in `core/`. A declared file is an item's scope, not proof that its defect lay there, so this is a lead, not a verdict.

**Why it matters.** Triage's generator check reads each filing for the fact it misread. It cannot see that many unrelated misreads land in the same few files, which is the signal the software-engineering literature uses to find an architectural cause. A file that keeps collecting defects for different reasons is a design problem that no single item names.

**What the research says.**

1. Kim, Zimmermann, Whitehead and Zeller, "Predicting Faults from Cached History", ICSE 2007 (https://www.st.cs.uni-saarland.de/edu/softmine2007/Papers/kim-icse-2007.pdf, about four fifths of the text read 2026-11-23): "the cache selects 10% of the source code files; these files account for 73%-95% of faults", over seven open-source projects. Temporal locality, faults appearing "in bursts within the same entities", contributed most.
2. Xiao, Cai, Kazman, Mo and Feng, "Identifying and Quantifying Architectural Debt", ICSE 2016, doi:10.1145/2884781.2884825 (https://personal.stevens.edu/~lxiao6/papers/ICSE-16-Debt.pdf, first 60% read): files that change together in history, combined with their structural dependencies, form four patterns (hub, anchor submissive, anchor dominant, modularity violation). The top five debts covered "8% to 25%" of error-prone files and "20% to 61%" of maintenance effort in seven Apache projects. Those projects had 53 to 92 months of history, and the paper names no minimum size.
3. Mo, Cai, Kazman, Xiao and Feng, "Architecture Anti-patterns: Automatically Detectable Violations of Design Principles", IEEE Transactions on Software Engineering, doi:10.1109/TSE.2019.2910856 (https://par.nsf.gov/servlets/purl/10118809, first 40% read): "files involved in these architecture anti-patterns are more error-prone and change-prone", and "Unstable Interface and Crossing contribute the most by far".
4. Tornhill and Borg, "Code Red: The Business Impact of Code Quality", arXiv:2203.04374 (2022, first 70% read): over 39 proprietary codebases, "Alert code results in 15 times more reported Jira defects than Healthy code", and resolving issues in low-quality code took "on average 124% more time in development". The study is correlational.
5. Gall, Hajek and Jazayeri, "Detection of Logical Coupling Based on Product Release History" (https://plg.uwaterloo.ca/~migod/846/papers/gall-coupling.pdf, full text read): files that change together reveal "hidden dependencies not evident in the source code".

None of these was tested on a project with one developer. This repository differs in a way that helps: it records each defect's files in its item, where those studies had to recover them from commit messages.

**Decision needed.** Should each release cut print a short hotspot reading for the simulator: the files with the most defect- and safety-classed items over recent weeks, and the pairs of files that most often change together, with the top few handed to a design review? The other option is to leave defect location unread, as now.

**Recommendation.** Build it, as a report and never as a gate. It reads records the store already holds, and the papers above agree that location is where architectural causes show. It is the owner's call because it is new workflow machinery that would hand design reviews to the simulator queue.

**Done when.** The owner's answer is recorded here. If yes, `bin/docket release` prints the reading, a test pins its counts on a fixture, and the first reading's top files each have a design-review item or a recorded reason for none.

**Generator check.** One instance: a signal no reader collects. It is not a member of an existing head.

**Answer, 2026-11-24.** Build the hotspot reading, as a report and never as a gate (project owner, 2026-11-24, ratified, over leaving defect location unread). The owner answered "Agree with best practice" to the recommendation above.

**Done 2026-11-24.** `docket.hotspots.read` counts, for each simulator source file, the items classed defect, safety or science that were filed in the eight weeks before a cut and whose `touches` name it. It keeps the five files with the most, and for each the file those items most often name beside it. `bin/docket release` prints the files that no design review covers, and prints nothing when a review covers every one. A design review is an item under the `hotspot-review` feature whose `touches` name the file. An open review covers the file. A finished one covers it until three more defects name the file after it closed, and a dropped one covers nothing.

Four choices were made here rather than put to the owner, because each is internal to the reading:

1. Defect location is read from `touches`, not from git. Each item records the files its work covers, which the papers above had to recover from commit messages, and the reading then needs no history, so it also works in a shallow clone. Git's history would add files a change touched without declaring them. It is left out until a review finds `touches` misleading.
2. Files that change together are shown as each file's most frequent partner among the same defect items, rather than as a separate list of pairs, so each file takes two lines.
3. Five files over eight weeks, with `science` counted beside `defect` and `safety`. Five is close to the 10% of files that Kim et al. found holding most faults, since about 70 source files had a defect in the window. Eight weeks matches the inflow trend test, so one cut reports on one stretch of time. A `science` item is a wrong citation or parameter, which the project's safety classes already treat as a value that could mislead.
4. The cut says nothing when every top file has a review, so it speaks only when a review is owed, as the inflow report does.

The first reading, over 2026-09-29 to 11-23, named `controller.py` (48 items), `dashboard_frame.py` (48), `simulation_view.py` (39), `run_view.py` (35) and `area_layout.py` (24), all under `src/anesthesia_sim/app/`. The first four are named together often, by 37 of the 108 items that name any of them, so one review takes them, `PL-DZHD`. `area_layout.py` shares at most 7 items with any of them, so `PL-Y2CB` reviews it alone.

The same change rewords the inflow miss's instruction, which said to file an investigation unless the feature listed "an item for this week". It now says "an open item on this miss", since a miss covers eight weeks.

Files checked for prose the change made wrong: `subprojects/docket/README.md` (new section "Where simulator defects land"), `subprojects/docket/src/docket/cli.py` (`cmd_release`, `_missed_expectations`), `subprojects/docket/src/docket/render.py`, `.claude/skills/docket/modes/release.md`, `.claude/skills/docket/modes/triage.md` and `docs/features.toml`.
