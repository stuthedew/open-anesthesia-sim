---
id: PL-YZJD
title: falsifies: can only ever fold for an item whose declaration reached the base before the working session started, so an untriaged item triaged and worked in one session structurally cannot use it - which is most of why it stands at 0 of 1,324
status: untriaged
touches: .claude/skills/docket/modes/close-out.md, subprojects/docket/src/docket/verify.py
added: 2026-09-21
---

**Problem.** `.claude/skills/docket/modes/close-out.md` records that `falsifies:`
stands at **0 of 1,324** items - written once into the tool in `v0.4.27` and
never onto an item - and prescribes the case that should work: "write it at
triage only in the case that actually works: the item's own brief already
quotes the old string". But the same file also states that "a session cannot
declare one for itself mid-work", because the check reads **the base's copy of
the item**, not the branch's.

Those two rules compose into a precondition the prescription does not state: the
declaration has to have *merged to the default branch* before the working
session starts. An item that is `untriaged` when a session picks it up, is
triaged by that session, and is worked in the same session can never satisfy it -
the `falsifies:` line exists only on the branch, so it folds nothing and is
reported as the session's own word for it.

**Why it matters.** That is the ordinary path rather than an edge case. The
project files captures `untriaged` by design (`bin/docket new` allocates no
band), and a session that picks one up triages it as work begins - the `docket`
skill's start mode says so explicitly: "Set the item's `status` and `feature` as
work begins". So the one mechanism that could fold the settled `REJECT` is
unreachable on the path the skill prescribes, and a session meeting that
`REJECT` is told to write `falsifies:` at triage without being told that its own
triage is too late to count.

Observed 2026-09-21 on `PL-DPY6`, whose *title* quoted the old string
(`root-cause-of: PL-AAAA, PL-BBBB, PL-CCCC`) - the exact precondition
`PL-FCM3` is cited for. It was `untriaged` at pickup, so the declaration could
only ever have been made on the branch, and the close-out reported the expected
`REJECT` with four candidate lines.

And a `REJECT` a correct close-out reaches every time is the
shape `CLAUDE.md` calls a defect in the check: it costs attention forever and
trains a session to skim the block where a real protected-path failure is
printed. The close-out mode already anticipates that and asks for the `REJECT`
to be reported rather than cleared, which is right - but it offers a way out
that, on the ordinary path, does not exist.

**Done when.** Either the close-out mode says plainly that a `falsifies:`
declaration counts only when the base already carries it, so a session that
triages its own item knows not to try; or the check reads the declaration from
the item's state *before this branch's first commit* rather than from the base,
which would let a triage-then-work session declare it honestly at the moment it
still could. The second is the larger change and is a decision rather than a
fix.

**Not a claim that the check is wrong.** Reading the base is what makes the
field worth anything - "the whole worth of the field is that a reviewer wrote it
first". The finding is that the prescription beside it names a case the
prescribed workflow cannot reach.
