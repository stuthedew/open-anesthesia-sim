---
id: PL-JT1C
title: Run the model review of 2026-11-24: refresh the session ledger and CI history, read each trial session's arm, compute each arm's required sample size from the first closed outcome windows, and run the blind-review pass check
status: done
feature: model-review
touches: docs/model-review.md, docs/session-ledger.tsv, docs/ci-runs.tsv, tools/ci_runs.py, tests/unit/test_ci_runs.py, tools/effort_trial.py, tests/unit/test_effort_trial.py, .claude/skills/model-review/SKILL.md, .claude/skills/docket/modes/triage.md, docs/apparatus.md, docs/maintainer.md
added: 2026-11-24
closed: 2026-11-24
pr: 2318
tests: tests/unit/test_ci_runs.py::test_a_day_at_the_listing_cap_is_read_in_halves_and_loses_no_run, tests/unit/test_effort_trial.py::test_a_generator_cause_session_stays_in_its_drawn_arm
---

**Problem.** Run the model review of 2026-11-24: refresh the session ledger and CI history, read each trial session's arm, compute each arm's required sample size from the first closed outcome windows, and run the blind-review pass check

**Generator check.** A one-off. The listing cap that `PL-4SFQ` made the CI
tool refuse was reached because the project grew, not because that fix
failed, and the moved-session change reverses a ratified decision on new
evidence rather than repairing a defect. `PL-JYC2` and `PL-VGVV`, filed by
this run, re-enter no closed item.

**Why it matters.** The project owner asked for this month's run on
2026-11-24 (project owner, 2026-11-24): the main question is the effort trial,
`high` against `xhigh`, assigned by `PL-HYRM` and analysed under `PL-63CB`
§ "Effort monitoring". It is the first run at which trial items have closed
30-day windows. A scheduled run earlier that day could not finish because it
had no `claude-code-remote` tools, and committed nothing.

**What the run does.** It follows `.claude/skills/model-review/SKILL.md` in
full: it refreshes `docs/ci-runs.tsv` and `docs/session-ledger.tsv`, reads each
cloud session's arm from the first "Effort trial:" line of its session-start
digest, leaves out threads and sessions with no arm and counts each group,
keeps moved sessions in the arm they drew (decision 1 below), computes each arm's required sample size from the observed rates,
reports by model and by split period, runs the blind-review pass check, and
writes the run's entry into `docs/model-review.md`.

**Best practice for the trial's analysis, researched 2026-11-24.** The owner
asked whether the trial follows best practice. Sources read in this session:
the CONSORT 2025 explanation and elaboration (Hopewell S et al. BMJ
2025;389:e081124, doi:10.1136/bmj-2024-081124), full text, items 16a, 16b and
21b; the abstracts of Donner A, Klar N, Am J Public Health 2004;94(3):416-22
(doi:10.2105/ajph.94.3.416), of the surgical-trial clustering simulation in Br J
Surg 2018;105(3):182-191 (doi:10.1002/bjs.10763), of DeMets DL, Lan KK, Stat
Med 1994;13(13-14):1341-52 (doi:10.1002/sim.4780131308), and of Friede T,
Kieser M, Pharm Stat 2013;12(3):141-6 (doi:10.1002/pst.1564).

1. **Moved sessions are analysed in the arm they drew** (project owner,
   2026-11-24, ratified, over leaving them out of both arms as `PL-6LVZ` set).
   Item 21b: "To preserve the benefits of randomisation, all randomised
   participants are included in the analysis and retained in the group to
   which they were allocated", and excluding them "may compromise the
   randomisation". A move picks out a generator's cause, the hardest work, so
   leaving it out is not random. The result with moved sessions left out is
   reported beside the primary one.
2. **The session, not the item, is the unit of randomisation**, so the items
   of one session are analysed as a cluster. Taken without asking, because the
   sources give one answer: standard methods are invalid when clusters are
   randomised and the individual is the unit of inference, unless the
   analysis allows for the clustering (Donner and Klar), and ignoring
   clustering raised the false-positive rate to as much as 12% in the
   simulation (abstract only; see the recheck below).
3. **Repeated monthly looks use an O'Brien-Fleming-type alpha-spending
   boundary** (Lan-DeMets), which allows any number of looks at any time,
   instead of 0.05 divided by six looks. Taken without asking, for the same
   reason; CONSORT item 16b asks that the method be stated.
4. **The required sample size is computed from the pooled outcome rate of both
   arms**, never from the difference between them, which keeps the
   re-estimation blind (Friede and Kieser recommend the pooled one-sample
   estimator).
5. **The trial's primary outcome is also analysed as the time from merge to
   the first failure** (project owner, 2026-11-24: "And analyze expected time
   to bad outcome (following best practice)?"). Sources read: the abstracts of
   Schoenfeld DA, Biometrics 1983;39(2):499-503 (PMID 6354290); Pocock SJ,
   Clayton TC, Altman DG, Lancet 2002;359(9318):1686-9
   (doi:10.1016/S0140-6736(02)08594-X); Royston P, Parmar MKB, BMC Med Res
   Methodol 2013;13:152 (doi:10.1186/1471-2288-13-152); Uno H et al., J Clin
   Oncol 2014;32(22):2380-5 (doi:10.1200/JCO.2014.55.2208); Chen X, Harhay MO,
   Li F, Biom J 2023;65(6):e2200002 (doi:10.1002/bimj.202200002); and Amorim
   LDAF, Cai J, Int J Epidemiol 2015;44(1):324-33 (doi:10.1093/ije/dyu222).
   A plain mean time to failure cannot be estimated, because most items never
   fail within the follow-up. The restricted mean failure-free time over the
   first 30 days is the model-free measure Royston and Parmar and Uno et al.
   recommend, and the hazard ratio is secondary. The failures needed, not the
   items, set the sample size (Schoenfeld). An item that fails twice counts
   once.
6. **The smallest difference worth acting on is a hazard ratio of 1.3**, the
   realistic difference, and the trial cannot reach it (project owner,
   2026-11-24: "When you ask me for smallest size to act on I'll ask for best
   practice"). Source: DELTA2, Cook JA et al., BMJ 2018;363:k3750
   (doi:10.1136/bmj.k3750), full text read through PMC6216070 by a subagent of
   this session. It says the target for a definitive trial "should be one
   considered to be important to at least one key stakeholder group", that
   "the anchor and opinion seeking methods are to be favoured" for
   importance, and that "the opinion seeking and the review of the evidence
   base methods are recommended" for a realistic difference. The owner's
   recorded opinion is that price never justifies a setting that may be less
   correct (`PL-2D28`), so any real rise is important, and importance sets no
   lower limit. The realistic difference then comes from the evidence. On
   Anthropic's 463-problem SWE-bench Pro subset, Opus 5.5 solved 95.5% at
   `high` and 96.5% at `xhigh` (*Optimizing for cost and intelligence*,
   https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence,
   read 2026-11-24 by a subagent). Failures were 4.5% and 3.5%, a ratio of
   about 1.3. The page calls its figures "directional, not guarantees", and
   the `xhigh` figure is one run. The sample size is also given at 1.5, 2.0
   and 3.0, as DELTA2's Table 1 item 5d asks. The monthly looks measure their
   information against the failures needed to detect a doubling, so that the
   trial can still stop early for a large harm.
7. **A change to the trial's outcome would follow Evans** (Evans S, PLoS Clin
   Trials 2007;2(4):e18, doi:10.1371/journal.pctr.0020018, full text read
   through PMC1852589 by a subagent of this session). A change is acceptable
   only when "the decision is independent of the data obtained from the trial
   to date", and "Even DMC review of pooled data can suggest treatment
   effects". The infeasibility above rests only on data from before the trial,
   the items merged 2026-10-11 to 2026-10-25, and on the trial's accrual. A
   new outcome would be tested only on items merged after the change, as the
   paper's staged design does, and the change would be recorded as an
   amendment in `docs/model-review.md`.
8. **The analysis adjusts for item kind, size and lane, and treats a
   difference between kinds as a hypothesis** (the owner asked on 2026-11-24:
   "it seems like a pretty heterogenous data set (defects, planning, new
   features) would it make sense to do subgroup analysis? Research best
   practice"). Taken without asking, because the sources agree. Points 7 and 8
   of the trial's amendment in `docs/model-review.md` carry it. Sources, with
   what was read of each:
   - Kahan BC et al., Trials 2014;15:139 (doi:10.1186/1745-6215-15-139), full
     text through PMC4022337. Adjusting for known prognostic covariates raised
     power from 80% to a median of 92.6% over 12 outcomes, and adjusting for
     three covariates unrelated to the outcome lowered it at most to 78.5%.
     The covariates are named before the data are seen. With a time-to-event
     outcome and few events, too many covariates can raise the false-positive
     rate. An adjusted hazard ratio compares like items, so it differs from the
     unadjusted one.
   - Brookes ST et al., Health Technol Assess 2001;5(33): the executive
     summary, and the INAHTA brief that summarises the monograph, read by a
     subagent. The monograph's body was not reached. Tests within each
     subgroup found effects in 7% to 66% of simulations where none existed,
     and an interaction as large as the overall effect needed four times the
     sample. Their 2004 paper (J Clin Epidemiol 57:229-36,
     doi:10.1016/j.jclinepi.2003.08.009) had no reachable full text and is not
     relied on.
   - Kent DM et al., the PATH Statement, Ann Intern Med 2020;172:35-45
     (doi:10.7326/M18-3667), full text through PMC7531587. Risk-based
     subgroups are of most value "When there is a well-established overall
     treatment effect", subgroup results from overall null trials "should be
     interpreted cautiously", and selecting effect modifiers by
     one-variable-at-a-time tests is to be avoided.
   - Schandelmaier S et al., ICEMAN, CMAJ 2020;192(32):E901-6
     (doi:10.1503/cmaj.200077), main text read by a subagent; its appendices
     were not reached. Credibility rests on a direction stated in advance,
     prior evidence, a test for interaction, few modifiers tested, and no
     arbitrary cut points.
   Kind and size predicted failure before the trial, on the 376
   implementation items merged from 2026-10-11 to the trial's start whose
   window has closed (21 failures): kind chi-square 6.73 on 2 degrees of
   freedom, size 9.74 on 3. Lane did not (1.74 on 3), and is kept because the
   skill's step 4 names it.

**Full-text recheck, 2026-11-24.** The owner asked that a cited paper's full
text be read, not only its abstract (`PL-KQF4`). A subagent rechecked the
sources of decisions 2 to 5 against their full texts where one could be
reached, without pirate sites.

- Royston and Parmar 2013 (PMC3922847), Uno et al. 2014 (PMC4105489) and
  Amorim and Cai 2015 (PMC4339761): full text read, and each supports its use
  above. Royston and Parmar call wider use of the restricted mean "merited"
  rather than recommending it. Amorim and Cai also cover multi-state models.
- Donner and Klar 2004 (PMC1448267): full text read. They reject the "unit of
  analysis" framing, so decision 2 now says "unit of inference".
- Chen, Harhay and Li 2023 was cited wrongly. It concerns regression on the
  restricted mean survival time, not a Cox model, and only its abstract could
  be reached. The source for the small-sample correction of a Cox model's
  cluster-robust variance is Wang X, Turner EL, Li F, Biom J
  2023;65(3):e2200113 (doi:10.1002/bimj.202200113), read in full as the arXiv
  preprint 2203.02560v2. It says the default sandwich estimator "tends to
  underestimate the variance" when clusters are few. Chen et al. stays the
  source for clustered restricted-mean regression, from its abstract only.
- Schoenfeld 1983 could not be reached. The events formula was checked in Wu
  J, Xiong X, Stat Biopharm Res 2017;9(1):35-43 (PMC5619877), read in full,
  which states it and attributes it to Schoenfeld 1981 (Biometrika
  68:316-319) and 1983. So both are cited.
- Pocock, Clayton and Altman 2002, DeMets and Lan 1994, Friede and Kieser 2013
  and Dell-Kuster et al. 2018: no full text could be reached (publisher
  refusals, closed repository copies). Each claim above that rests on them
  rests on the abstract only. Two points are not in the abstracts: that the
  plot shows the numbers still followed (Pocock), and that an
  O'Brien-Fleming-type function spends little of the significance level early
  (DeMets and Lan). The 1.0425 inflation does not rest on either, because a
  simulation checked it. The owner was asked for these four papers' full
  texts.

**Result, 2026-11-24.** The run's entry is in `docs/model-review.md` under
"Run of 2026-11-24", and the trial's record there carries the amended analysis
plan. In short: 120 cloud sessions drew an arm, 135 items were worked only by
them, and the trial is not yet adequate. At the realistic hazard ratio of 1.3
it needs 476 failures, which cloud sessions alone would take about twelve
years to supply. Threads do about five in six of the items and are not in the
trial. The owner chose on 2026-11-24 to bring them in (`PL-C38D`), and agreed
to a less absolute form of the cost rule (`PL-1WTY`). Two findings
were filed: `PL-JYC2` (arms kept only in the harness's events) and `PL-VGVV`
(a third of the `xhigh` arm ran at `high`).

**The CI history tool.** The first refresh refused 2026-11-22, which held
1,076 runs, more than GitHub's listing returns for one query.
`tools/ci_runs.py` now reads a day at the cap in halves, down to one second, the finest time
GitHub's `created` query can name.
The new test failed on the code before the fix: `uv run pytest -q
tests/unit/test_ci_runs.py` gave `ci_runs.RefreshFailed: 2026-11-22 holds 1076
runs, and GitHub lists at most 1000 for one query` in
`test_a_day_at_the_listing_cap_is_read_in_halves_and_loses_no_run`.

**Moved sessions.** Decision 1 changed what a moved session's line says, so
`tools/effort_trial.py`'s `moved_line` and docstring, its test, the model
review skill's step 6, the docket triage mode, `docs/apparatus.md` and
`docs/maintainer.md` now say the review counts the session in the arm it drew.

**Docs swept.** `docs/model-review.md`, `.claude/skills/model-review/SKILL.md`,
`.claude/skills/docket/modes/triage.md`, `docs/apparatus.md`,
`docs/maintainer.md`, `tools/effort_trial.py`, `tools/ci_runs.py`, and a
search of the tree for "out of both arms" and "1,000-run".
