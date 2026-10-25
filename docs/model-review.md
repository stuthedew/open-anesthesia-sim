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

## Runs

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
