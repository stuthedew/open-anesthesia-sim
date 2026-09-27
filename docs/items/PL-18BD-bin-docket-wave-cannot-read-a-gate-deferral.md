---
id: PL-18BD
title: bin/docket wave cannot read a gate deferral whose holding condition has no id, so PL-B396 and the three entries it blocks, deferred to Gate 3 on 2026-09-27, still count as work Gate 2 can clear and hold the beat at clear the gate
priority: P2
effort: S
status: done
classes: defect, planning
touches: ROADMAP.md, docs/items/PL-B396-agent-amounts-are-displayed-in-litres-of-vapour.md, docs/items/PL-KZ99-store-each-agent-s-molar-mass-and-liquid.md, docs/items/PL-0S0V-agent-volume-display-decimals-and-the-other.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-27 on the owner's answer to its decision
added: 2026-09-27
closed: 2026-09-27
pr: 1165
payoff: bin/docket wave's Gate 2 count stops listing four entries the roadmap defers to Gate 3, so the gate reads clear when the work it can clear is done, with no hand subtraction from prose
verify: grep -qF 'blocked-by: PL-YRLM' docs/items/PL-B396-*.md
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
could hold, and it is the only open blocker of the other three.

**Why it matters.** `roadmap.wave` keeps the beat at `clear` while
`gate.is_clear` is false, and `is_clear` reads `clearable`. So when every other
Gate 2 entry has closed, `wave`, the session-start digest and every "what is
left" report will still say Gate 2 is open, naming four entries the gate
section says are deferred, and each reader will subtract them by hand from
prose - the re-derivation `CLAUDE.md` § "Prefer deterministic tooling over
repeated model work" exists to remove. It recurs: Gate 3 inherits the same
five unless item 28 or machine selection is scheduled before v0.6.0 ships, and
beat 3 itself calls a gate with a deferral in it the normal case.

**Decision needed.** Whether `wave` should agree with a deferral the gate
section records, and how.

1. **Give the condition an id, as `PL-0H5D` did for `PL-WZVZ`.** File one item
   off the frozen list holding the question `PL-B396` holds today - which
   release builds planned-milestone item 28 - and set `PL-B396` to `blocked`
   on it, so `PL-B396` becomes the work its title names. `_blockers_outside`
   follows `blocked-by` transitively and skips closed blockers, and `PL-B396`
   is the only open blocker of the other three (`PL-S6WW`, the other one
   `PL-0S0V` and `PL-KZ99` name, closed on 2026-09-17), so all four move from
   `clearable` to `blocked_outside` with no code change. That is the route
   taken for `PL-WZVZ` through `PL-TBMK` and `PL-4TWW` (project owner,
   2026-09-21, ratified, over a `blocked-on:` field). When a release schedules
   item 28, the holding item closes and `PL-B396` takes that version in
   `blocked-by:`, as `PL-Y04W` took `v0.7.0`. Cost: `PL-B396`'s front matter
   and brief change, the gate section's "What reads this, and what reads past
   it" paragraph is rewritten to say the two readings agree, and each later
   deferral whose condition has no id needs a holding item of its own.
2. **Read the current gate's deferral group.** `gate_status` counts an open
   entry listed under a count-carrying group heading that opens `Deferred to
   Gate N` apart from `clearable`, as a third carve-out beside `blocked_outside`
   and `self_cleared`, and `wave` prints it as deferred to that gate. The
   heading is where beat 3 already requires the section to say so, and
   `tools/doc_check.py`'s `check_gate_counts` already holds its count to the
   entries under it. Cost: an M change to `subprojects/docket/src/docket/roadmap.py`
   and `render.py` with tests, and reversing `gate_status`'s rule against
   reading headings for this one heading kind, which holds because a deferral
   is the decision itself rather than a summary of one the items compute.
3. **A field on the item**, `PL-0H5D`'s rejected first option: a
   `deferred-to:` naming the gate. Cost: a new store field holding a second
   copy of a decision beat 3 puts in the section, and two copies drift.
4. **Leave `wave` as it is.** The v0.6.0 gate section's "What reads this, and
   what reads past it" paragraph already names the four as a known
   disagreement, and whoever calls Gate 2 clear subtracts them by hand. Cost:
   nothing now, and the hand subtraction on every gate report until the four
   close, then again at Gate 3.

*Recommendation: 1.* It makes `wave` agree for all five with nothing built, by
the route the project already ratified for this exact problem on `PL-WZVZ`,
and it leaves `gate_status`'s rule against reading headings intact. Option 2
is the general fix, and is worth its M change only if deferrals whose
condition has no id keep arriving: this is the second in two gates, and the
first was answered by filing its condition as items. Option 3 is the second
copy option 2 avoids, and option 4 keeps the hand subtraction.

**Answered 2026-09-27: option 1, the holding item** (project owner, ratified,
over teaching `wave` to read the deferral group, a `deferred-to:` field, and
leaving `wave` as it is). The holding item is `PL-YRLM`, which takes over the
question of which release builds planned-milestone item 28, carrying
`deferred-from: v0.6.0` because it was captured after Gate 2 froze.

**Generator check.** The misread fact is that a condition on an unscheduled
planned-milestone item has no id a `blocked-by` can hold, so every reader of
`blocked-by` takes the waiting item as unblocked. `PL-0H5D` answered it for
`PL-WZVZ` on 2026-09-21 by filing the condition as items, and this is the same
mechanism at a sibling site within 30 days, answered the same way: a re-entry of
`PL-0H5D`, whose survey counted one known case where `PL-B396`'s brief already
recorded a second. No head's `misread:` states the fact (`bin/docket generators
--misread`, read 2026-09-27), and two sites is short of a generator.

**Done when.** `PL-B396` is `blocked` on `PL-YRLM`, and its brief says the
question moved there; `bin/docket wave` counts `PL-B396`, `PL-0S0V`, `PL-VJZK`
and `PL-KZ99` among the Gate 2 entries waiting outside the list rather than
among those it can clear; and the v0.6.0 gate section's "What reads this, and
what reads past it" paragraph says the two readings agree for all five.
