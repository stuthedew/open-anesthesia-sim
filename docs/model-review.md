# Model review register

This file is the model review's record. It holds each pre-registered trial
and each review's dated findings, newest first. The procedure that writes it is
`.claude/skills/model-review/SKILL.md`. Write a trial here before its first
item is worked, and never edit a run's findings after they are written: a later
run that revises one says so under its own date.

## Trials

### Trial: effort `xhigh` against `high` on Opus 5.5 cloud sessions

Registered: 2026-10-19, by the project owner (`PL-HYRM`), with the split
changed on 2026-10-24 (`PL-TN18`)
Item type: every closed item whose sessions are all cloud sessions with an
"Effort trial:" line in their session-start digest; Projects threads are not
assigned
Assignment: a hash of the session id, one session in four at `xhigh` until
`PL-TN18` merged on 2026-10-24 and one in two after; the app's effort picker
can only lower the level
Sample size: computed at the first run that has outcomes to compute it from,
as the skill's effort monitoring step 3 says
Outcome: the skill's outcome measures, within their windows
Decision rule: a corrected significant difference is put to the owner with its
effect, interval, counts and confounders; the owner decides
Stop early if: never by a session; the owner ends it, and the review puts the
question at the run on 2027-04-24 in any case
Amended 2026-11-03 (`PL-6LVZ`, `PL-WBW3`): a session moved to another level by
hand, including one working on a generator's cause under the owner's rule of
2026-11-02, is counted and left out of both arms. A Projects thread is in
neither arm whatever its digest line says, because a thread never reads the
effort cap
Amended 2026-11-11 (`PL-7KF5`, project owner): the trial runs on every model a
cloud session is started on, and a change of model does not end it. The hook
already draws an arm whatever the model. The two arms are compared within one
model at a time, with model as a stratum beside the split period, and two
models' sessions are never pooled in one group. When a model first appears in
the ledger, check that it accepts both `high` and `xhigh`; a model that does
not is reported apart
Amended 2026-11-24 (`PL-JT1C`): this analysis plan replaces the rule of
2026-11-03 for moved sessions and the first run's division of 0.05 across six
looks. The project owner agreed to points 1 to 3 and asked that points 4 and 5
follow best practice. `PL-JT1C` holds the sources.

1. A session moved to another level by hand stays in the arm it drew, because
   the draw is what was randomized (project owner, 2026-11-24, ratified, over
   leaving it out of both arms). The comparison with moved sessions left out is
   a secondary result.
2. The items that share a session form one cluster, because the session is
   what was randomized, and every variance allows for the clustering.
3. Each monthly run from 2026-11-24 to 2027-04-24 is one look, and the
   significance level is spent by a Lan-DeMets function of O'Brien-Fleming
   type, two-sided, 0.05 in all. A look's information is the failures observed
   so far divided by the failures needed to detect a doubling (point 5). At six
   equal steps of information the boundaries would be |z| 4.80, 3.40, 2.79,
   2.45, 2.23 and 2.08. Each run computes its own boundary from its actual
   information. The looks raise the sample size by a factor of 1.0425, which a
   simulation of 400,000 trials confirmed (significance 0.049, power 0.800).
4. The primary outcome is a fix that did not hold, on implementation items,
   analysed as the time from merge to the first failure. Each item is followed
   until its first failure, 30 days after merge, or the run's date. The report
   plots each arm's cumulative share failed, rising, with 95% confidence bands
   and the number of items still followed. The headline effect is the
   difference between the arms in mean failure-free days over the first 30
   days (the restricted mean survival time). A Cox model stratified by split
   period and model gives the hazard ratio as a secondary result. The 30-day
   failure rate on items whose window has closed is reported too.
5. The smallest difference worth acting on is a hazard ratio of 1.3. It is the
   realistic one, and any real rise is important to the owner. The failures
   needed are 4(z₀.₉₇₅ + z₀.₈)² / (ln HR)², times 1.0425 for the looks and
   times the design effect (Schoenfeld 1983). The items needed are that number
   divided by the 30-day failure rate of both arms pooled, which keeps the
   estimate blind to the comparison. Each run also gives the numbers for a
   hazard ratio of 1.5, 2.0 and 3.0.
6. Until a look crosses its boundary, the report gives the counts and the
   outcomes pooled across the arms, and says the data are not yet adequate. A
   look that crosses its boundary reports the effect and its 95% confidence
   interval at once. The run of 2027-04-24 reports the effect and its 95%
   confidence interval in any case, so that the owner sees how large a rise
   the data rule out.

## Runs

### Run of 2026-11-24

Run by a Projects thread for `PL-JT1C`, the first run at which items in the
randomized effort trial have closed 30-day windows. The analysis scripts were
scratch work, kept out of the tree; each step below names the record it read.

**What was refreshed.** `docs/ci-runs.tsv` holds 21,254 runs after
`tools/ci_runs.py refresh` added 2,605. The refresh first refused 2026-11-22,
which held 1,076 runs, more than GitHub lists for one query, so the tool now
reads such a day in halves. The session ledger holds 1,508 rows after 264
were added and 1 updated, from two pages of `list_sessions` and `get_session`
for the 270 sessions named in `Claude-Session:` trailers that had no row.

**Who is in the trial.** The ledger holds 290 sessions created since
2026-10-24 04:00 UTC. 151 are Projects threads, which are in neither arm. Of
the 139 cloud sessions, 14 started before `PL-8MZ9` moved the draw into the
session-start hook at 21:06 UTC that day, so they print no arm, and 5 later
ones printed no "Effort trial:" line in the events read. 120 drew an arm. Every
arm agreed with the hash of the session id under the rule in force when the
session started. No session was moved by hand, and no session printed a
different arm later.

| Arm | Model | Split period | Sessions | Implementation items | Design items |
| --- | --- | --- | --- | --- | --- |
| `high` | Opus 5.5 | one in four at `xhigh` | 4 | 1 | 1 |
| `high` | Opus 5.5 | one in two at `xhigh` | 45 | 28 | 15 |
| `high` | Fable 5.2 | one in two at `xhigh` | 10 | 5 | 4 |
| `xhigh` | Opus 5.5 | one in two at `xhigh` | 46 | 58 | 10 |
| `xhigh` | Fable 5.2 | one in two at `xhigh` | 15 | 8 | 5 |

Fable 5.2 accepts both levels: the ledger records Fable 5.2 sessions at
`high` and at `xhigh`. Of the items merged since the trial began, 135 were
worked only by sessions with an arm, and none by sessions in both arms or on
two models. 638 were worked only in threads, 25 by a session with no arm, 6
by a session from before the trial, and 16 name no session.

**The level each session ran at.** 22 of the 61 sessions drawn `xhigh` ran at
`high`, because a level picked when a session is opened wins over the level
the hook writes. 1 of the 59 drawn `high` ran at `medium`. This makes the arms
more alike, so the comparison by drawn arm understates any difference
(`PL-VGVV`).

**Outcomes, pooled across the arms.** Of 100 implementation items, 32 have a
closed 30-day window, and 1 of them failed within it. Over all the follow-up, 2
items failed, both on the day they merged. The estimated share failed by 30
days is 2.0% (95% CI 0.5% to 7.8%), and the mean failure-free time over the
first 30 days is 29.4 days. 46 of the 100 had a red CI run while their pull
request was open, not counting the two hold steps. The items fall into 58
clusters of sessions, with a mean of 1.7 items and a largest of 9.

**Sample size: not yet adequate, and out of reach on cloud sessions alone.**
The smallest difference worth acting on is a hazard ratio of 1.3, as the
trial's record now says. Detecting it with 80% power, across six looks, needs
476 failures. The 30-day failure rate decides how many items that is. Before
the trial, 29 of 489 implementation items merged 2026-10-11 to 2026-10-25
failed within 30 days (5.9%), and their design effect for sessions was 0.95,
so 1.0 is used. The trial's own pooled estimate, 2.0%, rests on 2 failures.

| Hazard ratio | Failures needed | Items per arm at 5.9% | Items per arm at 2.0% | Months for the `high` arm on Opus 5.5, at 5.9% |
| --- | --- | --- | --- | --- |
| 1.3 | 476 | 4,010 | 11,888 | 143 |
| 1.5 | 200 | 1,679 | 4,978 | 60 |
| 2.0 | 69 | 575 | 1,704 | 20 |
| 3.0 | 28 | 229 | 678 | 8 |

The `high` arm on Opus 5.5 gains about 28 implementation items in 30 days and
the `xhigh` arm about 56. By 2027-04-24 that is about 170 and 341 items, so
about 30 failures at 5.9%, or 10 at 2.0%. A 95% confidence interval for the
hazard ratio would then span a factor of about 2.1, or 3.7, either way from
the estimate. Threads merged 498 implementation items in the same 31 days,
about five times the cloud sessions' 100. With threads in the trial, a doubling
would need about 2 to 6 months and a hazard ratio of 1.3 about 14 to 42.

**This look.** The trial has 2 of the 69 failures that its looks are
measured against, so its boundary is far above any value 2 failures could
give, and no comparison between the arms was made.

**The blind review pass check.** `uv run python tools/blind_review_report.py`
counted 547 pull requests merged after `#1767`. 244 owed one or more passes.
Pass 1 recorded 435 findings on 199 pull requests, 244 of them new and
marked blocking or should-fix. Pass 2 recorded 337 findings on 152, 74 of them
new and marked so. On the 150 pull requests that owed two passes, pass 2 found
72 new blocking or should-fix findings. That is above the bar of 3, so the
second pass stays. The report could not count `#1765` in full: it owed one
pass and has no `Blind-review:` record. No earlier run counted any pull
request, so no `--since` run was made. 30 items merged after `#1767` have a
later re-entry or recurrence. Of those 37 filings, 11 were filed on the
reviewed branch and are left out, which leaves 26. This run did not split them
by whether their pull request owed a pass.

**What nobody asked.**

- The trial's arms are read again from the harness's session events at each
  run. That took four background readers about 25 minutes each, and 8
  sessions needed a second try (`PL-JYC2`).
- `xhigh` sessions on Opus 5.5 merged 58 implementation items and `high`
  sessions 29, from 46 and 49 sessions. One cluster of sessions holds 9 items,
  so this count is not a result. It is reported because the item counts
  decide how fast each arm accrues.

**Still provisional.** Every trial item: 68 implementation items whose
30-day window is open, and all 35 design items, whose 90-day windows close
from 2027-01-22.

### Run of 2026-10-25, the first

Run by the "Complete workflow and CI items" thread for `PL-63CB`. The
analysis scripts were scratch work, kept out of the tree; each step below
names the record it read.

**What was refreshed.** `docs/ci-runs.tsv` holds 12,716 runs, from
2026-08-22, after `tools/ci_runs.py refresh` added 1,058. The session ledger
holds 1,244 rows after 56 were added and 3 updated: one page of
`list_sessions`, then `get_session` for the 18 thread sessions named in
`Claude-Session:` trailers that had no row.

**The join.** The store holds 2,113 closed items with `status: done` and a
`pr:`. 2,027 of them have a squash commit on `main` ending "(#N)", and 1,998
of those name at least one session that the ledger holds. 881 have a closed
30-day window. No design item has a closed 90-day window yet, so all 476
design verdicts are provisional. A run's red CI runs were joined through the
pull request's head branch and the time it was open, not only through the
run's `pull_requests` column. GitHub had already emptied that column for
almost every run whose branch was deleted, and only 1 item joined through it.

**Effort monitoring: not yet adequate.** No item worked only at `high` on
Opus 5.5 has a closed window, because `high` became the default on
2026-10-19 and the first window closes on 2026-11-18. 87 items worked at
`xhigh` or `max` on Opus 5.5 do. To detect a rise of 5 percentage points in
the rate at which a fix did not hold (from 4.1%), with a significance level of
0.05 divided across 6 monthly looks and 80% power, each group needs 595
items. The randomized trial has no outcome yet: the ledger holds 26 sessions
created after its start on 2026-10-24 at 04:00 UTC, none with a closed
window, so no arm lines were read.

Red CI runs need no window, since they are complete when the pull request
merges. Crude, items worked only at `high` on Opus 5.5 had a red run more often
(201 of 567, against 145 of 442 at `xhigh` or `max`). Stratified by the week
the item closed, its lane and its effort size, the Mantel-Haenszel odds ratio
is 1.16 (95% CI 0.77 to 1.75, p = 0.55). The crude difference is the time
trend described below, not the effort level.

**Findings.** Each is an association to trial, not a conclusion. The screen
made 73 comparisons, and 25 survived Benjamini-Hochberg at q = 0.10. Most are
the two confounders below, so only these are worth a decision.

1. **The rework measure does not discriminate. Change the measure.** 608 of
   881 items (69%) have a later `defect` or `refactor` item citing them inside
   their window, because briefs here cite ids freely. A measure that marks
   most items as failures cannot rank settings. The rate at which a fix did not
   hold, read from `recurrences:` and `reenters:`, is 36 of 881 (4.1%) and is
   the triage's own judgment, so this run uses it as the primary outcome. Filed
   to tighten the skill's definition.
2. **A fix did not hold more often on Opus 5.5 than on Opus 5: trial this.**
   16 of 87 against 20 of 794, odds ratio 8.7 (95% CI 4.4 to 17.4). The two
   models worked in different months, and `reenters:` was first written on
   2026-10-11, so a recent item was more likely to be judged at all. Workflow
   items (30 of 487 against 6 of 394) and `M` items (15 of 184 against 21 of
   697) show the same pattern. No change of default rests on this. It is the
   question the effort trial's later runs can answer, since both its arms are
   Opus 5.5.
3. **Red CI runs per pull request rose through the project, whatever the
   setting.** The share of closed items with a red run was 18% in ISO week 36,
   17% in week 38, 30% in week 39, 37% in week 41 and 49% in week 43. Part of
   week 43 is `#1773`, which broke the second test job on every apparatus pull
   request until `#1774` fixed it. That change is the confounder behind every
   red-run association with a model, an effort level or an origin. Filed to
   find what drives the rise.

   **Answered 2026-10-25 by `PL-2D1S`: the rise is two checks that fail by
   design.** Both landed in week 39 as steps of the required `pr-title` job.
   One fails a pull request until its closed items record its number, and the
   other, retired a day later, until its body was written into the tree.
   Together they made 195 of the 335 red runs on these pull requests since
   2026-09-21. Without them, the share with a red run was 12%, 11%, 22%, 10%
   and 22% in weeks 39 to 43, against 18%, 23% and 17% in weeks 36 to 38.
   `PL-SW87` keeps them out of this measure, and `PL-86DN` asks whether to
   remove the one still running.

**What nobody asked.**

- Projects threads did a third of the work. 716 of 2,113 closed items had a
  thread session: 533 at `high` on Opus 5.5, 115 at `max` on Opus 5.5 and 67
  on Fable 5.1. At least one thread in this project ran without the
  repository's hooks (`PL-CR81`), and such a thread has no session-start
  digest and no trial arm. While that holds, the trial's sample comes only
  from the other sessions.
- No `Blind-review:` trailer is on `main` yet. The trailer began with `#1767`,
  so the review-findings measure has no data until a simulator pull request
  carrying one merges.

**Still provisional.** All 476 design verdicts, and 1,232 implementation
verdicts whose 30-day window is still open.
