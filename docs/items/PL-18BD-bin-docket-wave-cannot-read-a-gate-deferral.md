---
id: PL-18BD
title: bin/docket wave cannot read a gate deferral whose holding condition has no id, so PL-B396 and the three entries it blocks, deferred to Gate 3 on 2026-09-27, still count as work Gate 2 can clear and hold the beat at clear the gate
status: untriaged
added: 2026-09-27
---

**Problem.** bin/docket wave cannot read a gate deferral whose holding condition has no id, so PL-B396 and the three entries it blocks, deferred to Gate 3 on 2026-09-27, still count as work Gate 2 can clear and hold the beat at clear the gate

**Found by `PL-DB64`, 2026-09-27, measured.** `PL-DB64` deferred `PL-WZVZ`,
`PL-B396`, `PL-0S0V`, `PL-VJZK` and `PL-KZ99` from Gate 2 to Gate 3 on
`ROADMAP.md` § "The cadence" beat 3's terms (project owner, 2026-09-27,
ratified), writing the paragraph beat 3 asks for and moving the five into a
group headed `Deferred to Gate 3 on 2026-09-27`. `bin/docket wave --no-fetch`
then printed the same gate line on `main` at `19af95d` and on that branch - 95
entries this gate can clear, 3 the milestone clears itself, 14 held outside it -
and the 95 still held `PL-0S0V`, `PL-B396`, `PL-KZ99` and `PL-VJZK`. `PL-WZVZ`
was among the 14 before the change as after it.

**Why.** `roadmap.gate_status` takes an open entry out of `clearable` in two
cases only: its `blocked-by` chain leaves the frozen list (`blocked_outside`),
or the milestone's own `Required scope` names it (`self_cleared`). Its docstring
refuses a third on purpose - the section's group headings "are not read, and
are not the test" - because on Gate 1 a heading summarising a fact the rule
already computes had disagreed with the rule. Beat 3's third disposition is not
a fact the items compute. It is a decision the gate's own section records, so
the two readings agree only where the deferred entry's holding condition also
has an id: `PL-WZVZ` through `PL-TBMK` and `PL-4TWW` (`PL-0H5D`), `PL-Y04W`
through `blocked-by: v0.7.0`. `PL-B396` is a `needs-decision` stand-in for
planned-milestone item 28, which has neither an id nor a version a `blocked-by`
could hold, and the other three are blocked by it alone.

**Why it matters.** `roadmap.wave` keeps the beat at `clear` while
`gate.is_clear` is false, and `is_clear` reads `clearable`. So when every other
Gate 2 entry has closed, `wave`, the session-start digest and every "what is
left" report will still say Gate 2 is open, naming four entries the gate
section says are deferred, and each reader will subtract them by hand from
prose - the re-derivation `CLAUDE.md` § "Prefer deterministic tooling over
repeated model work" exists to remove. It recurs: Gate 3 inherits the same
five unless item 28 or machine selection is scheduled before v0.6.0 ships, and
beat 3 itself calls a gate with a deferral in it the normal case.

**Decision needed.** Whether `wave` should read a deferral the gate section
records, and how.

1. **Read the current gate's deferral group.** `gate_status` counts an open
   entry listed under a count-carrying group heading that opens `Deferred to
   Gate N` apart from `clearable`, as a third carve-out beside `blocked_outside`
   and `self_cleared`, and `wave` prints it as deferred to that gate. The
   heading is where beat 3 already requires the section to say so, and
   `tools/doc_check.py`'s `check_gate_counts` already holds its count to the
   entries under it. Cost: an M change to `subprojects/docket/src/docket/roadmap.py`
   and `render.py` with tests, and reversing `gate_status`'s rule against
   reading headings for this one heading kind, which holds because a deferral
   is the decision itself rather than a summary of one the items compute.
2. **A field on the item**, `PL-0H5D`'s rejected first option: a
   `deferred-to:` naming the gate. Cost: a new store field holding a second
   copy of a decision beat 3 puts in the section, and two copies drift.
3. **Leave `wave` as it is.** The v0.6.0 gate section's "What reads this, and
   what reads past it" paragraph already names the four as a known
   disagreement, and whoever calls Gate 2 clear subtracts them by hand. Cost:
   nothing now, and the hand subtraction on every gate report until the four
   close, then again at Gate 3.

*Recommendation: 1.* It reads the decision in the one place beat 3 says it
lives, adds no field, and the heading it reads is already held to its entries
by a check. Option 2 would also let `wave` report Gate 2 clear before item 28
is scheduled, at the price of that second copy; option 3 never would.
