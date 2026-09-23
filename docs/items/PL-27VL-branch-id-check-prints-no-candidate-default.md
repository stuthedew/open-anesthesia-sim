---
id: PL-27VL
title: branch_id_check prints 'no candidate default branch resolved' where one did resolve, past a preferred candidate git did not answer: since PL-1PBV its runner passes that silence to default_base, which now marks the base guessed, and the reason string names only the case where every probe failed
priority: P3
effort: S
status: ready
classes: defect
feature: evidence-declines
touches: tools/branch_id_check.py, tests/unit/test_branch_id_check.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
payoff: a branch-id or verify decline names what actually went wrong with the base, so the reader tries the remedy that fits
verify: grep -q 'def test_a_base_resolved_past_an_unanswered_candidate_says_so' tests/unit/test_branch_id_check.py && grep -q 'def test_verify_refusal_says_a_base_resolved_past_an_unanswered_candidate' subprojects/docket/tests/test_cli.py
---

**Problem.** branch_id_check prints 'no candidate default branch resolved' where one did resolve, past a preferred candidate git did not answer: since PL-1PBV its runner passes that silence to default_base, which now marks the base guessed, and the reason string names only the case where every probe failed

**Found closing `PL-1PBV`, 2026-09-23.** `branch_id_check._git` now returns
`SILENT` for a git call with no answer, where it used to return `""`. So
`default_base` can see that `origin/main` went unanswered, and it marks a later
candidate that resolved, say the local `main`, as `GuessedBase("main")`. `main()`
then declines, which is the right verdict: before, that ref was walked as if it
were the base. But the printed reason is `no candidate default branch resolved
here`, and here one did resolve.

**Reach is close to nil.** It takes `rev-parse --verify --quiet origin/main`
failing with something other than exit 1 while a later probe succeeds. That
means a 30 s timeout or a damaged ref store. Every realistic failure, such as no
repository or no git, fails all four probes alike, and then the message is
true. The verdict is "not checked" in both cases, and the remedy it prints
(`git fetch origin`, or `--base`) works for both. Only the stated reason is
wrong.

**The cheap fix, if it is ever worth taking.** `default_base` returns the
`GUESSED_BASE` singleton when nothing resolved, and a new `GuessedBase(name)`
when a name resolved past a silence. So `base is GUESSED_BASE` tells the two
apart. Keep the existing wording for the first case, because
`test_a_checkout_with_no_default_branch_says_so_rather_than_passing` pins it,
and add a sentence for the second.

**Reproduced at triage, 2026-09-23**, with a runner that leaves `origin/main`
unanswered and answers the rest: `default_base` returned
`GuessedBase('origin/master')` - not resolved, and not the `GUESSED_BASE`
singleton - so `main()` prints "no candidate default branch resolved" about a
checkout where one did.

**The same wording stands at a second site.** `cli._guessed_base_refusal`, which
`bin/docket verify` prints, says "no candidate default branch resolved in this
checkout" while its own docstring names the resolved-past-a-silence case as the
first it covers. So the fix is one wording decision applied at both, and
`touches` carries both. `vcs._Silences.reason` says "could be established",
which is true in both cases, and is left alone.

**Why it matters.** Reach is near nil, as above, but a decline has to say truly
what it could not read, and this sentence names a cause that did not occur at
the moment a reader is choosing which remedy to try.

**Done when.** Both messages distinguish nothing resolving from a candidate
resolving past an unanswered preferred one, keeping the existing wording for the
first case, with a test for the second at each site.

**Generator check.** One-off. `GuessedBase` has carried two cases since
`PL-73P0`, and each message was written when only the first could reach it;
`PL-1PBV` made the second reachable at this runner. The two sites are one fix,
not two items.
