---
id: PL-86DN
title: A pull request opened after its closing push fails its first pr-title run until the number is recorded by hand: 132 red runs on 116 pull requests since 2026-09-26, one closing pull request in five every week, each costing a push and a full quality run
priority: P2
effort: M
status: done
classes: infra
feature: fewer-red-runs
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, tools/open_pull_requests.py, tools/pr_record_check.py, tests/unit/test_open_pull_requests.py, docket.toml, docs/apparatus.md, .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/start.md, .claude/skills/pull-request/SKILL.md
deferred-from: v0.7.0 - filed after Gate 3 froze; a CI cost in the workflow lane, not a hazard
added: 2026-10-25
closed: 2026-10-25
pr: 1832
payoff: a closing pull request starts green, so about 30 pushes and full quality runs a week stop being spent on writing one number
verify: grep -q 'def test_closing_an_item_writes_its_branch_s_open_pull_request_number' subprojects/docket/tests/test_cli.py
---

**Problem.** `tools/pr_record_check.py`, a step of the required `pr-title`
job, fails a pull request until every item it closes records `pr:` equal to
its number. The number exists only once the pull request is open. So a pull
request opened after the push that closes its item fails its first `pr-title`
run, and the session then runs `bin/docket record N` and pushes again. The
check's docstring calls this the design: "the pull request stays red until the
number lands".

**Measured 2026-10-25 by `PL-2D1S`**, from `docs/ci-runs.tsv`, GitHub's jobs
API for each failed run, and every closed pull request's head branch and open
time:

- 132 red runs since the check landed with `#1056` on 2026-09-26, on 116 pull
  requests. On 110 of the 116, the red run was the pull request's first
  `pr-title` run.
- 128 of the 132 were followed by a push of a new commit, and the full
  `quality` workflow ran on each of those commits. That workflow's median
  pull-request run took 6.4 minutes from 2026-10-19 to 2026-10-25 (296 runs).
- The share of closing pull requests that took the hold, by the ISO week they
  merged: 21% in week 39, 16% in week 40, 12% in week 41, 24% in week 42 and
  20% in week 43. It is the same for Projects-thread branches (26 of 138),
  harness-named session branches (67 of 323), item-named session branches
  (22 of 117) and worker branches (1 of 5).
- It is the largest single class of red run since 2026-09-21: 132 of 335.

**This reopens `PL-1DZF`'s ratified decision** (project owner, 2026-09-27,
ratified, "accept and count"). That case covered gate bursts of "at most 36
runs, paid once per gate", and said pr-record's first-run red was working as
designed, so nothing would be built. It rested on pr-record going "from 24
red runs on its first day to 3 on its second". The count did not stay there:
the hold has cost one closing pull request in five every week since. So this
is ordinary evidence the case did not carry, and the question goes back to
the owner.

**Why it is not simply sessions ignoring the close-out mode.** The close-out
mode says to run `record N` before the closure's commit, and the
`pull-request` skill says to open the pull request no later than the first
push of work. But the close-out mode also says the closure travels in the
same commit as its work (`PL-D2GW`). A session that keeps its work local
until it is finished therefore pushes work and closure together, then opens
the pull request, and the red run follows by construction. Only a pull
request opened before the work is pushed avoids it.

**Why it matters.** Each instance costs a push, a full quality run and the
wait on it, about 30 a week. It also puts a red run that means nothing beside
real failures, and that teaches a reader to skim past red.

**Decision needed.** Should every claimed item get its pull request at once,
as a draft, so the number exists before any work and the closing commit
carries it?

1. **Keep the hold and count it** (`PL-1DZF`'s decision). Costs about 30
   extra pushes and quality runs a week. `PL-SW87` keeps it out of the model
   review's red-run measure either way.
2. **Open the draft pull request at the claim.** `bin/docket claim` opens the
   branch's pull request as a draft when it pushes the claim, if none is
   open. `bin/docket set <id> --status done` then writes `pr:` itself
   whenever the branch's pull request is open, as `record N` does. The
   closing commit carries the number, so the first run after it passes. The
   check still refuses a merge where both steps were skipped. Costs: a draft
   pull request appears in the owner's list for every claimed item, including
   ones later abandoned, and `claim` needs a token allowed to open a pull
   request in every kind of session, which has not been checked for Projects
   threads. `start.md` already opens a draft where the claim's push opens the
   branch's first pull request, so this makes that the rule for every claim.
3. **Only make `set --status done` write the number when a pull request is
   open.** Cheaper, but it changes nothing for the 116 pull requests above,
   none of which had a pull request open when its item closed.

**Recommendation: 2.** It is the only option that removes the extra push
rather than relabelling it, and it keeps the merge hold that `PL-HMZZ` built.
The choice is the owner's because it reopens their ratified decision, and
because it changes what the pull request list shows them.

**Answered 2026-10-25: option 2** (project owner, 2026-10-25, ratified, over
keeping the hold and counting it, which was `PL-1DZF`'s decision, and over
writing the number only where a pull request is already open). `bin/docket
claim` opens the branch's pull request as a draft when it pushes the claim.
`bin/docket set <id> --status done` writes `pr:` from the branch's open pull
request.

One question was still open when the owner agreed: whether every kind of
session holds a token that can open a pull request. The docket package reads
the GitHub API through `vcs.py`, but it writes nothing there yet. Where a
session has no such token, `claim` says so and names the step the session
takes instead: it opens the draft with its own GitHub tool, as `start.md`
already asks at a branch's first push. Either way, the pull request exists
before the closing commit.

**Done when.** After `bin/docket claim` pushes a claim, the branch has an
open draft pull request, or `claim` has said it could not open one and what
the session does instead. `bin/docket set <id> --status done` writes `pr:`
equal to that pull request's number, so the closing commit carries it and the
first `pr-title` run after it passes.
`test_closing_an_item_writes_its_branch_s_open_pull_request_number` in
`subprojects/docket/tests/test_cli.py` pins that. `start.md`, `close-out.md`
and the `pull-request` skill describe opening the draft at the claim.

**Related, not this item.** 37 further red runs since 2026-09-21 were the
title half of the same job: a title that did not yet lead with every item the
branch closes. 20 of them were on four Projects-thread pull requests whose
later pushes each closed one more item (`#1601`, `#1620`, `#1686`, `#1761`).
Those are real failures the check caught, and most were fixed by a rename
with no new commit.

**Generator check.** One mechanism, a hand step that must follow the
closing push, is behind this hold, the retired body record (63 runs, all on
2026-09-26) and the title lag above. But no three items name it, so it is
recorded as an ordinary item rather than as a generator.
