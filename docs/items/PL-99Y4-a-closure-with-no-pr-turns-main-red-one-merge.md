---
id: PL-99Y4
title: A closure with no pr: turns main red one merge later, because CI's shallow clone cannot recover the number
status: untriaged
added: 2026-09-01
---

**Problem.** `main` was red for two consecutive pushes today, 2026-09-01, and
nobody noticed. Run 33559... on `97573ae` and run 33560131271 on `3b37a75` both
failed on `bin/docket check`:

```
Errors (the store is wrong; fix before committing):
  PL-PF8H-...md: marked done on `origin/main` but records no `pr`; without it
  there is no way back from the closure to the work that made it
```

`PL-PF8H` closed in #162 without a `pr:`, which is the shape the `docket` skill
*prescribes* - "let the item land with an empty `pr`", so that the closure ships
in the same commit as the work and the merge race that lost `PL-D2GW` cannot
reopen. On its own merge commit `c663c13` the number was recoverable from the
merge subject, so the check raised an advisory and CI stayed green. One merge
later it was not, because `.github/workflows/quality.yml` runs
`actions/checkout` with no `fetch-depth`, which defaults to 1: the merge commit
naming #162 had scrolled out of the clone. Advisory became error, and `main`
went red one commit after the closure landed, not at the closure.

It went green again at `8836845` only because that pull request happened to
write `pr: 162` and `pr: 164` in, as tidy-up of what the local tool called a
grooming advisory. The repair was accidental.

**Why it matters.** It compounds, and it is armed right now. Every item that
closes under the prescribed workflow lands with an empty `pr:` and turns `main`
red on the next merge unless a follow-up beats it there. 78 items are open;
each one of them closes this way. The cost is a red default branch, plus the
session time to establish that the failure is not the incoming change's - this
capture cost one.

`PL-768D` is the live instance: it closed in #166 with no `pr:`, its merge
`055d1ca` is currently HEAD so the check still calls it recoverable, and the
next merge to `main` makes it an error. That one is being fixed by hand in the
same branch as this capture; the class is not.

The check is also drawing a conclusion the clone cannot support, which is the
deeper defect. `docket check` **already** declines to verify *recorded* pull
requests on a shallow clone, and says so: "the checkout is a shallow clone, so
the commits it is missing are the oldest ones and the longest-settled
provenance would read as broken". The *missing*-`pr` check faces the same
limitation and escalates to a hard error instead. Same clone, same
unanswerable question, opposite treatment - and the inconsistency is what
turned `main` red.

**Where.** `.github/workflows/quality.yml` (the `checks` job's
`actions/checkout`, and the new `floor` job's), and whichever check in
`subprojects/docket/src/docket/checks.py` raises the missing-`pr` error.

**Done when.** A closure that lands with an empty `pr:` cannot turn `main` red,
and the fix is not "always remember the follow-up".

**Options.** Two, and they are complementary rather than exclusive.

1. **Give CI enough history to answer** - `fetch-depth: 0`, or a bounded depth
   like 50, on `actions/checkout`. One line, and it also makes the two other
   things CI currently reports as "not checked" answerable: recorded pull
   requests, and release tags. Costs clone time on every run.
2. **Make the missing-`pr` check fail safe when it cannot see** - report
   "cannot answer" rather than "the store is wrong" when the base history is
   too shallow to hold the merge commit, matching what the recorded-`pr` check
   already does. This is the one that removes the false failure at the source;
   option 1 only moves the horizon.

Recommend both: 2 because a check that reports a wrong verdict is worse than
one that reports nothing, and 1 because the extra history buys back two checks
CI is currently skipping.
