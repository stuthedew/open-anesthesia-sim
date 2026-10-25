---
name: model-review
description: Run the model review, which scores closed items by how their work held up and recommends model and effort settings. Use it when the owner starts one, monthly, or after a generator or cluster appears.
---

# model-review

The model review answers one question for the owner: which model and effort
setting does each kind of item need? It answers it from measured outcomes,
not from impressions. The owner set four goals on 2026-10-17, in this order:
reliability first and savings second; no burden on item or project sessions;
a review that brings findings to the owner unasked; and predictors of failure
that the review discovers rather than ones somebody named in advance
(`PL-63CB`).

So this skill loads only when a review starts, and costs every other session
nothing. A working session records nothing about itself. Everything the review
reads comes from records that already exist: the item store, git, the session
ledger, the CI run history and the harness's own session records.

## When to run it

Run it monthly, and after any generator or cluster appears. At each run,
check every generator recorded since the last run (project owner, 2026-10-19,
ratified, over a weekly or a quarterly cadence). A 30-day outcome window means
a shorter cadence would mostly re-score the same items. The first run also
backfills the ledger and takes the first full CI snapshot.

## What the review may conclude, and the bar for each

These rules were set by the project owner on 2026-10-17 (ratified, over
resident prose, over a tool that computes the analysis, and over a
self-assessment by each session).

- **A downgrade needs a pre-registered trial.** Moving an item type to a
  cheaper model or a lower effort needs a trial registered before it starts,
  in the form § "Pre-register a trial" gives below. The result applies to that
  item type only.
- **An upgrade needs one traced cluster.** A generator or cluster whose
  members were worked on a cheaper setting is enough to trial the stronger
  one.
- **Zero failures is not proof of safety.** With no failures in n trials, the
  95% upper bound on the failure rate is about 3/n (Hanley JA, Lippman-Hand A.
  If nothing goes wrong, is everything all right? JAMA 1983;249(13):1743-1745).

  | Clean items in a row (n) | Upper 95% bound on the failure rate, 1 - 0.05^(1/n) |
  | --- | --- |
  | 3 | 63% |
  | 10 | 26% |
  | 30 | 9.5% |
  | 60 | 4.9% |
  | 100 | 3.0% |

- **Confounding by indication.** `Item.model_guidance` sends safety, science
  and open-decision items to the strongest model by rule. So the hardest items
  are worked on the strongest model, and a naive comparison is biased against
  it. Compare within an item's attributes, and take the clean answer from a
  prospective assignment within one type where both settings are plausible.
  Never randomize safety-critical work (Psaty BM et al. J Am Geriatr Soc
  1999;47(6):749-754).
- **An association is a hypothesis.** Every association the screen finds is
  reported as something to trial prospectively, never as a conclusion.

## Refresh the records first

1. **The CI run history.** Run `python3 tools/ci_runs.py refresh`. GitHub
   deletes a workflow run 90 days after it ran, so `docs/ci-runs.tsv` keeps
   one row per run: run id, workflow, run number, attempt, event, branch, head
   commit, linked pull requests, status, conclusion and the two times. The
   tool asks for every day from the day before the newest row, keeps every row
   GitHub no longer returns, and keeps a pull request link that GitHub has
   dropped because the branch was deleted. It refuses a day that reaches
   GitHub's 1,000-run listing cap rather than read it short. Commit the file.
   Runs before 2026-08-22 were already deleted when the first snapshot was
   taken on 2026-10-19.
2. **The session ledger.** `docs/session-ledger.tsv` has one row per session
   in this repository (`docs/maintainer.md` § "The session ledger records
   what model and effort worked each item" has what each column means).
   Refresh it in three steps, so that no model retypes a value:
   1. Page through `list_sessions` (`mine: true`, `limit: 100`) from the
      `claude-code-remote` MCP server. A page is too large to show inline, so
      the harness saves it to a file. Parse that file with a script. Keep a
      session when any of its sources is this repository, not only its first.
   2. Fetch every Projects thread with `get_session`. `list_sessions` leaves
      threads out, because they carry the `hearth-thread` tag, and a session
      cannot pass the `tags` filter. Find them as the session ids in
      `Claude-Session:` trailers on `main` and in `docs/pr-bodies/` that have
      no ledger row yet.
   3. Rewrite the file, sorted by creation time. Keep every row whose session
      the harness no longer returns, because the ledger exists so that this
      record outlives the harness's.

## Join each closed item to its sessions

A closed item names its pull request in `pr:`. The squash commit for that pull
request on `main` carries each working session's `Claude-Session:` trailer,
and `docs/pr-bodies/` is the fallback. About two closed items share each
session, so the facts belong to the session, and an item is joined to them
when the review reads them (project owner, 2026-10-19, ratified, over model
and effort fields on each item, `PL-70M6`). An item whose sessions ran at
different models or effort levels is counted as mixed and left out of a
comparison between settings.

Read the store with `docket.store.read_items`, and place each item in its lane
with `Item.lane(workflow_paths)`. Never parse the item files by hand.

## Outcome measures

An outcome says whether the work held up. It accrues for weeks after the item
closes, so every measure has a window, and each run re-scores every item
whose window is still open. The window is **30 days** for an implementation
item and **90 days** for a design item. A design item is one whose classes
include `planning`, or whose brief records a decision the owner took, written
"(project owner, DATE". Each measure below is read from a record, not judged.

| Measure | Read from | Counted |
| --- | --- | --- |
| A fix that did not hold | `read_items`: later items whose `reenters:` names the item, and the item's own `recurrences:` entries that are not withdrawn | Filings dated within the window, with the sum of the re-entering items' efforts (S = 1, M = 3, L = 8) and, where the ledger joins them, their sessions' `cost_usd`. This is the primary outcome |
| A decision reopened | Later items and `docs/dead-ends.md` entries that name the item's id within a paragraph containing "reopen" or "refuted" | Matches within the window. This is a text match, so list each one in the report for a reader to confirm |
| Churn on its files | `git log --numstat` over the files its pull request added or changed, from its merge to the window's end | Lines added and deleted by later commits, divided by the lines the pull request itself added (relative churn: Nagappan N, Ball T. Use of relative code churn measures to predict system defect density. ICSE 2005) |
| Red CI runs on its pull request | `docs/ci-runs.tsv`: rows whose `pull_requests` holds its number | Runs with `conclusion` `failure`, and the distinct `head_sha` values created after the first failure (pushes after the first red run) |
| Review findings | The `Blind-review:` trailer on its squash commit, and the review threads on its pull request | The trailer's `findings` count, and the number of review threads opened by a reviewer other than the author |

**A citation is not rework.** An earlier version of this table counted every
later `defect` or `refactor` item whose brief named the item's id. On
2026-10-25 that marked 415 of 605 closed implementation items (68.6%), because
briefs here cite ids as context, as precedent and as examples. Counting a
citation only in the citing item's `**Problem.**` paragraph still marked 101
(16.7%). In a random sample of 25 of those matches, 8 said the cited work had
failed, 6 were arguable and 11 did not. A text match cannot separate those
cases, so the measure is triage's own judgment, written in `reenters:` and
`recurrences:` (`PL-J7YG`). Do not rank settings on a citation count.

**`reenters:` was first written on 2026-10-11**, and only part of the earlier
store was filled in afterwards. Seven of the eight sampled failures above were
filed before then, and none carries a `reenters:` naming the item it cites. So
an item whose window opened before 2026-10-11 is under-counted. Compare
settings only on items closed on or after that date, or stratify by the week
the item closed, and say which.

**Normalize by size.** Report each measure per item and per 100 lines the pull
request added. Compare items only within one effort size (S, M or L) and one
lane. A count with no denominator is not reported.

## Score design items by their fallout

A design or decision item is scored mostly by what happened downstream: the
later filings that re-enter it, its decisions later reopened or refuted, and the churn
on the files its pull request introduced. Its 90-day window means its verdict
arrives late by construction, so each run re-scores it until the window
closes, and the report says which verdicts are still provisional.

## Screen every recorded attribute

The predictors of failure are found by the screen, not named in advance.

1. Build one row per closed item. Take features from the item's front matter,
   the words of its brief, the shape of its diff (files, lines, lanes
   touched), its pull request's history, its joined sessions' ledger rows, and
   its outcome measures. Add judgment features only where a rule decides
   them, such as design against implementation above.
2. For each feature and each outcome, report the effect size with its 95%
   confidence interval and the n behind it.
3. Control the false discovery rate across every comparison with the
   Benjamini-Hochberg procedure at q = 0.10 (Benjamini Y, Hochberg Y. J R Stat
   Soc B 1995;57(1):289-300).
4. Report every association that survives as a hypothesis for a
   pre-registered trial. Also report what nobody asked: a model over-used on
   trivial work, a kind of session with high cost and little output, or a
   feature whose apparatus cost outran what it paid the product.

## Effort monitoring

From 2026-10-19 every session opens at `high`, as the owner's own judgment
(`docs/maintainer.md` § "Match effort to the standard the work is held to",
`PL-6XZG`). The owner asked to be told when there is statistically
significant evidence that working at `high` caused real-world issues, such as
a poor design choice that needed rework or behavior nobody intended. Each
monthly run does this:

1. **Unit and groups.** The unit is a closed item, joined to its sessions
   through the ledger. Items worked only at `high` on Opus 5.5 form one group.
   Items worked only at `xhigh` or `max` on Opus 5.5 form the other. Items
   worked at mixed levels are counted and left out.
2. **Outcomes.** The measures § "Outcome measures" defines above, within
   their windows.
3. **Adequate data first.** Before any test, compute the number of items each
   group needs to detect the smallest difference worth acting on, and state
   it. Until both groups reach it, report the counts and "not yet adequate",
   not a result.
4. **Adjust and correct.** Compare the groups within lane and item size, for
   example with a stratified comparison or a logistic regression. Monthly
   looks at the same question inflate false positives, so correct the
   significance level for repeated looks.
5. **Say what it cannot show.** From 2026-09-22 to 2026-10-19 the ledger holds
   Opus 5.5 sessions at `high` (189), `max` (242) and `xhigh` (59). But 174 of
   the 189 at `high` are Projects threads, a different way of working, and
   only 71 of the 242 at `max` are. So compare within origin as well. The
   groups also differ in date, project phase (product focus began 2026-09-25)
   and the apparatus around them. A significant difference is therefore an
   association that points at a cause, not proof of one, and the report says
   so.
6. **The randomized trial, from 2026-10-24 04:00 UTC.** Each new cloud
   session is assigned `xhigh` or `high` automatically (`docs/maintainer.md`,
   `PL-HYRM`). The trial's data starts when `PL-8MZ9` moved the draw into the
   session-start hook. A session's arm is the line starting "Effort trial:"
   that `tools/effort_trial.py session-start` prints into its session-start
   digest. Read it from the session's `hook_response` events with
   `list_events` (`kinds: ["system"]`). The arm is a hash of the hook's
   session id, so a resumed session prints the same arm again. A `/clear`
   gives a new session id and can change it, so use the first such line in a
   session, and count the sessions whose later lines differ. The split was one
   session in four at `xhigh` until `PL-TN18` merged on 2026-10-24, and one in
   two after, so analyze the two periods as strata. A session whose digest
   leaves 2 when divided by 4 was `high` under the first rule and is `xhigh`
   under the second, so it prints a different arm if it resumes on the new
   code; the first-line rule assigns it. A session with no line, or whose line
   says it is "in neither arm", has no arm and is counted and left out.
   Analyze sessions by the level they were assigned (intention to treat).
   Report, as a second result, the level they actually ran at: the lower of
   the arm and the level the app asked for, which `list_sessions` gives as
   `session_context.effort_level`, since a cap lowers a level and never raises
   one. A session with no such level started at its arm, because the hook also
   writes `effortLevel`. Report how many ran at a level other than the one
   assigned. Once it has adequate data, this randomized comparison is the
   primary result and the historical one supports it. Projects threads are not
   assigned and are analyzed apart. A thread whose transcript shows no
   session-start digest ran without this repository's hooks at all, so it
   has no arm.
7. **When to stop.** Once both arms reach the sample size step 3 computes, put
   ending the trial to the owner with the result. Put it to them at the run on
   2027-04-24 in any case, six months in, with the counts and what more data
   would buy. The trial ends only on the owner's word. This is a placeholder
   rule, set by `PL-HYRM` on 2026-10-19, for the owner to change.
8. **Report.** When the corrected test is significant, put it to the owner:
   the effect with its 95% confidence interval, the counts, the confounders,
   and a recommendation.

## Pre-register a trial

Write the trial into `docs/model-review.md` under "Trials", before its first
item is worked, in this form. A trial with any field blank has not started.

```text
### Trial: <item type> on <setting> instead of <setting>
Registered: <date>, by <session or owner>
Item type: <the rule that decides membership, read from the store>
Assignment: <how each item gets its setting, and who may override it>
Sample size: <n per arm, and the calculation behind it>
Outcome: <which measure above, and its window>
Decision rule: <the result that changes the default, and the one that does not>
Stop early if: <the harm that ends it, such as a safety-relevant defect>
```

## The report

Write each run's findings into `docs/model-review.md` under a dated heading,
newest first, and keep earlier runs as they were written. A run's entry holds:

- what was refreshed, with row counts for the ledger and the CI history;
- the effort monitoring result, or "not yet adequate" with the counts;
- each finding, with its evidence, its n and its confidence interval, marked
  either "trial this" or "change the default", each a decision for the owner;
- what nobody asked, as the screen's last step describes;
- which design verdicts are still provisional.

Then bring the owner only the findings that need a decision, each in one read:
the question, the recommendation and what it rests on.
