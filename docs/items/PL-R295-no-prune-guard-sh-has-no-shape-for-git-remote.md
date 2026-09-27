---
id: PL-R295
title: no-prune-guard.sh has no shape for git remote remove or git remote rm, which delete every remote-tracking ref of the named remote at once - git remote remove origin leaves no origin/<branch> at all, a stranded item's only copy among them - so the one git spelling that deletes more refs than a prune runs unrefused
priority: P2
effort: S
status: done
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/no-prune-guard.sh, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1142
payoff: a session's git remote remove or rm is refused before it deletes every remote-tracking ref of that remote, a stranded item's only copy among them
verify: grep -q 'def test_removing_a_remote_is_refused' tests/unit/test_no_prune_guard.py
---

**Problem.** no-prune-guard.sh has no shape for git remote remove or git remote rm, which delete every remote-tracking ref of the named remote at once - git remote remove origin leaves no origin/\<branch> at all, a stranded item's only copy among them - so the one git spelling that deletes more refs than a prune runs unrefused

**Filed by `PL-61FT`'s design round (`#1128`)**, after a scratch remote lost
every remote-tracking ref to `git remote remove`. The round put it inside the
prune guard's promise - every spelling git 2.43's own usage documents that
deletes refs without naming them one by one - and left it to be worked at its
own rank.

**Reproduced at triage, 2026-09-26.** On git 2.43.0, in a scratch clone of a
bare remote holding `main` and `other`, with `other` then deleted on the remote
so that the clone's `origin/other` held the only copy of its commit: `git remote
remove origin`, `git remote rm origin`, `git remote -v remove origin`, `git
remote --verbose rm origin` and `git remote remove -- origin` each exited 0 and
left no ref under `refs/remotes/`, `origin/other` among them. A bare `git remote
remove` exited 129 with its usage and deleted nothing. Beside them, `git remote
rename origin kept` moved all three refs under `refs/remotes/kept/` and deleted
none, and `git remote set-head origin -d` deleted only the symbolic
`origin/HEAD`, which holds no commit of its own. `git remote -h` documents
`remove` alone; git v2.43.0's `Documentation/git-remote.txt` documents `rm`
beside it: "'remove':: 'rm':: Remove the remote named <name>. All
remote-tracking branches and configuration settings for the remote are
removed." Piped as hook payloads on `origin/main` (`d8550400`), `git remote
remove origin` and `git remote rm origin` pass unrefused, and `git remote prune
origin` is refused.

**Why it matters.** It is the widest deletion inside the prune guard's promise.
A prune deletes the refs whose branches are gone from the remote; this deletes
every ref the remote has, so `git remote remove origin` takes each stale
`origin/<branch>` that is the only copy of an item captured on a branch nobody
merged, which `bin/docket stranded` exists to recover and then cannot. Found by
the design round's own measurement rather than met in ordinary work, and owed
all the same, since its outcome cannot be undone.

**Done when.** `git remote remove` and `git remote rm`, wherever the guard
reads a git call, are refused with a reason that answers what the caller wanted
- `git remote set-url` to point a remote elsewhere, a ref deleted by name -
pinned in `tests/unit/test_no_prune_guard.py`, and the guard's header states
the spelling as read rather than as owed.

**Generator check.** A member of `PL-61FT` (what a shell command does when run,
which the guards read from its spelling): filed by that head's design round
before its build closed it, so not an instance after the close, and inside the
promise the round drew, so it is worked at its own rank rather than recorded as
a `KNOWN_GAPS` row. No other head's `misread:` states the fact.

**Fixed 2026-09-26.** `REMOVE_SHAPES` in the hook reads `remote remove` and
`remote rm` as `remote prune` is read - the two words in order, in every git
call the guard finds - and refuses either with a reason of its own:
`bin/docket stranded` first, `git remote set-url <name> <url>` to point the
remote elsewhere and keep its refs, and a ref deleted by name. The prune
reason's recipe restarts a merged branch and the push reason's pushes by name,
and neither answers a session removing a remote. `runs` takes no setting
pattern for it, since no setting removes a remote. The header's promise names
the spelling as read, and a paragraph beside the push one records the
measurement and the two neighbours left alone: `remote rename`, which moves the
refs, and `remote set-head -d`, which deletes only the symbolic `<name>/HEAD`.

Pinned in `tests/unit/test_no_prune_guard.py`: eight refused spellings, the
five measured and three command shapes (`test_removing_a_remote_is_refused`);
eight admitted remote calls, the recipe and writing about the spelling among
them, each git call measured on the same scratch clone
(`test_a_remote_call_that_keeps_the_refs_is_untouched`); and the recipe
(`test_the_remove_refusal_answers_the_question_the_caller_had`). Like `remote
prune`, the shape asks only for the words in order, so a remote named `rm` or
`remove` would be refused too. That is a false refusal nobody has met, and
`PL-61FT` works those when met and never probes for them, so it is neither a
row nor an item.
