---
id: PL-2D1S
title: Find what drives the rise in red CI runs per pull request, from 17% of closed items in ISO week 38 to 49% in week 43
priority: P2
effort: M
status: done
classes: infra
feature: model-review
touches: docs/items, docs/model-review.md
added: 2026-10-25
closed: 2026-10-25
pr: 1828
payoff: the cause of the doubling in red CI runs per pull request is named and has an item
verify: grep -qE '^\*\*Classified\.' docs/items/PL-2D1S-*.md
---

**Problem.** Find what drives the rise in red CI runs per pull request, from 17% of closed items in ISO week 38 to 49% in week 43

**Measured 2026-10-25, in the first model review** (`docs/model-review.md` §
"Run of 2026-10-25, the first"). The share of closed items whose pull request
had at least one failed CI run, by the ISO week the item closed: 18% in week
36, 23% in week 37, 17% in week 38, 30% in week 39, 25% in week 40, 37% in
week 41, 32% in week 42 and 49% in week 43. Runs were joined to a pull request
through its head branch and the time it was open, from `docs/ci-runs.tsv`.
Part of week 43 is `#1773`, which broke the second test job on every
apparatus pull request until `#1774`. The rise began weeks before that.

**Why it matters.** A red run costs a push and a wait, and the rise confounds
every comparison of red runs between models, effort levels and origins.

**Done when.** The failed runs since week 39 are classified by the failing
job and step (a check that refused correct work, a real defect caught, a
flaky test, a break on the base branch), with counts, and the largest class
has an item.
Record the classification in a `**Classified.**` paragraph here.

**Generator check.** Not yet known: this item is the search for a mechanism.
If the classification finds one mechanism behind three or more red-run
causes, record it as a generator then.

**Classified.** Checked 2026-10-25. The red runs are the 335 runs with
`conclusion` `failure` on the pull requests of the 1,273 items closed in ISO
weeks 39 to 43. A run was joined to a pull request through its head branch
and the time it was open, as the review did, and the 1,818 closed pull
requests were read from GitHub's pull request listing. The failing job and
step of each run came from GitHub's jobs API. Each of the 140 runs outside
the two record steps was then read in its own log, through the GitHub
connector, because the proxy refuses the storage host that log downloads
redirect to. Three log reviews split the 140 by check, and two of their rows
were re-read here against the logs.

| Class | Runs | What they were |
| --- | --- | --- |
| A check refused correct work | 203 | 132 the number-record step of `pr-title` failing until `bin/docket record N` lands, by design; 63 the body-record step, all on 2026-09-26, between `#1068` adding it and `#1118` retiring it; 5 tests pinning behaviour the branch correctly replaced; 2 a branch stacked on another's closure; 1 a false positive in a test-name check |
| A real defect caught | 118 | 38 a title not leading with every item the branch closes; 16 an item rule (work done with the item left open, or a `verify:` already passing); 18 a whole-repository self-check test refusing a file the branch added; 6 the formatter or lint on a branch file; 4 a test the branch broke; 36 a `tools/` check refusing the branch's own change, 6 of them a container path that passed locally because the check read the session's disk (4 path citations on 2026-09-21, which `PL-H0CF` fixed, and 2 quotations on 2026-10-17, fixed here) |
| A break on the base branch | 8 | 3 an unformatted item file on `main` after `#1722`; 2 a release tag made a minute after its merge; 2 closures on `main` without `pr:` racing `#1056`; 1 `#1773`'s costly-test skip |
| A flaky test or runner | 5 | 3 jobs GitHub never gave a runner, on 2026-10-05; 1 an xdist worker crash in a Qt test; 1 a fixture `git commit` exiting 128 |
| A gate newer than the branch | 1 | the no-claim rule from `#991`, a minute after it merged |

**What drives the rise.** The two record steps landed in week 39, and they
are the whole of it. The share of closed items with a red run outside those
two steps was 12%, 11%, 22%, 10% and 22% in weeks 39 to 43, against 18%,
23% and 17% in weeks 36 to 38. The share with a caught defect was 11%, 10%,
10%, 7% and 20%. So more defects are not reaching CI. The number hold alone
fails one closing pull request in five every week since 2026-09-26: 21%, 16%,
12%, 24% and 20% by the week it merged, the same for every kind of branch.

**The week-43 figure has moved since the review.** Re-run on this tree, week
43 reads 38% (87 of 231), not 49%, because 77 items closed later on
2026-10-25 joined the denominator and 9 of them had a red run. Without them
it reads 51% (78 of 154). Weeks 36 to 42 reproduce the review's figures
exactly.

**Items.** The largest class is the number hold, now `PL-86DN`, which
reopens `PL-1DZF`'s ratified decision to accept it and recommends opening
each claimed item's pull request as a draft at the claim. `PL-SW87` keeps
both holds out of the review's red-run measure. `PL-3JG7` holds the 32
defect runs that a local `make check` would have refused. The container-path
quotation was a defect in `tools/doc_check.py`'s `check_quoted_sources`,
fixed on this branch with a regression test.

**Generator check, answered.** One mechanism is behind three red-run causes:
a hand step that must follow the closing push. That covers the number hold,
the retired body record and the title that lags its closures. But no three
items name it, and a generator is counted by the items it causes, so it is
recorded in `PL-86DN` as an ordinary item.
