---
id: PL-WTQR
title: Write a closed item's pr: at merge time from the pull_request payload, so the backfill advisory and its dedicated commit stop existing
priority: P2
effort: M
status: done
classes: defect, infra
feature: delegation
milestone: v0.3.3
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests, .github/workflows/record-pr.yml, tests/unit/test_record_pr_workflow.py, .claude/skills/docket/SKILL.md, subprojects/docket/README.md
added: 2026-09-03
closed: 2026-09-03
pr: 261
verify: uv run pytest subprojects/docket/tests/test_cli.py tests/unit/test_record_pr_workflow.py && grep -q 'def closed_by' subprojects/docket/src/docket/vcs.py
---

**Problem.** `pr:` is derived data maintained by hand. `docket check` computes
the number, states the exact line, and then asks a session to retype it into a
file and commit it. `PL-QS72` made that the arrangement deliberately, and was
right to: the closure has to travel in the same commit as its work (`PL-P5S0`)
and the number does not exist until after that commit, so *something* has to
supply it afterwards. What `PL-QS72` settled was that erroring was wrong. What
it left open was who writes the field.

**Why it matters.** The project owner's reading, on seeing three of these in
one `make check`: "a really awkward workflow of backfilling PRs". It is, and
the cost is measurable rather than aesthetic.

- **A commit and usually a pull request after every merge that closes
  anything.** `#188`, `#189`, `#213`, `#216`, `#221`, `#237`, `#241`, `#247`,
  `#250` exist wholly or partly to write this field, and `#257`'s three items
  were being transcribed on a separate branch while this item was written.
- **Duplicate work between sessions.** The advisory-driven edit is the most
  deterministic work in the queue - the tool names the item and dictates the
  content - so every session that runs `make check` computes the same answer.
  Two did, and opened `#229` and `#230` for one identical insertion
  (`PL-QTSB`).
- **A failure no local tool can repair.** Where the squash subject names no id,
  there is nothing to recover from: `main` went red and the number had to be
  read off the GitHub UI by hand (`PL-2XTF`).

`CLAUDE.md`'s own test settles it. *A check that fires every run without
changing a decision is a defect in the check.* This one fires after every
merge that closes anything, and there is no decision in it.

**Where.** The write did not exist anywhere, which is the actual gap - both
halves of the existing machinery are readers. `vcs.closed_by` supplies what a
commit closed, `cli.cmd_record` writes the number onto it, and
`.github/workflows/record-pr.yml` runs the pair at the moment both facts are
certain.

**Done when.** A merge that closes items leaves those items carrying their
pull request number on the default branch, with no session involved, and the
advisory fires only when that did not happen.

**Worked 2026-09-03.**

**The number is taken, not derived, and that is the point.** Every existing
path infers it: `_merges_naming` parses the squash subject, `_number_closing`
falls back to the file's own history. Both are inferential and both have
failed - the subject scan mis-attributed a rider to its capture commit
(`PL-GW37`), and a UI-generated title defeated it entirely (`PL-2XTF`).
`github.event.pull_request.number` is the number, exactly. A caller handed it
by the event that fired needs no subject, so no subject can defeat it, which
is why `PL-2XTF`'s error class does not survive this: nothing is being
recovered from a title any more.

**`closed_by` compares trees, by id.** `status: done` in the commit's tree and
not in its parent's, which is `_number_closing`'s question asked forwards
instead of backwards. Three decisions in it are load-bearing:

- **By id, not by path.** A title edit renames an item's file, so a path
  missing from the parent tree proves nothing - the item may have been done
  under its old name, and comparing paths would stamp this commit's number
  over the one that actually closed it. One `ls-tree` of the parent removes
  the class, and a test holds it.
- **Only the files the commit touched.** `git diff --name-only` against the
  first parent, not `diff-tree`, which shows nothing on a true merge and would
  read as closing nothing.
- **A missing parent declines.** At `fetch-depth: 1` there is nothing to
  compare against, and "no parent" would otherwise read as *everything done
  here was closed here* - one number stamped across the whole store. This is
  the `PL-99Y4` rule applied to a new reader.

**A conflicting number is refused, never overwritten.** Two numbers for one
closure means one is wrong and nothing here can know which. A confident wrong
provenance is worse than the missing one this exists to supply.

**Both halves are kept, and they now answer to different failures.** The write
is the mechanism; `_check_closures` is what notices the mechanism did not run,
and its advisory says so in those words. Leaving it phrased as a chore would
have been the real defect - a session would discharge it by hand, restore the
per-item commit, and hide a broken job while doing it.

**What the workflow cannot do, and says so.** It runs on `pull_request:
closed` with `contents: write`, which GitHub does not grant to a fork pull
request. Every branch here is same-repository, so this is a degradation rather
than a hole: a fork merge simply leaves the field unwritten and the advisory
fires, which is exactly today's behaviour. The push also needs a bypass on the
protected default branch; without it the job fails loudly rather than silently
skipping.

**Two invariants are checked rather than reviewed** (`tests/unit/test_record_pr_workflow.py`).
The recording commit's subject must not read as a merge - a trailing `(#N)`
would make `_merges_naming` prefer *it* to the merge it is recording, and the
number in it would be right, which is what makes that failure hard to see. And
the checkout must stay at `fetch-depth: 0`, or `closed_by` declines on every
run and the workflow becomes an expensive no-op.

**The store is validated before the push, not after.** A push made with
`GITHUB_TOKEN` starts no further workflow, so `quality.yml` will not run on
the recording commit and the job's own `bin/docket check` is the only gate
there is.
