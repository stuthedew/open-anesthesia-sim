---
id: PL-TPXK
title: Review the four streamlining decisions of 2026-11-20 independently, and put the corrected whole-second stepping facts back to the owner
priority: P2
effort: S
status: done
classes: housekeeping
feature: standing-weight
touches: docs/items
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; it reviews how four workflow and design decisions were recorded, so the release does not wait on it
added: 2026-11-21
closed: 2026-11-21
payoff: the owner's choice of whole-second stepping rests on corrected figures, and each build item carries the review's notes
verify: grep -qF 'Answered 2026-11-21: keep whole seconds' docs/items/PL-TPXK-review-the-four-streamlining-decisions-of-2026.md
---

**Problem.** Review the four streamlining decisions of 2026-11-20 independently, and put the corrected whole-second stepping facts back to the owner

**Checked 2026-11-21**, in a project thread that took no part in the four decisions. The project owner had written "Would there be any good usage for like a review and rework something or verify things", and the coordinator asked for a review of the night's four decisions before their builds land. The thread read the four records at `origin/main` `2b17061`, reran their counts, and read each cited source again. The decisions are `PL-7CY5` (compute a run by one exact step per whole second), `PL-MR85` (sort the instructions loaded at launch), `PL-LY24` with `PL-KGPR` (retire four checks on the workflow's records) and `PL-LFJZ` (the form of a done-condition).

**Why it matters.** The owner ratified all four on a session's recommendation, and four build threads started on them the same night. A wrong figure in a ratified record is built on by every later session, and one of the four changes what a learner sees.

**Result.** Every count in the four records reproduces. Three statements that the owner was shown about whole-second stepping are wrong, and they understate what a learner sees at 1x and at 5x. The safety-critical standard and the expert-review section stay loaded in full under the sort. Five smaller defects are in the build items, and the build threads were told about each through the coordinator on 2026-11-21.

## 1. Whole-second stepping, `PL-7CY5`

**What holds.** The scripts are in `/mnt/project-files/v0.7.0/review-2026-11-21/`.

| Claim in the record | What the review measured | How |
| --- | --- | --- |
| One exact 1 s step per second is numerically sound | 86,400 repeated 1 s steps with a dial change each hour stay within 2.05e-13 of an 80-digit reference for sevoflurane at the reference settings, and within 1.74e-13 for desflurane at the supported maxima. That is slightly closer than 0.1 s steps. | `round.py`, with Python's `decimal` at 80 digits |
| 24 hours computes in 0.41 to 0.47 s and holds 6.2 MB | 0.449, 0.465 and 0.526 s for the three agents, and 6.22 MB as nine doubles per second | `step1s.py` |
| 24 hours through the shipped step with its mass-balance check takes about 2.5 s | 2.42 s, and the check passes at every step | `acct.py` |
| The fastest time constant is 6.0 s, and 14 to 17 s at the reference settings | 6.02 s for isoflurane at the maxima, and 13.7, 15.8 and 16.6 s for isoflurane, sevoflurane and desflurane at the reference settings | `step1s.py`, eigenvalues of `build_system_matrix` |
| The three displacements at a 0.1 s and a 1 s delay | 0.0067 and 0.066 (case opening), 0.050 and 0.50 (unperfused load, then dial off), 0.143 and 1.343 percentage points (ventilator start), with desflurane the worst agent in each | `ctrl.py`, with the reference test's own `_worst_over_agents` |
| The two quotations from OMNeT++ and the three from Fiedler | Each is on its page word for word | The two pages, read through a fetching agent |
| Korman and Mapleson 1997, and Mapleson and Korman 1998 | Each abstract states what the record says of it | PubMed records 9175984 and 10211005, abstracts only |
| 2,636 closed items, 16 test files, 9,381 lines, 13 constants and 7 members of `PL-GJ1W` | Each reproduces | `bin/docket`, `wc -l`, `grep` |

**What is wrong.** Each of these was in the record, on the decision card or in the reply that the owner read before choosing.

1. **"At 10x and faster nothing changes."** The interface has no 10x rate. `SUPPORTED_PLAYBACK_RATES` in `src/anesthesia_sim/app/playback.py` is 1, 5, 20, 60 and 300, and a control change takes effect on a grid of 0.1, 0.5, 2, 6 and 30 s at those rates. Under whole seconds the 5x grid also coarsens, from 0.5 s to 1 s. So two rates change, 1x and 5x, and three do not.
2. **"The 1x interface would show what the 10x interface shows today", and "the same figure the interface already shows today at 10x".** No rate shows 1.34 percentage points today. The published figures for today's rates are 0.14, 0.70, 2.5, 5.8 and 10 (`PUBLISHED_DISPLACEMENT_PER_GRID_STEP_PP` in `tests/reference/test_control_resolution.py`). The 1 s figure is new, and it falls between today's 5x and 20x.
3. **"The ventilator start, at 1.34 points for less than a second."** Only the delay is less than a second. After a ventilator start applied 1 s late, the displayed alveolar value differs from the on-time run by more than 1.0 percentage point from 0.8 to 3.0 s after the change, by more than 0.5 until 8.0 s, by more than 0.14 (today's worst figure at 1x) until 17.5 s, and by more than 0.05 until 113 s (`ctrl.py`).
4. **"The interface already works on a 1 s grid or coarser at 10x and faster"**, in the recommendation. The 5x grid is 0.5 s.

**What the record leaves out.**

1. **What the 1.34 is.** It is desflurane with the dial at 18%, fresh gas at 10 L/min and the ventilator off for five minutes, and then ventilation started at 12 L/min with a cardiac output of 10 L/min. The same manoeuvre gives 0.59 percentage points for sevoflurane at an 8% dial and 0.36 for isoflurane at a 5% dial (`peragent.py`). Each is about 7% of the dial setting.
2. **What a learner sees.** The run stays consistent with itself, because the change is recorded at the whole second at which it took effect. The displacement is the difference from a run in which the change took effect at the instant of the click. At 1x the readouts and the clock change once a second where they change ten times a second today, and at 5x five times a second in simulated seconds where they change ten times today.
3. **Nitrous oxide is off the timeline.** The record argues that the stored-state design is where the simulator must go "once nitrous oxide makes the equations non-linear". The algebra is sound. `ROADMAP.md` row 11 says the substance generalization and nitrous oxide "came off the timeline" on 2026-09-26, and they are in the "Beyond" row. So that argument is about work with no release.
4. **Four things `PL-SZ6G` (whole-second time and the 1 s step) must change and does not name.** The table of displacement at each playback rate in `docs/MODEL.md` § "Supported simulation step", and the three tables for each rate in the reference test: the 1x and 5x rows both become the 1 s figure. `PlaybackRate.steps_per_tick`, which refuses a fractional step count: a 0.1 s tick is 0.1 of a step at 1x and 0.5 at 5x. The sentence in `docs/INTERFACE.md` that begins "Simulated time is displayed to 0.1 s, which is exactly one simulation step". The chart's grid of tenths, `CHART_GRID_RESOLUTIONS_S` in `src/anesthesia_sim/app/chart_time_base.py`.
5. **Two things `PL-MH9J` (every state stored) must decide.** `tools/import_boundary_check.py` forbids `numpy` in every module under `core/`, so stored states held there are an `array.array('d')`. A chart window wider than its columns must not read every Nth second, which hides a short excursion. `PL-8LXM` holds the record of the minimum-and-maximum reduction for each column.

## 2. The sort of the instructions loaded at launch, `PL-MR85`

**What holds.** Rows 78 to 108 keep every line of the safety-critical clinical-output standard (`CLAUDE.md` § "Safety-critical clinical-output standard"), and rows 109 to 115 keep the section "Proactive expert review and domain best practices". Claude Code's memory documentation holds the quoted sentence, "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read through a fetching agent on 2026-11-21). The same page says that path-scoped rules "trigger when Claude reads files matching the pattern", and that the project-root `CLAUDE.md` is loaded again after compaction. It does not say that a rules file is. In this thread a path-scoped rule also loaded after a write to a matching file.

**Defects.**

1. **Row 72 and `PL-HS2T` (retire the branch-name check) collide.** Row 72 cuts the paragraph "Name the work after the item" to one line because `tools/branch_id_check.py` and `tools/pr_title_check.py` enforce it, and `PL-HS2T` deletes the first of the two. That check never required an id on each commit subject. It required one id for each branch: its docstring says "Not every commit - one is enough to make the branch visible". `PL-PNB2` (one line for each check) carries the correction.
<!-- absent: tools/branch_id_check.py -->
2. **`PL-G3KZ` (the cap) counts lines.** Lines in the four files run from 80 to 1,264 characters. The 39 non-blank lines of the safety standard and the review section are 7% of `CLAUDE.md`'s 583 non-blank lines and 18% of its 47,286 characters. A session could meet a line cap by joining lines. `PL-G3KZ` carries the correction.
3. **Row 180's rule needs `tests/` in its paths.** `PL-GDN7` (procedures that move to path-scoped rules) carries the correction, with a note on row 23.
4. **Rows 64 and 65.** The four conditions for fixing a defect in place move to the docket skill, and the table keeps no line of them. The third condition keeps a session from fixing a defect in `core/`, `data/`, `docs/MODEL.md` or `docs/INTERFACE.md` without an item. The line that stays in `CLAUDE.md` to name the skill should also name those four paths, because a session fixes a defect it has just found without first loading a skill. `bin/docket arm` holds a pull request that changes those paths for the owner's read, so a fix made in error cannot merge unread. `PL-CYT1` (procedures that move to the docket skill) is the item this is for, and no session holds it yet.

## 3. The check retirements, `PL-LY24` and `PL-KGPR`

**What holds.** A separate tally of `docs/ci-runs.tsv` gives the same 18,649 runs, 1,092 failed runs and 632 refusals, and every row of the table of 14 reproduces from `hits.json`. `PL-LY24` already says that each figure is a lower bound, because `make check` and the push hook refuse first.

**Notes for the build, sent to its thread.**

1. `PL-HS2T` named `make check`, CI and the push hook as the check's callers. `.claude/hooks/docket_branch_guard.py` also calls it, it is the only guard in CI on a second live claim on one item, and comments in `subprojects/docket/src/docket/render.py`, `vcs.py`, `claims.py` and `checks.py` rely on it. The build thread's triage of 2026-11-21 names all three refusals and the hook.
2. `PL-F7XT` called `docs/pr-bodies/` a closed archive. `.claude/skills/docket/modes/release.md` still adds to it at each release, in the step that runs `python3 tools/pr_body_check.py --recover`. The build thread's triage keeps the release step.
3. `tools/dead_ends.py check` never refused in 5,537 runs, and the tally's search for a step named `dead_ends` matches no step, because the steps are named "dead ends". No failed step of either name is in the file, so the zero is right. The 5,537 runs are not 5,537 chances: eight commits on `main` have changed `docs/dead-ends.md` since the check entered CI on 2026-09-21. The retirement still applies. Its cost is that an entry can leave that file without a recorded place, in a file changed about once a week.

## 4. The done-condition form, `PL-LFJZ`

**What holds.** `count.py` at `2b17061` gives 3,103 items, 2,648 with a `verify:`, 1,773 that run only `grep`, 845 that name a test and 794 that name none, 16 + 12 + 7 = 35 members of the three root causes, and 948 + 109 + 3 = 1,060.

**Corrections.**

1. `PL-LFJZ` says that the one-shot rewrite "states the same condition as 'the change has a test that fails without it'". The chosen field does not show that. It shows that the named test is defined and that the branch added or changed it. What shows that the tests detect the change is the close-out's check that the unit tests catch a mutant of each changed line (`.claude/skills/docket/modes/close-out.md`, the paragraph that begins "The mutation check refuses a branch", `PL-CZXN`), for every module under `src/` that imports no Qt. For Qt modules and for the workflow's own code, nothing shows it, as before. The review first recommended a run of the named tests on the commit where the branch left `main`, as SWE-bench does ("at least one test where its status changes from a fail to pass", Jimenez et al., ICLR 2024, § 2.1, https://arxiv.org/abs/2310.06770). It withdrew that the same night, because the mutation check is stronger and already runs.
2. `PL-N046` kept a `grep` command on items that delete code or change documents, and `PL-QTZG` removed the code that reads the command. The build thread's triage has docket read the files itself, which settles it.

## The question for the owner

**Decision needed.** Should runs still be computed at whole seconds, now that the figures are corrected? The choice is the owner's, because it changes what a learner sees at 1x and 5x, and because the owner ratified it on the wrong figures. The build of `PL-SZ6G` continues on whole-second time while the question is open, and it publishes no text about 1x or 5x until the answer.

**Recommendation: keep whole seconds.** The corrected figures change how large the cost is and not which design is better. The run a learner sees is still exact for the changes as recorded, the fastest time constant of the model is 6 s, and the worst figure needs an 18% desflurane dial with the ventilator off for five minutes. Tenths of a second keep today's timing at 1x and 5x, and cost ten times the memory and time: 62 MB and about 4 s for each 24-hour run.

**Done when.** The owner has answered on the corrected figures, and the answer is recorded here and beside `PL-7CY5`'s recorded answer.

**Answered 2026-11-21: keep whole seconds** (project owner, 2026-11-21, ratified, on the thread's decision card, over one rule at tenths of a second and over stopping the build to talk it through). The owner read the corrected figures in the thread's reply before choosing: no 10x rate, 1x and 5x both on a 1 s grid, and a worst case of 1.34 percentage points that stays above 0.5 for 8 s. `PL-SZ6G` (whole-second time and the 1 s step) may now publish its text about 1x and 5x, with these figures.

**Generator check.** Not a head, and a member of none. The three wrong statements have one cause, a playback rate recalled and not read from `app/playback.py`. That is one instance.

**Thread observation for `PL-CR81` (Projects threads and hooks).** This thread's first command printed "5 passed", so no guard hook ran in it, and no session-start digest printed (session `session_01GnrHQvfcZVcnrpLXTQd9Nf`, Claude Code 2.1.330, `CLAUDE_CODE_ENTRYPOINT=remote_projects`). `PL-CR81` is closed, so the observation is recorded here.
