---
id: PL-7790
title: A session that starts an item by pushing only queue-file edits stakes no claim docket next can see
priority: P3
effort: M
status: needs-decision
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, .claude/skills/docket/SKILL.md
added: 2026-09-05
---

**Problem.** `PL-X3WZ` made the in-flight mark read a commit's diff as well as
its subject: a commit whose whole diff sits inside `docs/items/` stakes no
claim, because captures, triage passes, `docket record` writes and notes
written into a brief all lead with an id they are not implementing. The
residual is the opposite case - a session that genuinely *starts* an item by
pushing only a `touches` fill or a `verify:` command, which is annotation by
the diff and a claim in fact.

**Observed 2026-09-05, live, in the session that made the change.**
`origin/claude/docket-project-check-optimization-da5xn8` carried one pushed
commit, "PL-P3B6, PL-K1DL: file the verify-replay cost, and the rejected path
split", changing two item files and nothing else. The session was implementing
`PL-P3B6` at that moment; its implementation was unpushed. Before the change
that branch marked both ids, and only one of them was real - which is the
defect `PL-X3WZ` fixed - but the mark it lost on `PL-P3B6` was a true signal.

**Why it matters.** It is the direction that costs more of the two: an item
wrongly left marked is one a session picks around, while an item wrongly
unmarked is two sessions on one piece of work (`PL-PRHN`).

**What already bounds it, and why this is not urgent.** Three things, and the
change was taken knowing them:

- A branch named `claude/pl-p3b6-short-slug` carries the claim in its own name,
  which is read whatever the diff says. `.claude/skills/docket/SKILL.md` now
  says so where it asks for the first push.
- `list_sessions` sees a session that has committed nothing at all, which is
  functionally this case, and the skill's start procedure already reads it.
- The mark returns on the first commit outside the queue, which is usually
  minutes away.

**Two refinements were tested against `PL-X3WZ`'s eight false marks and
rejected.** "Changes only the item file whose id leads the subject" misreads
both a single-file capture and a `docket record` write; "creates a new item
file" misreads the `docket record` write *and* would not have recovered
`PL-P3B6`, whose capture commit created both files. Anything that recovers this
case has to read something other than the paths.

**Where.** `subprojects/docket/src/docket/vcs.py` - `_annotates_only` and the
walk that calls it; `.claude/skills/docket/SKILL.md` if the guidance changes.

**Done when.** Either a reading exists that separates "filed this item" from
"started this item" without reintroducing the false marks, or the case is
measured over enough sessions to say the branch-name and `list_sessions` cover
is sufficient and this is closed as accepted.

**Decision needed.** Whether to keep looking for a reading that separates
"filed this item" from "started this item", or to accept the branch-name and
`list_sessions` cover and close this as understood. Both refinements tried
against `PL-X3WZ`'s eight false marks reintroduced them, so anything that
recovers this case has to read something other than the paths - which is the
work, and is why the question is worth answering before it is started rather
than during.
