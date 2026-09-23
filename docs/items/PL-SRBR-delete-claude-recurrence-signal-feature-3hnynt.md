---
id: PL-SRBR
title: Delete claude/recurrence-signal-feature-3hnynt once #794 is confirmed to hold the change in 52c6d698, the commit tools/left_behind_check.py reports as left behind by #793
priority: P2
effort: S
status: ready
classes: housekeeping
feature: parallel-sessions
touches: docs/items
added: 2026-09-23
payoff: the session-start digest's left-behind line goes quiet, so the next line it prints is a new finding and not one every session has learned to skip
verify: test "$(git ls-remote origin refs/heads/main refs/heads/claude/recurrence-signal-feature-3hnynt | wc -l)" -eq 1
not-delegable: The work is deleting a remote branch, and no session here can do that: the push is refused with HTTP 403 (docs/worker.md § "Ref operations a session cannot perform", PL-ZM48). The project owner runs the command in the brief, and a session then closes the item.
---

**Problem.** Delete claude/recurrence-signal-feature-3hnynt once #794 is confirmed to hold the change in 52c6d698, the commit tools/left_behind_check.py reports as left behind by #793

**Reproduced 2026-09-23, and the condition is met.** `python3
tools/left_behind_check.py --all` still names the branch. It carries `52c6d698b
PL-DGP0: derive the recurrence threshold from the generator floor, and raise
the similarity floor to 0.15`, pushed after `#793` merged at `46620e20`, and
`vcs.orphaned does not report it`. `#794` (`9fe0ee33`, on `origin/main`)
changes all eleven files `52c6d698` changes, and the added and removed lines
agree exactly. That is 162 lines across the eight `subprojects/docket/` source,
test and README files, 23 in `docs/WORKING_NOTES.md`, 86 in the new `PL-DGP0`
item file and 10 in `PL-X5JR`'s. `#794` has one line more, `pr: 793` in
`PL-X5JR`'s front matter. `origin/main` still holds both constants,
`DISPLAY_FLOOR = 0.15` in `duplicates.py` and `MIN_RECURRENCES =
MIN_ROOT_CAUSE_ITEMS - 1` in `model.py`. So the branch carries nothing the base
lacks. `PL-R808` found that the commit "does not cherry-pick cleanly onto
today's `main`". That is later work editing the same files, not anything
missing.

**The step left is the deletion, and it is the project owner's.** A session
cannot delete a remote branch here. The push is refused with HTTP 403
(`docs/worker.md` § "Ref operations a session cannot perform", `PL-ZM48`). The
command, and the read that confirms it worked. Read the output, not the exit
status: `ls-remote` exits 0 either way.

```text
git push origin --delete claude/recurrence-signal-feature-3hnynt
git ls-remote --heads origin claude/recurrence-signal-feature-3hnynt
```

The second command prints nothing once the branch is gone. A session then
closes this item.

**Generator check.** Bookkeeping. This is `PL-R808`'s first live finding,
filed in the commit that closed it. The commit was pushed on 2026-09-20, before
that head closed, so it is not a post-close instance. Its mechanism is
`PL-3D2M`'s: a commit pushed after its pull request merged lands nowhere.
Reporting that is what `tools/left_behind_check.py` exists to do.
