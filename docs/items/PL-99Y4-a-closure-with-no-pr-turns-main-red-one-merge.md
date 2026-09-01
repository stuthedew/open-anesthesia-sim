---
id: PL-99Y4
title: A closure with no pr: turns main red one merge later, because CI's shallow clone cannot recover the number
priority: P2
effort: S
status: done
classes: defect, infra
feature: public-history
milestone: v0.2.8
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_vcs.py, .github/workflows/quality.yml
added: 2026-09-01
closed: 2026-09-01
pr: 169
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_missing_pr_declines_on_a_shallow_clone' subprojects/docket/tests/test_checks.py
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

**Triaged and done 2026-09-01, both options, on the project owner's approval.**
P2, `defect`/`infra`, `public-history` beside `PL-P5S0`, which set the rule
this corrects.

Option 2 is the source fix. `ClosureReport` gains `shallow`, straight from
`is_shallow`, and `_check_closures` errors only where it is `False`. A derived
number stays an advisory at any depth - finding the commit is proof it was
there to find - so truncation qualifies an absence and never a hit. Truncation
or an unanswerable `is_shallow` declines, naming the ids, which is the answer
`PL-J295` already established for `tags` and `merged_pull_requests`.

Option 1 is the other half, and measuring it first changed how much it was
worth: on the full history `bin/docket check` and `tools/doc_check.py` both
lose their "not checked" section entirely. Three checks CI was silently not
running - release tags, recorded pull requests, and now the missing-`pr` read -
go from declined to passing. So it adds coverage rather than risk, and 498
commits is nothing to clone.

**Reproduced before and after, not argued.** A `--depth 1` clone whose HEAD is
`3b37a75` - one of the two commits where `main` actually went red - run under
the code as it stood on `main`: 1 error, exit 1, naming `PL-PF8H`. The same
clone with the two changed modules copied in: 0 errors, exit 0, and

```
Not checked (this checkout cannot answer; nothing is claimed):
  whether PL-PF8H lost provenance by recording no `pr`: the checkout is a
  shallow clone, so the merge commit naming each number can lie outside it
  and its absence proves nothing; a full-history checkout answers
```

**Documentation corrected, not merely swept.** Two statements were falsified by
this change rather than made vague by it: `subprojects/docket/README.md`'s
"this does **not** decline in a shallow clone ... only when no default branch
resolves at all", and its "**No commit names one** -> the error it always was".
`.claude/skills/docket/SKILL.md` carried the second in miniature. All three now
state the three-way split. `README.md` gains what CI's full checkout buys and
why a local shallow checkout reporting those three as not checked is correct.
