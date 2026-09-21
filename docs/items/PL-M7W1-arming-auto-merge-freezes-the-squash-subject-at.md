---
id: PL-M7W1
title: Arming auto-merge freezes the squash subject at that moment, so a later rename to satisfy pr-title never reaches origin/main: the gate goes green on a title that will not land
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: commit-provenance
touches: tools/pr_title_check.py, .github/workflows/pr-title.yml, docs/worker.md
added: 2026-09-21
payoff: the pr-title gate stops reporting green on a subject that will never reach main, so the provenance it exists to protect is actually protected rather than left to the fallback
---

**Problem.** `tools/pr_title_check.py` reads the pull request's **live** title.
GitHub's auto-merge captures the squash commit message **when auto-merge is
armed**. When those two moments differ, the check validates a string that never
lands, and `origin/main` gets the stale one with nothing reporting it.

**Why it matters.** The gate reports success while the guarantee behind it is
void, which is `CLAUDE.md`'s first compounding-friction test rather than an
ordinary miss. `pr_title_check.py` exists because a squash subject is the only
carrier from which `docket check` can recover which pull request closed an
item, so a green check on a title that never lands leaves `origin/main` holding
the stale one with nothing reporting it. It also punishes the correct
behaviour: both renames on #868 were made *because the check asked for them*,
and both were discarded. Arming auto-merge early is the ordinary way to use it,
and nothing in the flow signals that the subject has frozen.

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

## What #880 actually showed: a near miss, and a narrower hazard than this item claimed

**Corrected 2026-09-21 (`PL-G7ST`).** The section that first stood here, landed
on `origin/main` in `32c70c5d`, said #880 was a third instance and that "the
frozen squash subject is the 21:09 original". **That was wrong, and the commit
carrying it disproves it**: the subject on `origin/main` is

```text
PL-2JRC: triage the untriaged captures standing in the queue on 2026-09-21 (#880)
```

which is the *renamed* title. The original said "the 10 untriaged captures". The
claim was written while the pull request was open, from the arm time alone, and
never checked against what landed - in the item whose whole subject is squash
provenance, which is the part worth keeping.

**What happened.** Auto-merge was armed at 21:15:50 on the 21:09 title and the
title was edited at about 21:26, so the precondition this item describes was
fully set up. It never fired: the project owner merged manually at 21:35:55, and
a manual squash merge composes its subject from the **live** title. The stale
subject was never at risk of landing.

**So the hazard is narrower than § "Why it matters." above states, and that is
the finding.** The freeze bites only when auto-merge itself performs the merge.
Where a human merges - the ordinary case on this project, and what happened on
both #868 and #880 - the live title is used and the capture is irrelevant. #868
is still a real instance because the stale subject *did* land there; what #880
adds is the boundary. Any fix taking direction 1 should therefore expect to fire
on pull requests that will mostly be merged by hand, which is an argument about
its cost rather than against it.

**The behavioural point survives the correction**, and is the one that bears on
the decision below. The session that armed and then renamed without re-arming
had written this item's `**Decision needed.**` within the hour, having read
§ "Direction 2's mechanism is now confirmed, on #877" or been about to. So
direction 2 - a `docs/worker.md` sentence whose entire cost falls on a session
remembering at the right moment - was not applied by the reader best placed to
apply it, and that is true whether or not the merge method happened to rescue
the outcome.

**Decision needed.** Which of the three directions above to take, and whether
`pr_title_check.py`'s docstring keeps its stronger claim.

**Recommended: direction 1** - re-run `pr-title` on `auto_merge_enabled` and
fail when the armed subject does not lead with the ids - conditional on the
armed message being readable from the event payload, which is the one thing to
establish before committing to it. It is the only direction that closes the
hole rather than describing it, and it costs one extra workflow trigger. Where
the payload does not carry the armed subject, fall back to direction 2 rather
than direction 3: retiring the claim reopens `PL-2XTF`, which wanted both
halves deliberately.

**Done when.** A session that arms auto-merge and later renames a pull request
either cannot land a stale subject, or is told at the moment it matters that it
will - and whichever is chosen, `pr_title_check.py`'s docstring describes the
guarantee it actually provides.

## Direction 2's mechanism is now confirmed, on #877, 2026-09-21

A second instance hit this within the hour, and it was used to test the
re-arm remedy rather than only to work around it. The freeze reproduced, and
**disabling auto-merge, renaming, then re-arming defeated it**: the corrected
subject is what landed.

| Time (UTC) | Event |
| --- | --- |
| 20:57:46 | #877 opened, title leads `PL-VCJ2` - which this branch does **not** close |
| 20:58:04 | auto-merge armed (squash) - subject captured here, with the wrong id |
| 20:58:00 | `pr-title` **fails**: "this branch closes PL-HWV1, but the title does not lead with PL-HWV1" |
| 21:00:xx | auto-merge **disabled**, then the title renamed to lead with `PL-HWV1` |
| 21:00:44 | `pr-title` re-runs and **passes** |
| 21:00:48 | auto-merge **re-armed** - subject re-captured from the corrected title |
| - | merged as `5b350003` |

The subject on `origin/main` is the corrected one:

```text
PL-HWV1: withdraw the volatile-anaesthetic objection, and correct the false premise it rested on (#877)
```

**What this settles and what it does not.** It settles that re-arming
*re-captures* the subject - the arm event is the capture point, not the first
arm, so direction 2's instruction is mechanically sound rather than merely
plausible, and direction 1 can assume a re-arm produces a fresh payload to
check. It does not settle the disposition: this instance was caught only
because `pr-title` happened to fail for an unrelated reason - the wrong id -
which is what prompted looking at the arm order at all. **A rename that
satisfies the gate without a prior failure still has nothing pointing at the
freeze**, which is the silent case the item is about, and this instance is
therefore not evidence that a reader will notice unaided.

One detail worth keeping for direction 1: the failed and passing `pr-title`
runs both persist on the head commit's check list (20:58:00 failure, 21:00:44
success), so a reader of history sees a red run beside a green one, exactly as
`PL-X1S4` describes for closures pushed under a stale title.
