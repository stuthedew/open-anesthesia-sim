---
id: PL-GR0L
title: push-check-guard.sh's refusal says it checks the tree the push sends, but it reads the working tree, so uncommitted work that makes an open item's verify: pass refuses a push whose commits would pass (seen 2026-09-30 on PL-Z85N's brief-only push)
priority: P2
effort: S
status: done
classes: defect
feature: fewer-red-runs
milestone: v0.5.19
touches: .claude/hooks/push-check-guard.sh, tests/unit/test_push_check_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-30
closed: 2026-09-30
pr: 1237
payoff: a refused push says which tree its checks read, so a session whose own uncommitted edit tripped a check stashes or commits it rather than hunting the commits for a fault they do not carry
verify: grep -q 'def test_a_refusal_names_uncommitted_work_the_checks_read' tests/unit/test_push_check_guard.py
---

**Problem.** push-check-guard.sh's refusal says it checks the tree the push sends, but it reads the working tree, so uncommitted work that makes an open item's verify: pass refuses a push whose commits would pass (seen 2026-09-30 on PL-Z85N's brief-only push)

**Observed.** On `claude/adoring-cray-zuvz88`, the push of commit `06acdfa5`
(only PL-Z85N's rewritten brief) was refused with "This push is refused until
the tree it sends passes the checks CI runs", citing `PL-Z85N is open but its
verify: command already passes`. The test that made the `verify:` pass was an
uncommitted edit in the working tree; in the commit being pushed the `grep`
failed, as it should for an open item. The branch had no pull request, so
`git push --no-verify` was the sanctioned way through.

**The design is deliberate, the wording is not.** The hook's header says,
under "Which tree", that "the checks read the working tree, so an uncommitted
edit counts" - the right call for `git commit ... && git push`, where the hook
runs before the commit. Its "Known gaps" promise only "never a false refusal
of a clean tree", which held: this tree was not clean. What is wrong is the
refusal text: it names the tree the push sends, which is not the tree it
read, so a session told its push is broken goes looking in the commits.
Saying it read the working tree, uncommitted edits included, and that
committing or stashing them settles which one is meant, would make the
refusal true. Where a pull request is open there is no `--no-verify` escape,
so the cost there is a commit or stash the message does not suggest.

**Why it matters.** The refusal is an answer a session acts on, and
`.claude/rules/apparatus-standard.md`'s floor asks that it be true; this one
names a tree it did not read. Its instruction - "Fix what it names, commit,
and push again" - then points the wrong way: what it named was true of the
working tree only, so following it sends a session into commits that carry no
fault. With a pull request open there is no `--no-verify`, and the one step
that clears it, a stash, is nowhere in the message.

**Reproduced 2026-09-30** against `c9ae80e7`: a scratch repository whose
committed `tools/doc_check.py` exits 0, with one uncommitted edit making it
exit 1, is refused with "This push is refused until the tree it sends passes
the checks CI runs on every pull request", the `doc_check` report, and "Fix
what it names, commit, and push again" - no word of the working tree or of the
uncommitted edit.

**Done when.** The refusal names what it read - this checkout, not the tree
the push sends - and where `doc_check` or `docket check` failed in a tree
`git status --short` shows changes in, it says so, counts the paths, and says
that committing them (the refusal then stands) or stashing them and pushing
again (the checks then read only what is sent) settles which tree was meant.
It adds nothing from a clean tree, nor where only `branch_id_check` failed,
since that one reads the history and uncommitted work cannot be its cause.
`tests/unit/test_push_check_guard.py` pins all three cases.

**Generator check.** A one-off. The fact misread is which tree the push
guard's checks read - the working tree, uncommitted edits included - and the
hook's own header states it; only its refusal text said otherwise. No head's
`misread:` states it: `PL-XBV4`'s is how fresh the state a read command
answered from is, a moment rather than which content. Nor is it a re-entry:
`PL-PLSJ` and `PL-S1BG`, the hook's two items closed 2026-09-27, chose the
working-tree read on purpose - `PL-PLSJ`'s **Done when.** opens "A PreToolUse
hook denies a `git push` whose working tree fails" - and neither was about the
wording.
