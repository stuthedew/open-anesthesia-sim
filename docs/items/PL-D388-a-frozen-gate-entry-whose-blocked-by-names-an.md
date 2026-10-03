---
id: PL-D388
title: A frozen gate entry whose blocked-by names an item no list holds silently leaves what bin/docket wave asks the gate to clear: PL-VV6N sits under 'Cleared before v0.6.0 begins' behind PL-YVV4, so Gate 2 can read clear with it undecided, and nothing checks the 2026-08-30 rule that what an entry needs is let in
priority: P2
effort: M
status: ready
classes: defect, infra
feature: gate-prerequisites
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md, .claude/skills/docket/modes/release.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21) and not safety or science; its problem was present at the freeze, so the presence test answers yes, and it is deferred on a stated reason: its one instance on this list, PL-VV6N, is disposed by the owner's answer recorded here whether or not the check is built first, and the check itself guards the triage passes and freezes still to come rather than any v0.6.0 entry
added: 2026-10-03
payoff: A frozen entry can leave what the gate is asked to clear only through a disposition its section records, so bin/docket wave cannot report Gate 2 clear while an entry like PL-VV6N sits undecided behind a prerequisite no list holds
verify: grep -q 'def check_gate_prerequisites' tools/doc_check.py
---

**Problem.** A frozen gate entry whose blocked-by names an item no list holds silently leaves what bin/docket wave asks the gate to clear: PL-VV6N sits under 'Cleared before v0.6.0 begins' behind PL-YVV4, so Gate 2 can read clear with it undecided, and nothing checks the 2026-08-30 rule that what an entry needs is let in

**Why it matters.** `bin/docket wave` counts a frozen entry as "blocked
outside the gate" the moment its `blocked-by` chain leaves the frozen list,
and `roadmap.GateStatus.clearable` then leaves it out of what the gate is asked
to clear. `is_clear` asks only that `clearable` be empty and every id be
known, so once the clearable entries close, the beat moves to "implement" with
that entry still open. That is a deferral nobody recorded:
`ROADMAP.md` § "The debt gate" -> "The cadence" beat 3 admits one only where
the gate section says so and why and names the later gate. `PL-9S30` called
the same shape "renegotiation by frontmatter" at Gate 1.

**Measured 2026-10-03 on `origin/main` at `e93af565`**, with
`roadmap.gate_status` and its own transitive `prerequisites` walk: 17 of Gate
2's 50 open entries are blocked outside the gate.

- 11 are v0.6.0's own work waiting on v0.6.0's own build, `PL-1FT6` (the
  LayoutModel) and four siblings. They are named in Required scope and filed
  under "Cleared by v0.6.0 itself"; `PL-W9BK` is wave's mislabel of them.
- 5 are the Gate 3 deferrals `PL-DB64` recorded (project owner, 2026-09-27,
  ratified). Their chains leave the list at `PL-YRLM`, `PL-TBMK`, `PL-4TWW`
  and `PL-2FZ9` on purpose, which is how wave reads a deferral (`PL-18BD`).
- 1 is neither. `PL-VV6N` (decide a retention rule for items captured but
  never worked) sits under "Cleared before v0.6.0 begins, the workflow lane"
  and its `blocked-by` names `PL-YVV4` (run the suppression count), a
  `planning` item the freeze's class filter left off the list. Gate 1's
  section declined `PL-VV6N`
  on 2026-09-13 for exactly this reason ("Admitting it would put an entry on
  the frozen list that cannot close until one that is not on the list closes
  first"); Gate 2's freeze took it back by class and left its prerequisite
  behind.

The cost is already paid once. The Order's item 14 design round (#1296, #1297,
#1298, 2026-10-03) took the needs-decision entries wave lists as clearable, and
`PL-VV6N` was not among them.

`PL-1RTM` was a second case until #1300 merged at 20:25Z the same day.
`PL-2JRC`'s triage (#880, 2026-09-21) made `PL-H0CF` its blocker and, in the
same pass, deferred `PL-H0CF` to the next gate by its capture date, writing
that "the gate still reaches it, through the entry it blocks". Wave read it the
other way and dropped `PL-1RTM` from what the gate is asked to clear. #1300
closed the two together, which is the pairing the roadmap asks for.

**Why it keeps happening.** The frozen list is computed by class and status
(`plan.is_debt`: `defect`, `safety`, `science`, `refactor`, `perf`, or
`needs-decision`), and what a debt entry waits on is usually not debt. Counted
from every `blocked-by` value ever written on a frozen entry (each item file's
`git log -p --follow`, the blocker classed by its classes and its `added` date
against the freeze): 38 entry-blocker pairs on Gate 1's list (22 entries) and
28 on Gate 2's (18 entries). Of the 66, 36 name a `feature`, `planning`, `docs`
or `ux` item, 11 the milestone's own Required scope, 9 a later version, 6 debt
that had closed by the freeze, and 4 debt captured after it. So a
class-computed list is not closed under its own prerequisites by construction,
and after the freeze a triage pass defers a new capture by its date without
asking whether a frozen entry waits on it: v0.6.0's
§ "Deferred from this gate" says "the presence test, which answers no".

`PL-9S30` fixed Gate 1's instance by writing the dispositions into
`ROADMAP.md` by hand. `PL-SL70`, `PL-WZBX`, `PL-7CSP`, `PL-FCM3` and `PL-FD5Q`
then taught wave to count such entries more exactly. None of them refuses an
entry that no section disposes of, so the shape came back at the next gate.

**Decision needed.** The project owner asked on 2026-10-03: "If an item is a
pre-rec to a gate item then shouldn't it automatically be in the gate?"
Whether a frozen entry's open prerequisites join the gate automatically, or
each must be accounted for and `make check` refuses one that is not.

**Recommendation: account for each, and refuse the unaccounted; do not admit
automatically.** The roadmap already gives every kind of prerequisite a home.
The milestone's own Required scope makes the entry the milestone's (§ "Debt
inside the milestone's own scope"). Work no release schedules defers the entry
(§ "The cadence" beat 3). Everything else joins the list beside the entry it
completes (§ "The gate is a snapshot, not a moving target": "what an entry
needs is let in", project owner, 2026-08-30). Automatic admission would put all
three kinds on the list. On the store measured above it admits 10 items:
`PL-1FT6` (L), `PL-2KXB` (L), `PL-W9P6`, `PL-WV9K` and `PL-R1WQ`, which are
v0.6.0's own build; `PL-TBMK`, `PL-4TWW`, `PL-2FZ9` and `PL-YRLM`, which are
the work `PL-DB64` deferred to Gate 3; and `PL-YVV4`. Nine of the ten cannot
close before v0.6.0 begins, which is the deadlock `PL-D143` recorded at Gate 1.
One belongs. Release planning states the constraint underneath the same way: a
requirement is available in a release only if everything it depends on,
transitively, is in that release too (Bagnall, Rayward-Smith and Whittley, "The
next release problem", *Information and Software Technology*
43(14):883-890, 2001, doi:10.1016/S0950-5849(01)00194-X; the formal statement is
restated in Jiang, Xuan and Ren, GECCO 2010, arXiv:1704.04773). The list has to
be closed under its prerequisites; here closure is reached from either end.

**The build, on that recommendation.**

1. **The check.** In `tools/doc_check.py`, a `check_gate_prerequisites`
   beside `check_self_cleared_group` (`PL-J6HP`), which already reads
   `_gate_groups` and imports `docket.roadmap`: for the current gate, hold the
   section's groups and `roadmap.gate_status`'s buckets to one answer per open
   entry, in both directions.
   - An entry under a "Cleared before vX.Y.Z begins" group that `gate_status`
     counts as blocked outside is an error, `PL-VV6N`'s case. It names the ids
     the entry waits on and the remedy that fits. Where every one is in
     Required scope, the remedy is to declare the entry there or defer it.
     Otherwise, admit those ids to the list, dated, as what the entry needs, or
     move the entry to a deferral group on beat 3's terms.
   - An entry under a deferral group that `gate_status` counts as clearable is
     an error too, `PL-18BD`'s case. Its remedy is the holding condition that
     item's ratified answer gives a deferral.
   - Entries under "Cleared by vX.Y.Z itself" stay `check_self_cleared_group`'s.

   `gate_status` itself still reads no heading, as its docstring and
   `PL-18BD`'s answer keep it. The check makes the section agree with it.
2. **The rule, written where each session meets it.** One sentence in
   § "The gate is a snapshot, not a moving target" naming the three homes.
   § "Deferred from this gate"'s opening sentence corrected, so a capture a
   frozen entry waits on is not deferred by its date. One sentence in
   `.claude/skills/docket/modes/release.md`'s freeze mode, which is where a
   freezing session reads the rule.
3. **The instance, so the check lands green.** Recommended: admit `PL-YVV4`
   to Gate 2's workflow-lane group beside `PL-VV6N`, dated and citing this item
   and the 2026-08-30 rule, and give the pair the design round the item 14
   round skipped. Its count gates only the answer that tightens intake, because
   `.claude/rules/expert-review.md` asks for a count before tightening anything.
   So if the owner keeps capture unbounded, `PL-VV6N` closes without it, and
   `PL-YVV4` drops as moot. The alternative is deferring the pair to Gate 3 as
   Gate 1 did; that would be the third gate to carry one decision.

   The second direction has a pending instance. `PL-YBFB` (defer `PL-5B1N` to
   Gate 3) was claimed at 20:43Z on 2026-10-03, and as briefed it moves
   `PL-5B1N` into the deferral group without a holding condition. `PL-5B1N`
   carries no `blocked-by`, so wave would keep it among the 30 entries this
   gate can clear, which is `PL-18BD`'s case again. The thread holding
   `PL-YBFB` was told the same day, and its file was left alone under the claim.

**Generator check.** The fact is the one `PL-WD5Z` and `PL-J6HP` state, a debt
item's gate disposition, at the frozen entries that `PL-WD5Z`'s field does not
reach: `bin/docket check` refuses `deferred-from:` on an entry the gate
places. So a frozen entry's deferral is its group heading, and wave reads it
through `blocked-by` (`PL-0H5D` and `PL-18BD`, both ratified, over a field).
Any off-list blocker therefore reads as a deferral, whether or not anyone
deferred anything. This item was filed after both heads closed, so it is a
post-close instance. `PL-18BD` (2026-09-27) is the mirror instance read at the
fact rather than at `blocked-by`, though its own check named it a re-entry of
`PL-0H5D`. That makes two; a third counts as a generator whose fix did not
hold. The check above refuses both directions, which is the reason to build it
rather than settle `PL-VV6N` alone.

**Done when.** `make check` fails on a store where an entry under "Cleared
before vX.Y.Z begins" waits on an id that neither the list nor Required scope
holds, or where an entry under a deferral group is one wave counts as
clearable. It passes once the id is admitted or the entry is deferred with a
holding condition. The three prose places state the same rule. `PL-VV6N` has a
disposition on `main`.

## Answers 2026-10-03

Account for each prerequisite, and let `PL-YVV4` into Gate 2 beside `PL-VV6N`
(project owner, 2026-10-03, ratified, over admitting every open prerequisite of
a frozen entry automatically and over deferring `PL-VV6N` and `PL-YVV4` to
Gate 3). The owner asked the same day whether deferring a prerequisite defers
the gate item that waits on it. It does, so under this answer that move is
recorded in the gate's section with its reason, and the check refuses the
silent half of it: a deferred prerequisite under an entry still listed as this
gate's work. Status moved to `ready` with this answer, as `docket check`
requires of an answered question.

Step 3's admission was made the same day: `PL-YVV4` is on Gate 2's workflow
lane with `ROADMAP.md` § "Deferred from this gate" naming the date and the
ground, so `bin/docket wave` counts `PL-VV6N` and `PL-YVV4` among the entries
this gate can clear. The pair's design round, and steps 1 and 2, remain.
