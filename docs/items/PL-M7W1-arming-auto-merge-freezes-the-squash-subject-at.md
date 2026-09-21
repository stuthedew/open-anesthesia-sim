---
id: PL-M7W1
title: "Arming auto-merge freezes the squash subject at that moment, so a later rename to satisfy pr-title never reaches origin/main: the gate goes green on a title that will not land"
status: untriaged
touches: tools/pr_title_check.py, .github/workflows/pr-title.yml, docs/worker.md
added: 2026-09-21
payoff: the pr-title gate stops reporting green on a subject that will never reach main, so the provenance it exists to protect is actually protected rather than left to the fallback
---

**Problem.** `tools/pr_title_check.py` reads the pull request's **live** title.
GitHub's auto-merge captures the squash commit message **when auto-merge is
armed**. When those two moments differ, the check validates a string that never
lands, and `origin/main` gets the stale one with nothing reporting it.

## Observed on #868, 2026-09-21, with the timeline

| Time | Event |
| --- | --- |
| 19:29 | #868 opened, title leads `PL-V065` |
| 20:10:34 | auto-merge armed (squash) - **subject captured here** |
| 20:15 | `PL-615L` closed on the branch; title edited |
| 20:15:59, 20:16:33 | `pr-title` **fails**: branch closes `PL-615L`, title does not lead with it |
| 20:17:48 | title renamed to `PL-V065, PL-615L: ...` |
| 20:18:05 | `pr-title` **passes** on the new title |
| 20:18:57 | merged as `158ca0e5` |

The subject on `origin/main` is neither renamed version. It is the **19:29
original**:

```text
PL-V065: record why v0.5.1 shipped as cut, and the four pull request numbers the merges left (#868)
```

So `pr-title` went green on a title that did not reach `main`, and the two
renames - made *because the check asked for them* - were discarded.

## Why this is the shape the check exists to prevent

`tools/pr_title_check.py`'s own docstring states the guarantee: a squash
subject is what `docket check` reads to recover which pull request closed an
item, and "a title that names no id is not a style lapse - it destroys
provenance that cannot be reconstructed from anywhere else." The docstring
already anticipates *one* leak - "a merger retypes the subject in the squash
dialog, which GitHub allows and this cannot see." **Auto-merge is a second,
and it is worse**, because it needs no retyping: arming it early is the normal
way to use it, and nothing in the flow signals that the title is now frozen.

It is a silent wrong answer rather than a miss: the gate reports success, and
the guarantee behind it is void.

## What it cost here, and why that is not reassurance

**Nothing, this time.** `docket check` reports `PL-615L: ... #868 is
recoverable from its merge commit`, because `PL-2XTF`'s other half falls back
to the item's own file history. That fallback is exactly why the damage was
bounded - and it is also why this could recur unnoticed for a long time, since
the visible symptom is absent whenever the fallback succeeds.

## Directions, not a decision

Three, cheapest first, and the choice wants measuring rather than arguing:

1. **Re-run `pr-title` on `auto_merge_enabled`** and fail when the armed
   subject does not lead with the ids. Cheap, but the arm-time message is not
   obviously readable from the event payload - check before committing to it.
2. **State it in `docs/worker.md`**: arm auto-merge only once the title is
   final, and re-arm after any rename. Zero machinery, relies on a session
   reading it at the right moment - which is the disposition test
   `CLAUDE.md` § "Route it" applies.
3. **Leave it to the fallback and retire the gate's stronger claim**, editing
   the docstring so it does not promise what it cannot deliver. Legitimate
   under `CLAUDE.md`'s "a check earns its place every run" - but `PL-2XTF`
   wanted both halves deliberately, so this reopens that.

**Done when.** A session that arms auto-merge and later renames a pull request
either cannot land a stale subject, or is told at the moment it matters that it
will - and whichever is chosen, `pr_title_check.py`'s docstring describes the
guarantee it actually provides.
