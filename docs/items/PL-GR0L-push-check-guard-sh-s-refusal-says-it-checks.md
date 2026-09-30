---
id: PL-GR0L
title: push-check-guard.sh's refusal says it checks the tree the push sends, but it reads the working tree, so uncommitted work that makes an open item's verify: pass refuses a push whose commits would pass (seen 2026-09-30 on PL-Z85N's brief-only push)
status: untriaged
added: 2026-09-30
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
