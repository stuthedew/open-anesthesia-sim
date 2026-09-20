---
id: PL-7RYB
title: PL-JQJQ's brief does not mark its design decision as ratified rather than specified, and nothing sweeps the items closed before that rule landed on 2026-09-16
priority: P2
effort: S
status: done
classes: docs, planning
feature: queue-hygiene
touches: CLAUDE.md, docs/items
added: 2026-09-16
closed: 2026-09-20
pr: 782
payoff: stops a later session defending 108 pre-rule decisions - most of them earlier sessions' own recommendations - at the bar reserved for ones the owner specified
verify: grep -qF 'form records no kind at all' CLAUDE.md
---

**Problem.** `CLAUDE.md` gained the ratified-versus-specified rule on
2026-09-16: a decision taken on a session's recommendation is written
`(project owner, DATE, ratified)` and names in one clause what it was chosen
over, so a later session can tell a design the owner authored from one they
nodded at, and so the two carry different bars to reopen.

`PL-JQJQ` closed hours before that rule landed and is a clean instance of what
it governs. The owner proposed pointing the system `python3` at 3.14; the
session refused it and recommended the `PreToolUse` guard hook; the owner
replied "Agree with recs". That is ratification, not specification, and the
brief does not say so - it records the rejected mechanism and the reasoning at
length, which is the harder half, but not the one word that sets the bar for
reopening it.

**The general half, which is the reason this is an item rather than a
one-line edit.** Every decision recorded before 2026-09-16 carries the plain
form or no marker at all, so the absence of `ratified` currently means
"specified" and "closed before the rule existed" indistinguishably. That is
the rule reading backwards as the opposite of what it says. Whether to sweep,
how far back, and whether an unmarked pre-rule decision should instead be read
as unknown are the questions to answer; a blanket retro-marking would be a
session asserting what the owner meant on decisions nobody can now reconstruct.

**Where.** `docs/items/PL-JQJQ-a-bare-python3-here-is-the-3-11-tools-floor-so.md`
for the concrete instance. The general half touches whatever the sweep decides,
and may be answerable by a check: whether a closed item's brief carries a
decision marker at all is decidable by reading the file, though which kind it
should be is not - that is the judgment half `CLAUDE.md` says not to script.

**Why it matters.** It is small but it fails in the direction that costs: the
bar to reopen a ratified decision is ordinary evidence, and the bar for a
specified one is a compelling argument. A session reading `PL-JQJQ` today would
apply the higher bar to a decision the owner nodded at, which is exactly the
confusion the new rule was written to remove.

**Found** while working `PL-FBXP` (the seven owed pull request numbers), when
the re-read `CLAUDE.md` showed the rule had landed mid-session.

**Done when.** `PL-JQJQ`'s brief marks its decision `(project owner, 2026-09-16,
ratified)` with the clause naming the `python3`-at-3.14 route it was chosen over,
and the general question below has an answer recorded - whichever way it goes - so
that the absence of a marker on a pre-2026-09-16 decision means one thing rather
than two.

**Decision needed.** How should a decision recorded *before* 2026-09-16 be read?
`CLAUDE.md`'s rule gives the plain form the meaning "specified", which carries the
higher bar to reopen, so every decision already in the store now reads as
specified whether it was or not. Three dispositions, and the choice is the project
owner's because it is about what their own past decisions meant:

1. **Read an unmarked pre-rule decision as unknown** and mark it so. Honest, and
   it requires a session to assert nothing it cannot know.
2. **Sweep and mark each one** from the reasoning recorded in its brief. The most
   useful and the least safe - a session asserting what the owner meant on
   decisions nobody can now reconstruct.
3. **Leave them and apply the rule forward only**, accepting that every pre-rule
   decision carries the higher bar by default.

The concrete half is not open in the same way and does not wait on this:
`PL-JQJQ`'s exchange is on record - "Agree with recs" to a session's
recommendation - so it is ratified under any of the three, and marking it is this
item's first edit.

**Decided 2026-09-20, by this session rather than by the project owner.** Rule
14 of `.claude/rules/instruction-writing.md` (project owner, 2026-09-19) landed
three days after this brief was written, and it turns who-decides on
*consequence* rather than on what the answer rests on: resting on "what the
project wants" does not make a granular choice the owner's. Under the route
taken the blast radius is one clause of one document, no item is edited, and
nothing is asserted about any past decision - which dissolves the reason this
brief gave for escalating, since "a session asserting what the owner meant on
decisions nobody can now reconstruct" is a property of dispositions 1 and 2 and
of neither of the others.

**The route is a fourth, and it was chosen over all three above.** The
ambiguity is not in the store; it is in the rule. Every marker already carries
its date, and a rule cannot bind a record written before it existed - so the
only thing missing was a sentence saying what the plain form means on a date
the notation did not yet exist on. `CLAUDE.md`'s `Record which it was` bullet
now carries it: from 2026-09-16 the plain form means specified, and dated
earlier it records no kind at all, is read as unrecorded, and is reopened on
ordinary evidence while saying the kind is unrecorded.

That is disposition 1's honesty at disposition 3's cost. It reaches all 235
dated attributions in the tree rather than the 108 pre-rule ones a sweep would
have had to find, edits none of them, and asserts nothing. Disposition 3 was
refused on the merits rather than on cost: most decisions here arrive as a
session's recommendation the owner agrees to, so defaulting the pre-rule corpus
to the higher bar freezes a large body of session-authored design behind the
owner's signature, which is exactly what `PL-XWH4` wrote the rule to stop.

**Which bar "unrecorded" carries, and why it is the lower one.** Both bars end
at the owner and differ only in how much evidence is wanted before raising it.
A session cannot calibrate against a record that does not say, so it takes the
bar that errs toward asking and hands the calibration back by naming the gap. A
decision wrongly re-raised costs one exchange; a decision wrongly frozen stands
for the life of the project.

**The boundary is 2026-09-16 inclusive, so the landing day sits on the recorded
side.** `PL-XWH4` landed the rule and swept that day's own decisions, and
`PL-QNMM` measured that every `ratified` mark in `ROADMAP.md` and
`docs/MODEL.md` is dated 2026-09-16 or later. The first day the notation was
applied deliberately is the first day it can be read from.

**No check was built, and this is the measured reason rather than an
omission.** The decidable-looking rule is "a `ratified` marker names what it
was chosen over". Counted 2026-09-20 over `docs/`, `CLAUDE.md`, `ROADMAP.md`,
`.claude/` and `subprojects/`: 36 post-rule `ratified` markers, 27 of them bare
and 9 carrying the clause. Reading the bare ones shows them to be *citations*
of a decision recorded in full elsewhere - `PL-T7VS` and `PL-6YL1` both cite
`PL-6TP8`'s retirement from a `reason:` line, and `PL-F48B` carries its clause
in the sentence after the parentheses rather than inside them. A check on the
bare form would fire on ~75% true citations, which is `CLAUDE.md`'s own
definition of a defect in the check rather than of coverage; whether a marker
is a primary record or a citation is not decidable from the file, and it is the
judgment half. So the rule stays prose, and the next session need not re-derive
this.

**What the resident-set edit paid.** `CLAUDE.md` requires every edit to it to
name what it replaces or say why nothing can be cut. Nothing was cut, and the
reason is placement rather than wordiness: the clause corrects the exact
sentence that was wrong, inside the one bullet that defines the notation.
Routing it to a path-scoped rule would be `PL-6SBB` in its own terms - the
definition of a notation is resident, so a session holding the notation and not
the caveat misreads a marker without opening any file to find it, the ones in
`CLAUDE.md` and `ROADMAP.md` included. Net growth is about 250 characters
against 108 pre-rule markers a sweep would have had to edit.

**Done (met).** `PL-JQJQ` marks its decision `(project owner, 2026-09-16,
ratified, over pointing the system `python3` at 3.14)`, with a line saying the
marker is retrospective and what the exchange was. The general question is
answered in `CLAUDE.md` itself, so the absence of a marker on a pre-2026-09-16
decision now means one thing rather than two. `PL-QNMM` - the
`ROADMAP.md`/`docs/MODEL.md` sweep, still `ready` at `P3` - records what the
rule changed for it: its 52 outstanding attributions stop being what makes the
record honest, its "list the undecidable ones" clause is discharged by the rule
itself, and the one form it now needs, `(project owner, DATE, specified)` for a
pre-rule decision the sweep confirms, is recorded there rather than in the
resident set.
