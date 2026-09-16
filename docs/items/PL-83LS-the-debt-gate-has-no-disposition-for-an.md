---
id: PL-83LS
title: The debt gate has no disposition for an anticipated safety finding whose hazard an unscoped later milestone creates
status: untriaged
added: 2026-09-16
---

**Problem.** Four open `safety`-classed items - `PL-7Z84` (a run has no identity
a workspace can pin to), `PL-9LNF` (three `app/` surfaces own state a layout
could duplicate or relocate), `PL-NWTM` (the unconditional displayed set has no
structural home in the code) and `PL-W54S` (what a broken-out top-level window
owes that set) - describe hazards that **planned-milestone item 34's area system
will create** and that do not exist today. Each is classed `anticipated`. The
debt gate offers three dispositions and none of them fits:

- **Clear it.** Impossible: there is nothing to fix yet. The splitter handles are
  inert (`src/anesthesia_sim/app/qt_widgets.py:784`), so no reader can close,
  replace or cover a required value.
- **Place it in v0.5.0's Required scope.** Wrong: it is not v0.5.0's work. Item
  34 is past v0.5.0 and has no milestone section, so § "Debt inside the
  milestone's own scope" has no scope to put them in.
- **Defer it with a reason.** Forbidden: § "The gate is a snapshot, not a moving
  target" closes by saying `safety` and `science` "are not deferrable by this
  project's own standard".

They are deferred in v0.5.0's `### Declined to Gate 2 ...` subsection today, on
the third option, with the reason written out.

**Why it matters.** This is a gap in the rule rather than a defect in any check.
`tools/doc_check.py`'s safety-class advisory is correct to name them - after
`PL-R0Q0` it names only the two remedies the rule accepts - and it will name
them on every `make check` until the rule says what a finding of this shape is
owed. Left as it is, the advisory is back in the state `PL-R0Q0` fixed, for a
different reason: a real advisory with no clean state a session can reach, which
`CLAUDE.md` calls "a defect in the check - it costs attention forever and trains
a session to skim the output where a real advisory also appears".

Putting them on v0.5.0's frozen list instead is a reachable state and the wrong
one: the gate is open when its entries are clear, and these cannot be cleared
before the milestone that creates the hazard, so the list would block v0.5.0 on
work belonging to a milestone two steps out.

**Why the project owner's.** It amends `ROADMAP.md` § "The debt gate", which is
the authoritative rule every gate is read against, and the choice is a policy one
rather than a reading of the tree. `CLAUDE.md` puts direction on the owner's side
of the division of labour.

**Options, for a decision rather than as a survey.** Recommended first.

1. **An `anticipated` safety finding is not debt until its hazard exists.**
   § "What counts" already draws exactly this line for process work - "Process
   work is debt once the mechanism is live, not before ... The distinction is
   state, not layer" - and this is that same distinction applied to a hazard: an
   unbuilt hazard costs nothing to carry, while a live one charges interest. It
   is decidable in code, because `anticipated` is a declared class that
   `subprojects/docket/src/docket/checks.py` already branches on, so
   `check_gate_reentries` could exclude it without scripting any judgment. Cost:
   a `safety` item wrongly classed `anticipated` becomes invisible to the gate,
   which is the failure `PL-MVC2` records for a misspelt class.
2. **Such a finding is placed on the *next* milestone's frozen list when that
   milestone is scoped**, and carries an explicit marker until then. Honest, but
   nothing holds the marker, and the advisory stays lit in the meantime.
3. **The rule stands and they go on v0.5.0's list.** Rejected above, recorded
   here so the option is visibly considered rather than missing.

**Found 2026-09-16** while fixing `PL-R0Q0`.

**Where.** `ROADMAP.md` § "The debt gate" - "What counts" and "The gate is a
snapshot, not a moving target"; v0.5.0's `### Declined to Gate 2 ...` subsection;
`tools/doc_check.py` `check_gate_reentries` if option 1 is taken.

**Done when.** `ROADMAP.md` says what disposition an `anticipated` `safety` or
`science` finding is owed when its hazard belongs to a milestone that is not yet
scoped; the four items carry it; and `make check` either stops naming them or
names them under a state a session can reach. If option 1 is taken, a test in
`tests/unit/test_doc_check.py` pins that an `anticipated` safety item is quiet
and a plain one is not.

**Related.** `PL-R7XK` corrects `PL-MN4J`'s disposition, which is the *other*
item the same advisory names and is not this shape - v0.5.0 builds the feature
its hazard needs, so Required scope already answers it. `PL-NMTF` (no open item
builds item 34's area system) is the head of the work these four wait on.
