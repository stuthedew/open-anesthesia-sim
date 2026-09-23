---
id: PL-YZJD
title: falsifies: can only ever fold for an item whose declaration reached the base before the working session started, so an untriaged item triaged and worked in one session structurally cannot use it - which is most of why it stands at 0 of 1,324
priority: P2
effort: S
status: done
classes: defect, docs
feature: verify-false-reject
milestone: v0.5.4
touches: .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/triage.md, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-2JRC's triage pass
added: 2026-09-21
closed: 2026-09-22
pr: 890
verify: grep -q 'def test_a_branch_declaration_names_the_window_it_missed' subprojects/docket/tests/test_verify.py && grep -q 'why triage is the only pass that can write it' .claude/skills/docket/modes/triage.md
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

**Decision needed.** Which of the two endings in **Done when.** above: state the
precondition in the close-out mode, or change the check to read the declaration
from the item's state before this branch's first commit.

**Recommended: state the precondition**, in the same sentence that prescribes
writing `falsifies:` at triage, so a session meets the limit at the moment it
would otherwise try. It costs nothing, removes the trap immediately, and leaves
intact the property that makes the field worth anything - that a reviewer wrote
it first. Moving the read to the branch point is the larger change and weakens
exactly that property: a session could then triage its own item and declare
what its own work falsifies, which is the self-certification reading the base
was chosen to prevent. Take it only if a count shows the triage-then-work path
is where `falsifies:` would actually earn its keep, and no such count has been
run - which at 0 of 1,324 is not evidence either way.

**Not a claim that the check is wrong.** Reading the base is what makes the
field worth anything - "the whole worth of the field is that a reviewer wrote it
first". The finding is that the prescription beside it names a case the
prescribed workflow cannot reach.

**Decision of record (session, 2026-09-22): the first ending, routed.** State
the precondition — and state it at all three moments a session could meet it,
rather than only in the close-out mode. The check is unchanged: reading the
base's copy is the property the field exists for, and moving the read to the
branch point would let a session triage its own item and declare what its own
work falsifies, which is the self-certification the base was chosen to prevent.

**What the two options between them missed.** `falsifies` appeared in exactly
one file under `.claude/` — `close-out.md` — and nowhere in `triage.md`. So the
instruction "write it at triage" was addressed to a triage pass and stored in a
file only a close-out session reads, at the one moment it is certainly too late.
That is a routing failure in `CLAUDE.md`'s own terms ("ask at what moment a
session needs the rule"), and it explains the 0-of-1,503 more completely than
the precondition does: no triage pass has ever been told the field exists.

**The premise in "Why it matters." above is measurably too strong.** The
triage-then-work-in-one-session path is not the ordinary path. Measured
2026-09-22 over 80 recent `done` items, 53 had their file on the base before
the commit that closed them and 27 were created and closed in one commit — a
third, not the norm. `bin/docket next` ranks on band, so an untriaged item is
outside the ranking altogether and the prescribed pickup path is an item some
earlier, merged pass triaged. The precondition is therefore satisfiable for
roughly two thirds of items; it was simply never delivered to anyone who could
satisfy it.

**And the reachable population is small enough that it settles option 2 on the
numbers, not only on the principle.** Of 502 single-id close-outs, 57 would
refuse the check and 20 are the changed-output-string shape; the brief quotes
the string in 3 of the 20; about two thirds of those sit inside the window.
That is roughly **2 folds in 502 close-outs**, and what a miss costs is an
advisory `REJECT` reported instead of folded — never a wrong gate result. A
change to the integrity semantics of `docket verify` cannot be bought for that.

**Still open to the project owner**, if they want it: the second ending
(`verify.py` reading the declaration from the item's state before the branch's
first commit). It is recorded here as declined on the reasoning above rather
than as unavailable.

**Landed.**

- `.claude/skills/docket/modes/triage.md` — new section "`falsifies:`, and why
  triage is the only pass that can write it", opening with the skip condition
  so an ordinary item pays nothing for it, and closing with the rarity so no
  later session re-opens this expecting a win.
- `.claude/skills/docket/modes/close-out.md` — the prescription now states the
  precondition and points at the triage mode; the stale `0 of 1,324` is recounted
  to `0 of 1,503` and dated.
- `subprojects/docket/src/docket/verify.py` — the branch-declared advisory gains
  the actionable half: the line had to reach the base before this branch's first
  commit, so triage is the only pass that can write it. Previously the message
  named the rule and left the reader with no move, which reads as a step this
  session skipped when there was none to take.
