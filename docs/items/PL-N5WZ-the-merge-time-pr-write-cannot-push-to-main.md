---
id: PL-N5WZ
title: The merge-time pr: write cannot push to main, because required status checks can never report on a GITHUB_TOKEN push - decide where the write is triggered instead
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: delegation
touches: .github/workflows/record-pr.yml, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests
added: 2026-09-03
---

**Problem.** `PL-WTQR` moved the `pr:` write to a job fired by the merge. The
job is correct and its first run proved it: it computed `pr: 261` for
`PL-WTQR`, committed it, and was refused by `main`.

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: - 3 of 3 required status checks are expected.
```

**This is not a bypass away from working, which is the part that decides the
item.** The requirement is *required status checks*, and it cannot be satisfied
by anything this job can do: a push made with `GITHUB_TOKEN` starts no
workflow, so `checks`, `floor` and `pr-title` can never report on the commit it
pushes. The `Base` ruleset was already disabled when the run happened - the
project owner turned it off trying to clear the way - and the push failed
anyway, so the ruleset was never the blocker either. The configurations that
would accept the push all weaken `main`'s own gate, which is a worse trade than
the per-item commit this was built to remove.

**Why it matters.** The job is parked, so nothing is failing - but nothing is
being written either, and the arrangement `PL-WTQR` replaced is what the queue
falls back to: a session reading an advisory, composing a commit, and often a
pull request, after every merge that closes anything. That is the cost the
project owner objected to, and it is back until this is answered. The second
cost is subtler and is why this is `needs-decision` rather than `ready`: a
parked workflow in the tree reads to a later session as a mechanism that
works, and `.claude/skills/docket/SKILL.md` currently tells sessions the
merge-time job writes the field. Until this closes, that instruction is
wrong in the direction that hides work rather than creating it.

**Decision needed.** Which trigger writes the field - a CI job on the pull
request branch before the merge, or a local fix mode riding the session's next
commit. The recommendation is the local one, for the reasons below. Answering
either way also settles whether `.github/workflows/record-pr.yml` is revived
or deleted, and the `SKILL.md` correction follows from the answer.

**The mechanism is not in question, only its trigger.** `vcs.closed_by` and
`docket record` are the write under every option below, and both are shipped
and tested. `.github/workflows/record-pr.yml` is parked rather than deleted for
that reason: it is one of the candidate triggers, not the feature.

**Where. Two candidates, and the second is recommended.**

- **Write on the pull request branch, before the merge.** Trigger on
  `pull_request: opened`, compute what the branch closes against its base -
  `pr_title_check.closes` already does exactly this - and push the `pr:` commit
  to the *head* branch, which is unprotected. Needs no protection change at
  all, and keeps the number exact, straight from the payload. It costs a bot
  commit landing on a branch a session may still be working, so that session's
  next push is rejected until it pulls. That friction lands on every item.

- **Write locally, riding the session's next commit.** A fix mode on
  `make check` that runs the write for any closure on the base that owes a
  `pr`. No CI, no permissions, no protection change, no bot commit anywhere,
  and no branch friction. The number is *inferred* rather than taken - but
  `PL-2XTF`'s second half already made that inference robust by falling back
  to the item's own file history, which is exact for the rider case
  `PL-GW37` found and for the UI-titled subject that defeated the subject
  scan. The field lands one merge later than the closure, which is what the
  advisory already describes as the normal transient.

**The exactness argument for the payload was worth less than `PL-WTQR` claimed,
and that is why the recommendation flipped.** It was the strongest reason to
prefer a CI trigger over a local one, and it rested on the subject scan being
the fallback. It is not: the file-history fallback shipped with `PL-2XTF` and
answers the cases the subject scan cannot. What the merge-time trigger uniquely
bought was therefore mostly already in hand.

**Done when.** A merge that closes items leaves those items carrying their pull
request number without a session composing a commit for it, and without any
change to `main`'s protection.

**Not to be confused with weakening the gate.** Disabling required status
checks on `main`, or exempting an actor from them, is not a route to be taken
here. The gate is the reason a red `main` means something.
