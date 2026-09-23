---
id: PL-27VL
title: branch_id_check prints 'no candidate default branch resolved' where one did resolve, past a preferred candidate git did not answer: since PL-1PBV its runner passes that silence to default_base, which now marks the base guessed, and the reason string names only the case where every probe failed
status: untriaged
feature: evidence-declines
added: 2026-09-23
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
