---
id: PL-5WFS
title: docket next cannot see a brief's stated prerequisite, so it offers PL-F52R ahead of the PL-WB0X extraction that gates it
priority: P2
effort: S
status: done
classes: infra
feature: planning-cadence
touches: subprojects/docket/src/docket/plan.py, docs/items/
added: 2026-09-02
closed: 2026-09-04
pr: 292
verify: bin/docket check && grep -q '^blocked-by: PL-VM40' docs/items/PL-SN2C-add-the-playback-multiplier-as-steps-per-tick.md
---

**Problem.** Inside the current step, `docket next` ranks by priority band and
by which feature is nearest finishing. It does not read a brief's body, so a
stated prerequisite — "do this after PL-WB0X stage 1", "depends on PL-DHV7 for
the unit" — is invisible to it.

v0.4.0 is the live instance, as of 2026-09-02. `docket next` offers, in order,
`PL-F52R` (draw the MAC-awake reference band), `PL-ZRSP` (plot the F_A/F_I
ratio) and `PL-DHV7` (express concentrations in MAC multiples) — all `P1`, all
in scope. But `PL-F52R`'s brief says it depends on `PL-DHV7` for the unit, and
`PL-DHV7`'s says to do it after `PL-WB0X` stage 1 (the Flet-free formatting
module). So the first three suggestions are in close to the reverse of the
order the briefs state, and `PL-WB0X` — the item that actually goes first —
is offered nowhere near the top, being `P2`.

**Why it matters.** A session that trusts the ranking starts `PL-F52R`, and
either discovers the dependency after reading the brief (one lookup, the cheap
outcome) or does not, and rewrites formatters that `PL-WB0X` is about to move.
The cost is small per session and paid by every session that picks up v0.4.0
work, which is the whole of the milestone now that it is the current step.

**A mechanism already exists and may be the whole answer.** `status: blocked`
with `blocked-by:` removes an item from `docket next` entirely; `PL-B9PY` uses
it. The open question is whether it is the right instrument here. It is a
strong statement — "cannot be started" rather than "goes second" — and it takes
the item out of the ranking rather than reordering it, so a milestone worked
strictly in dependency order would show most of itself as blocked. The
alternative is a weaker `after:` field that reorders without excluding, which
is new surface for a problem that may not recur.

**Decide before building anything.** Whether this happens often enough to earn
a mechanism at all is the first question, and the honest answer today is one
instance. Using `blocked-by` on `PL-DHV7` and `PL-F52R` costs nothing and would
have prevented this one; that may be the entire fix, with no code.

**Where.** `subprojects/docket/src/docket/plan.py` (the ranking), and the
briefs of `PL-DHV7` and `PL-F52R`, which state the prerequisites in prose.

**Found.** 2026-09-02, recording v0.4.0's scope decisions. `docket next` was
run immediately afterwards and offered `PL-F52R` first, against the sequencing
the same change had just written into `PL-WB0X`.

**Done when.** Either v0.4.0's dependent items carry the prerequisite in a
field `docket next` reads, so the ranking matches the briefs; or the item is
`dropped` with the reason that one instance does not earn a mechanism, leaving
this brief as the record and the prose as the only statement.

**Decision needed.** Does a stated prerequisite get a field `docket next`
reads, and if so which one?

1. **Nothing new: use `blocked-by` on the two v0.4.0 items.** `status:
   blocked` with `blocked-by:` already removes an item from the ranking, and
   `PL-B9PY` uses it. Setting it on `PL-DHV7` (express concentrations in MAC
   multiples) and `PL-F52R` (draw the MAC-awake reference band) costs two
   field edits and no code, and fixes the live instance today. Its cost is
   that "blocked" overstates the case - these are startable, just not first -
   and a milestone worked strictly in dependency order shows most of itself
   as blocked, which degrades what `blocked` means everywhere else.
2. **A weaker `after:` field** that reorders inside a band without excluding.
   Says the true thing, and is new surface in `plan.py` and the item schema
   for a problem with one recorded instance.
3. **Drop it.** Leave the prerequisites as prose, on the ground that one
   instance does not earn a mechanism, and let this brief stand as the record
   so the second instance can be counted against it.

**Recommended: 1 now, and re-raise 2 only if a second instance appears.** The
cost of `blocked` overstating the case is a word; the cost of the ranking
disagreeing with the briefs is a session that rewrites formatters `PL-WB0X`
(split `simulation_view.py`) is about to move. Whichever is chosen, the
v0.4.0 sequencing edit is the deliverable - `PL-WB0X` first, then `PL-DHV7`,
then `PL-F52R` - and it is worth making before the milestone's first item
starts rather than after.

**The "one instance" is now four, and they are live (2026-09-03).** This brief
argued the honest count against a mechanism was one. `PL-WB0X` merged as
`#263` that morning, which released every item that was waiting behind it, and
`bin/docket next` immediately offered a top three that its own briefs order
differently:

| `docket next` rank | Item | What its brief says |
| --- | --- | --- |
| 1 | `PL-ZRSP` (plot the F_A/F_I ratio) | "The control-input timeline (`PL-DR1Z`) is what makes that visible, so land this after it." |
| 2 | `PL-DHV7` (MAC multiples as a display unit) | was "do this after `PL-WB0X` stage 1"; now met |
| 3 | `PL-VM40` (simulated time from a step count) | no open prerequisite |
| — | `PL-F52R` (MAC-awake reference band) | depends on `PL-DHV7` for the unit |
| — | `PL-DR1Z` (control-input timeline) | no open prerequisite; gates `PL-ZRSP` |

So the ranking's first pick is the one item of the three that a brief defers,
and the item that actually unblocks it (`PL-DR1Z`) is `P2` and offered
nowhere near the top. `PL-ZRSP`'s deferral is a **safety** statement rather
than file contention: F_A/F_I is the textbook wash-in curve only while
inspired concentration is held constant, so without the control-input timeline
a learner reads a mid-run vaporizer change as uptake. That is the class of
misreading `CLAUDE.md`'s clinical-output standard names, and it is invisible
to a ranker that does not read the body.

This is the whole of the current step's work rather than one item, so the cost
is now paid by every session that picks up `v0.4.0`, and the wrong answer is
*silent* — `docket next` states a reason and the reason is sound as far as it
goes. That satisfies `CLAUDE.md`'s test for friction that earns an
interruption rather than a filing.

Nothing here changes the recommendation the brief already makes: setting
`blocked-by` on the dependent items costs two field edits and no code. What
changed is that it is now four items, not one, so "does this recur often
enough to earn a mechanism" has an answer.

## Decided: option 1 (project owner, 2026-09-04)

**A stated prerequisite gets `blocked-by`. No new field, and no change to the
ranking.** Three edges declared in this change, each a sequencing block whose
brief says so in the body:

| Item | Was ranked | Now blocked on | Stated where, before this |
| --- | --- | --- | --- |
| `PL-011` (bound the history) | 3rd | `PL-W3DD` | only in `PL-THVN`, a separate item filed to notice it |
| `PL-RCTQ` (the docs sweep) | 6th | the 8 milestone items it describes | its own "Done when" |
| `PL-SN2C` (playback multiplier) | 7th | `PL-VM40` | its own "Why it matters" |

**Why not option 2, the weaker `after:` field.** Its case was that `blocked`
overstates "goes second". That is a statement about a word, and the cheaper fix
is to define the word: `subprojects/docket/README.md` § "`blocked` means 'not
first', and that is the whole of it" now says a sequencing dependency is a
legitimate use, and asks the body to say which kind it is. That removes option
2's entire justification for one paragraph instead of new surface in the item
schema, `plan.py`, the checker and `triage`'s rules text.

**Why not a successor-count term in the ranking.** Considered and rejected on
structure rather than cost. Priority rules in the resource-constrained project
scheduling literature answer "which of several *eligible* activities do I start
when *resources are scarce*", minimising makespan; the well-studied families are
the critical-path rules (LFT, LST) and the successor-count rules (MIS, MTS).
This queue has the opposite shape - abundant eligible work, effectively one
worker, and a cost function that is *rework* rather than makespan. The half of
that model which transfers is the precedence network, which is what `blocked-by`
already is; the priority-rule half solves contention this queue does not have.

Worth recording that the obvious supporting argument is false: MTS (most total
successors) is reported among the best-performing rules alongside LFT and LST,
so "successor-count ordering is a weak heuristic" would not have been a
defensible reason. See Turkakin OH, Arditi D, Manisali E. Comparison of
heuristic priority rules in the solution of the resource-constrained project
scheduling problem. Sustainability 2021;13(17):9956, doi:10.3390/su13179956
(open access); and Kolisch R. Efficient priority rules for the
resource-constrained project scheduling problem. J Oper Manag
1996;14(3):179-192, doi:10.1016/0272-6963(95)00032-1 - which is about
resource-based slack rules (WCS, ACS) and is not evidence about successor
counts, despite being cited for it. Bibliographic details verified against
publisher records; the articles themselves could not be opened from this
environment, so treat their contents as indirectly verified.

**What is left, and it is not this item.** Declaring an edge is a one-off;
*noticing* that one is undeclared is the recurring cost, and every instance so
far was found by a person reading a brief - `PL-9K7K` found one, `PL-THVN`
found another, this item found a third, and a fourth (`PL-SN2C`) turned up on
a grep while deciding it. `PL-ZBRB` carries the detector.
