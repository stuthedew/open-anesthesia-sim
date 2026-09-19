---
id: PL-C4RS
title: Gate 1's group headings and v0.5.0's Required scope disagree on three ids, and ROADMAP.md states Required scope as the test
priority: P3
effort: S
status: done
classes: docs, defect
feature: planning-cadence
touches: ROADMAP.md, tools/doc_check.py
added: 2026-09-14
closed: 2026-09-19
verify: python3 tools/doc_check.py check && grep -qF 'the three ids below now sit under headings that agree with `Required scope`' ROADMAP.md
---

**Problem.** Gate 1's group headings and v0.5.0's Required scope disagree on three ids, and ROADMAP.md states Required scope as the test

**Found while building `PL-WZBX`** (the gate counted milestone work as
clearable before the milestone), whose first step was to check v0.5.0's
`Required scope` against the entries Gate 1 writes under "Cleared by v0.5.0
itself" before resting the implementation on that test. Seven of the eight are
in it. Three *other* ids are in it too, under headings saying the opposite:

- `PL-2FM6` and `PL-8LXM` — under "Cleared by the `v0.4.x` track, ahead of this
  gate — 7 entries".
- `PL-GVXP` — under "Cleared before v0.5.0 begins, the product lane — 39
  entries".

**Why it matters, and why it is not urgent.** `ROADMAP.md` § "Debt inside the
milestone's own scope" states one test — "whether the item appears in the
milestone's `Required scope`" — and then says an item passing it "is listed in
the frozen gate under a heading that says so". Three are not. All three have
closed, so nothing rode on it while `PL-WZBX` was built and the gate reads the
same either way today; it matters the next time a gate is frozen, because a
reader taking the headings as the record and a session taking the rule get
different answers about who clears an entry.

**Where.** `ROADMAP.md` § "v0.5.0 - the case you can branch" → "Debt gate: the
frozen list", the three group headings above; or v0.5.0's `Required scope`, if
the three were named there by mistake rather than misfiled below. Which side is
wrong is a judgment on the prose rather than a parse, which is why `PL-WZBX`
did not settle it in passing: it reads the rule, not the headings
(`subprojects/docket/src/docket/roadmap.py`, `gate_status`).

**Done when.** Each of the three either moves under a heading matching what
`Required scope` says of it, or leaves `Required scope`, with the correction
dated in the section the way that list records its other post-freeze notes.

**Why it matters.** `ROADMAP.md` states `Required scope` as the test for what a
milestone contains, so a group heading that counts differently is a second
answer to a question the document says has one. `bin/docket wave` reads the two
structures and reports whichever it reads, which is how a disagreement becomes a
wrong number in every session's digest rather than an inconsistency in a
document nobody opens.

**The disagreement has to be re-measured before it is fixed.** The roadmap moved
on 2026-09-14 - Gate 1 cleared, `v0.4.25` was inserted ahead of v0.5.0, and
`PL-RKWB` renumbered the port - so the three ids this item named at capture are
not necessarily the three that disagree today. What is measurable now:
`ROADMAP.md`'s `### Required scope` opens "Nineteen items, in the order the
dependencies allow" while `bin/docket wave` reports `Scope ... (25 ids), 17
closed, 8 open`. `PL-4PC5` is the same gap seen from the tool's side - that
`wave` counts ids cited in the section's prose as scope entries - and it is in
flight on `origin/claude/bold-mayer-ij89qm` as of 2026-09-14, so the two answers
have to agree with each other. Whichever lands second reads the other first.

**Done when.** The `Required scope` section's stated count, the group headings
under `### Debt gate: the frozen list`, and what `bin/docket wave` reports all
name the same set, with the ids that differ listed and each one's placement
stated rather than implied.

---

**`verify:` rewritten 2026-09-16, and the item's judgment is untouched.** The old
command was `! grep -q 'Nineteen items, in the order the dependencies allow'` - an
*absence*, satisfiable by anyone who edits that heading. Someone did: the phrase
was present in `ROADMAP.md` at `d7a3b05` and gone by `4690412`, so the command
began passing on a tree carrying none of this item's work and `bin/docket check
--verify` errored on `main`. This is the second instance of that shape in one
sweep; `PL-D1RT` was the first, and `PL-KND7` carries both.

Taken on the error's *second* disposition rather than its first, because the work
genuinely is outstanding: the `Done when.` above still asks for three ids to be
reconciled against `Required scope`, and this brief already records that which
side is wrong is a judgment on the prose. Closing it would have decided that
question by accident.

The replacement pins the **presence** of a sentence the correction must add,
which makes it a specification rather than a bet: it exits 1 today on the `grep`
half with `doc_check` passing, and can only pass once the reconciliation is
written. Whoever does the work writes that sentence into the gate section
alongside the dated correction the `Done when.` requires.

---

**Re-measured 2026-09-19, and one of the three is resolved.** `PL-HWW1` made
`Required scope` membership a declaration - the `(queue item ...)` slot rather
than every id under the heading - and `PL-GVXP` was never an entry there. It is
cited inside the `PL-8PSW` entry's prose, which is what put it in `Required
scope` at all, so it is no longer named on both sides: it sits under "Cleared
before v0.5.0 begins, the product lane - 39 entries" and nowhere else. That
half is closed by the parse rather than by an edit, which is the outcome this
item asked for when it said the two answers have to agree with each other.

**What is left is the other two, unchanged.** `PL-2FM6` and `PL-8LXM` are
*declared* entries 3 and 4 of v0.5.0's `Required scope` - so the narrowing did
not touch them - while Gate 1's frozen list carries them under "Cleared by the
\`v0.4.x\` track, ahead of this gate - 7 entries". Both structures are read
by their own grammar and both now say what they mean, which is exactly what
makes the disagreement real rather than a parse artefact: the section says the
milestone requires this work and the gate heading says another track already
cleared it.

**And the entry itself agrees with the gate heading, in prose.** Entry 4 reads
"(queue item PL-8LXM, moved with \`PL-2FM6\` into the \`v0.4.x\` track on
2026-09-08 and shipped there)". So the `Done when.` above is now a narrow
editorial question with the facts settled: either the two entries stay,
recording what the milestone required and where it was done, and the gate
heading is the one to reword; or the declarations come out and the entries
become prose about work that shipped elsewhere. Which is `ROADMAP.md`'s to
answer, and the reason `PL-HWW1` re-briefed this rather than closing it - a
session that picked one would be deciding what a milestone contains on the
strength of a parser change.

**`verify:` unchanged.** The sentence it pins - "the three ids below now sit
under headings that agree with \`Required scope\`" - is still exactly what the
reconciliation must write, and is still absent.

---

## Done 2026-09-19, and the answer was already in the file

**The question this brief reserved as "a judgment on the prose" was settled on
2026-09-08 by the project owner, in `ROADMAP.md` itself.** The note that moved
`PL-2FM6` and `PL-8LXM` into "Cleared by the `v0.4.x` track, ahead of this
gate" ends: "Required scope below drops to sixteen items. The gate total rises
by two, for `PL-ZX12` and `PL-GS3R`: `PL-2FM6` and `PL-8LXM` moved between
groups rather than joining." So the two were meant to leave `Required scope`
on the day they moved. The entries were never removed, which is the whole
disagreement this item recorded - not two defensible readings, but one
recorded decision and an edit that did not follow it.

**What landed.**

- The two entries left v0.5.0's `Required scope`. What the milestone required
  of them, and that the `v0.4.x` track shipped it, is now a prose note under
  that heading naming both ids **without** a declaration slot, so the record
  survives and places nothing (`PL-HWW1`'s grammar is what makes that
  possible - before it, naming an id was placing it).
- The section's stated size went from "Twenty items" to "Eighteen", and its
  own arithmetic with it ("the first five" to "the first three"). `bin/docket
  wave` reads 18 declared across 18 entries, so the count, the entries and the
  tool now agree.
- `PL-GVXP` needed no edit: it was cited inside the `PL-8PSW` entry's prose
  and left `Required scope` when `PL-HWW1` made a declaration rather than a
  mention the record of membership.
- The dated reconciliation went into the gate's preamble, beside that list's
  other whole-list notes, with each of the three placements stated rather than
  implied.

**§ "Debt inside the milestone's own scope" was left alone, deliberately.** Its
test - an item in `Required scope` is milestone work and is listed under a
heading that says so - is not what broke here. Nothing was in `Required scope`
that should not have been; an edit simply lagged a decision by eleven days.
Widening the rule to admit a third case would have written a carve-out for a
situation that, once the edit is made, does not exist.

**Where the finding went.** That this item was put to the project owner as a
decision at all is `PL-HGN6`: the line between their decisions and a session's
is consequence, not what the answer rests on, and this question's blast radius
was one section's phrasing.
