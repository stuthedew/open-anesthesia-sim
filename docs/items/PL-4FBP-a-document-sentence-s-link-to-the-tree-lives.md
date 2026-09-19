---
id: PL-4FBP
title: A document sentence's link to the tree lives only in the reader's head, so each drift is repaired by hand: decide whether a live assertion must name what it asserts, and a dated one carry its date
priority: P2
effort: M
status: needs-decision
classes: docs, infra
feature: generator-heads
touches: tools/doc_check.py, docs/MODEL.md, docs/items
added: 2026-09-17
root-cause-of: PL-8LDF, PL-2M9N, PL-41YP, PL-GQWP, PL-5N7T, PL-9LXK, PL-T9XJ, PL-4RHP, PL-DHJ7, PL-B8V1, PL-NLP4, PL-LM8P, PL-NWTM, PL-B5LB, PL-GTSL, PL-036, PL-0VFF, PL-C25K, PL-N32Y, PL-FV7G, PL-BHJW, PL-C7XV, PL-0R06, PL-DBGT
---

**Problem.** The project's authoritative documents were written as prose for a
human reader and only later became the specification the code is judged
against. The link from a sentence to the identifier, test, constant or count it
names therefore exists only in the reader's head, so nothing can tell a
statement that is still true from one the tree has moved past. Fifteen open
items repair one such sentence each, or ask for one more check over one more
family of them.

**Why it matters.** `CLAUDE.md` calls a stale statement about what a value
means a safety issue rather than tidiness, and this is the cluster that
produces them. The instances already run from a count that misleads a session
sizing the debt gate (`PL-B8V1`, `PL-NLP4`, `PL-4RHP`, `PL-DHJ7`) to a
`docs/MODEL.md` guarantee that exists as prose and nowhere else - `PL-NWTM`,
which is `safety`-classed and says the unconditional displayed set has no
structural home in the code at all.

The self-generating half is that every document maintained correctly produces
more of them. `docs/MODEL.md`'s "Required invariants" (eighteen when
`PL-8LDF` was filed, twenty-one today) and "Required tests" (fifteen then,
seventeen today) name things without naming *which* things (`PL-8LDF`,
`PL-2M9N`); `README.md` states three capability facts whose authority is a
Python constant with nothing comparing the two (`PL-GQWP`); two documents
hand-enumerate the CI floor job (`PL-5N7T`). Each is found by a session reading
the files rather than by anything that runs, one at a time, and each becomes
its own item.

**Why this item is the head - and this one is a refusal rather than a gap.**
Confirmed against the store on 2026-09-18. `PL-036` is the only other open item
whose subject is the mechanism, and its own `Decided` section closes the
general case: *"Recorded, and not to be revisited by tooling: whether a
documented statement is still true stays human."* Its `Done when` implements
one link - fifteen bullets under `docs/MODEL.md` "Minimum displayed outputs"
named against `SimulationSnapshot` fields. Writing `root-cause-of:` onto it
would record a claim its own brief contradicts and promote a narrow item above
every band but `P0`, where nobody could work the cluster from it. `PL-9LXK`
carries the owner's decision for the *count* half only.

**Decision needed.** Whether the annotation convention is adopted - and note
that this is a decision about scope rather than about truth. `PL-036`'s recorded
principle - the tool checks **linkage, not truth** - is not in question and is
not reopened here. What is unsettled is whether the *convention* is adopted:
that an assertion in an authoritative document names the tree entity it
asserts, so `doc_check` can resolve the link without deciding the sentence.
That is the annotation pass `PL-036` itself calls "eighteen judgments, not the
forty lines of checking", and it is what would close the cluster rather than
one bullet list of it. Two sub-questions come with it: which documents the
convention binds - `docs/MODEL.md` and `README.md` are held to the specialist
standard, the apparatus files are not - and what an assertion that legitimately
names nothing looks like, so the convention has an escape that is declared
rather than assumed.

**The items this explains (15, confirmed 2026-09-18 against each brief).**
`PL-8LDF`, `PL-2M9N`, `PL-41YP`, `PL-GQWP`, `PL-5N7T`, `PL-9LXK`, `PL-T9XJ`,
`PL-4RHP`, `PL-DHJ7`, `PL-B8V1`, `PL-NLP4`, `PL-LM8P`, `PL-NWTM`, `PL-B5LB`,
`PL-GTSL`. This is the 2026-09-17 candidate list, each re-read and still open;
`PL-NLP4` and `PL-NWTM` are `blocked` and stay members, since a root cause
explains an item whatever its status.

Four of them - `PL-LM8P`, `PL-B5LB`, `PL-GTSL`, `PL-T9XJ` - are one-off repairs
of one stale sentence each, which the head would re-point rather than close.
`PL-6ZQY` lists `PL-LM8P` as a drop candidate; being a drop candidate is a
question about whether that instance still reproduces, not about what caused
it, so it is named here and the drop stands or falls on `PL-6ZQY`'s own sweep.

**A confirmed floor rather than a census.** The store holds further instances
of the same sentence-to-tree link that this list does not name - `PL-0VFF`,
`PL-C25K`, `PL-N32Y` and `PL-FV7G` in `ROADMAP.md`, `PL-BHJW`, `PL-C7XV` and
`PL-0R06` in `docs/WORKING_NOTES.md`, `PL-DBGT` in the agent data files. They
are left out because they were read from their titles today and not from their
briefs, and the field is a recorded fact rather than an inference. A later
session working this head should expect the cluster to be larger than fifteen.

**Done when.** The decision below is recorded on this item as `(project
owner, DATE, ratified)` or refused with its reason where the next session meets
it. If adopted: the four clauses stand in `docs/MODEL.md` beside the hazard
table's own sentence and in `tools/doc_check.py`'s module docstring;
`check_bound_families` holds the hazard table and gates `make check`; and every
member carries the disposition the table below gives it - re-pointed,
re-scoped, or dropped with the reason - with `PL-036`, `PL-8LDF` and `PL-2M9N`
re-scoped as the three annotation passes. If refused: the members stay one-off
repairs, and the refusal names which of the four clauses fell and why, so the
next instance is filed against a decision rather than against this question.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found only two with a causing item in the store (`PL-BHVM`,
`PL-L4YG`); this item was filed to record that this cluster had none, and that
`PL-036` refuses to be one. On 2026-09-18 it became the head itself - the
second of the two endings its own `Done when` offered, since the first would
have meant widening `PL-036` against its own recorded decision.

**Confirmed 2026-09-19, against each brief.** The eight named above as read
from their titles were read in full this session, and all eight are the
mechanism: `PL-0VFF` (a frozen list whose entries name items the store has
since closed), `PL-C25K` (a release's definition of done asserting an item is
in effect that is `dropped`), `PL-N32Y` (a frozen scope line naming a stored
quantity the data files do not hold), `PL-FV7G` (a release row's "nothing ...
yet" outlived by the item it names), `PL-BHJW` (a dated note naming a CI job
folded away the same day), `PL-C7XV` (a dated sentence edited to carry a later
roadmap position), `PL-0R06` (a dated costing naming two items whose closure
changed what they were), `PL-DBGT` (a data-file note restating a table's count
and a test path that does not exist). `PL-036` joins as well: its list of
minimum displayed outputs has the same shape as the invariants list, and being
a member takes nothing from its recorded principle - linkage, not truth - which
this head keeps whole. Twenty-four, and the reading below says the cluster has
two halves rather than one: a **live claim that names nothing**, and a **dated
fact written in the present tense**. Nine of the twenty-four are the second,
and their repair is a date or a tense, not a link.

**Measured 2026-09-19, before recommending anything.** Sizes today: 21
bullets under "Required invariants", 17 subsections under "Required tests", 21
bullets under "Minimum displayed outputs", 7 rows in the hazard table. Three of
the four are named with a smaller count in the briefs that raised them
(eighteen, fifteen, fifteen): the counts drifted while the items waited, which
is the mechanism in miniature.

Coverage, one statement at a time - a subagent pass over `tests/` with every
match read in its body, then the three findings re-read here: of the 38
invariants and required tests, **36 have a test whose body asserts the
statement directly, 2 are held partially, 0 have no test**. None of the 21
invariants names its test; 3 of the 17 required tests name a file or a
function; the hazard table names a test on 7 rows of 7. So the annotation
pass is a lookup, not a test-writing project, and the number that would have
changed the recommendation - how often the declared-none form would be the
answer - is 0 of 38.

The two partials, and what the pass turned up on the way:

- Invariant 5 (stored amounts finite and nonnegative) is enforced by
  `require_nonnegative_finite("agent_amount_l", ...)` in every compartment's
  `__post_init__` (`core/alveolar.py:72`, `core/blood.py:46`,
  `core/tissue.py:64`, `core/circuit.py:237`) and by that guard's own unit
  test; no test reads each compartment's amount through a run. Whether a
  per-step guard plus its unit test is "held by" is the annotation pass's first
  judgment, not a defect, and it is recorded here so the pass does not re-find
  it.
- "Directional ventilation test" requires a faster approach of F_A toward F_I;
  `test_higher_ventilation_increases_early_alveolar_fraction` asserts F_A
  higher at 30 s. Filed under `invariant-test-gaps`.
- The step-refinement paragraph reports a measured gap "across the four
  reported values"; `test_step_refinement_converges` reads three. Filed there.
- Alveolar `gas_volume_l` and venous `volume_l` are guarded positive-finite,
  and no compartment-level test asserts either rejection. Filed there.

Three findings from reading 38 statements against their tests is the case for
the convention stated as a count: nothing else had surfaced them.

**Recommendation, 2026-09-19 - a session's, for the project owner to ratify.**
Adopt it, in four clauses, and the clauses are the whole of what is being
decided.

1. **A live assertion names what it asserts.** In `docs/MODEL.md` and
   `README.md`, a sentence asserting a fact about the tree - that a test holds
   an invariant, that a field exists, that a value is N, that a job runs X -
   names the entity in a form the tree resolves: a code-spanned test, path,
   symbol or field, or a `<!-- provenance: -->` marker over a restated number.
   `check_named_tests`, `check_citations`, `check_prose_provenance` and
   `check_make_targets` already resolve every one of those forms; this states
   the author's obligation to use them rather than the checker's reach.
2. **An enumerated family is held complete.** Where a heading promises one
   assertion per member - the invariants list, the required-tests subsections,
   the displayed-outputs list, the hazard table, a frozen gate list, a marked
   enumeration - every member names its entity or carries the declared-none
   form, and `doc_check` fails a member that does neither. This is the hazard
   table's own sentence, *"Every row names the test that holds it, or says
   plainly that it has none"*, extended to every such family in the two bound
   documents, plus the half the table lacks: a fixed form for "none", so that
   a forgotten link and a declared absence are distinguishable by a script.
3. **The declared-none form names the item that owes the link** - `held by no
   test yet (`PL-XXXX`)` - resolvable against the store, which `doc_check`
   already reads. An exemption is then a forward reference to work rather than
   a permanent hole, and closing the named item without adding the link fails
   the check. The tail's exact wording belongs to the annotation pass; the
   rule is a code span of the right kind, or this form naming an open item.
4. **A dated statement is a record, held to its date and never to the tree.**
   A sentence carrying a date, sitting under a dated heading, or inside a
   shipped release's section asserts what was true then. It is not linked, not
   checked, and not edited to carry a later fact; a later fact is appended
   with its own date. `check_gate_counts` states the same line from the other
   side - *"'frozen ... at seventeen entries', a dated fact that must never
   change"* - and this makes it the author's rule as well as the checker's.

And one rule for counts, which both halves meet: a count in prose is stated
only where a check holds it to what it counts - a group heading over its
entries, a marker over a data value - or it is dated. Otherwise the rule is
stated without the number, or the number is read from the tool that prints it,
which is the project owner's `PL-9LXK` decision (2026-09-13) applied beyond
data-file rows.

**Which documents.** `docs/MODEL.md` and `README.md` are bound by all four
clauses: they are the specialist-standard documents and the ones a reader of
a displayed value trusts. `ROADMAP.md`'s frozen lists are already families
(clause 2, through `check_gate_counts` and `_declined_ids`), and its prose is
under clause 4. `docs/ARCHITECTURE.md`'s package map is already a family, and
a marked enumeration (`PL-5N7T`) joins the table. `docs/WORKING_NOTES.md` is
records by construction - every thread is dated - so clause 4 governs it and
nothing else does. Apparatus prose (`.claude/`, `docs/resident-instructions.md`,
`CONTRIBUTING.md`) is not bound; the counts rule is advice there, which is what
`PL-T9XJ` and `PL-LM8P` already propose for themselves.

**What an assertion that names nothing looks like.** Inside a bound family:
the declared-none form, or the check fails. Outside one, in a bound document:
a number without a marker or a claim without a code span is the close-out
sweep's, by decision rather than by oversight, and `doc_check.py candidates`
prints it when its subject changes. Anywhere: dated, and it is a record.

**The check, in one paragraph - built only on ratification.**
`check_bound_families` reads a table of (document, heading, member shape,
entity kind) and, for each member, requires a code span of that kind or the
declared-none form naming an open item; resolving the span stays with the
checks that already do it. It is introduced over the hazard table, which
conforms today, so it lands green; each annotation pass adds its family to
the table as it lands, so the check never holds `make check` red for work
not yet done. Standard library only and no import of the package, as the
tool's docstring requires.

**What it costs, and why this is the owner's to ratify.** The visible cost is
on `docs/MODEL.md`'s page: 21 invariants and 17 test subsections each gain a
short tail naming a test, as the hazard table's "Held by" column already
does - one code span per statement. That is the one thing this recommendation
cannot measure, because it is a judgment about the document's human reader,
and it is why the answer is put here rather than adopted. The sibling decision
in this cluster (`PL-9LXK`) was the owner's for the same reason.

**Why adopt rather than refuse.** The safety standard first: a `must` in the
specification with no link to what holds it is the silent-wrong-answer shape,
and the pass found two partially-held statements out of 38 that nothing else
had surfaced. Then the established practice for software of this kind, read
before this was written: IEC 62304 requires the software development plan to
carry traceability between system requirements, software requirements,
software system tests and risk control measures (§ 5.1.1); the FDA's *General
Principles of Software Validation* (2002) names traceability analysis among
the validation tasks (§ 5.2.2, § 5.2.3); the requirements-traceability
literature dates the problem to Gotel and Finkelstein, *An analysis of the
requirements traceability problem*, ICRE 1994, pp. 94-101; and binding
documentation to the artifacts it describes so that drift is detected
mechanically is the whole of Martraire, *Living Documentation*, Addison-Wesley
2019. Then the project's own precedent: the hazard table already does it,
`check_named_tests` was built as "the cheap half of `PL-8LDF`", and `CLAUDE.md`
gives standing approval to putting the decidable part in code.

**What each member becomes on ratification.** The head's own work is the
clauses, the check over the hazard table, and this table applied; nothing
below closes on the day.

| Member | Half | On ratification |
| --- | --- | --- |
| `PL-8LDF` | family | the annotation pass for "Required invariants"; its check half is `check_named_tests` plus the family check |
| `PL-2M9N` | family | the annotation pass for "Required tests"; its open "error or advisory" question is answered - error, on a bound family |
| `PL-036` | family | the annotation pass for "Minimum displayed outputs", mechanism unchanged; the head's first instance rather than its statement |
| `PL-41YP` | family, second link | unchanged: the test carrying the field-to-widget link; reads `PL-NWTM`'s declaration once it exists |
| `PL-NWTM` | family, strongest form | unchanged, blocked on `PL-1FT6`: the family becomes a code declaration the document is held to |
| `PL-5N7T` | family, marked | unchanged: its marker design is clause 2 in `docs/ARCHITECTURE.md`; joins the table |
| `PL-GTSL` | family, tree-enumerated | re-scoped: the inventory of checks is held complete against `def check_*`; the prose stays judgment |
| `PL-GQWP` | live claim, README | unchanged: its option 1 (a test holding the README sentence to the constant) is clause 1 by test; option 2 is a marker |
| `PL-DBGT` | live claim, data-file note | re-scoped: `check_citations` reaches `sources` notes; the count is dropped, per the counts rule |
| `PL-9LXK` | counts, data rows | unchanged; owner-decided; the counts rule cites it |
| `PL-4RHP` | counts | confirmed: the heading states no count - triage's choice is the rule |
| `PL-T9XJ` | counts, apparatus | unchanged one-off: name the three files, state no count |
| `PL-LM8P` | counts, apparatus | unchanged one-off: drop the figures; the sentence is still present on 2026-09-19, so this is not a drop |
| `PL-B5LB` | live description | unchanged one-off: describe the tool without enumerating what the tree enumerates |
| `PL-DHJ7` | both halves | its decision is made: decidable counts are checked, judgment counts are dated; `needs-decision` becomes `ready` |
| `PL-B8V1` | record | its decision is made: date the claim in place; `needs-decision` becomes `ready` |
| `PL-NLP4` | record | follows `PL-B8V1` |
| `PL-FV7G` | record | confirmed: past-tense the clause |
| `PL-C25K` | record | confirmed: separate the two ids and read `PL-J786`'s reason; a release section is dated by its version |
| `PL-N32Y` | record, frozen scope | its decision is made: annotate with a dated note, never rewrite the scope line; `needs-decision` becomes `ready` |
| `PL-0VFF` | family, frozen list | re-scoped: closed entries carry their release, a record fact; the open count is *not* stated - `bin/docket wave` prints it |
| `PL-BHJW` | record | corrected as history: `PL-D551` closed 2026-09-05, the day the note is dated, so the note names both the job and its fold |
| `PL-C7XV` | record edited later | confirmed: one placement per dated entry; the 2026-09-16 move gets its own dated sentence |
| `PL-0R06` | record | re-scoped: append a dated note naming `PL-YVHK` rather than rewriting the 2026-09-08 costing |

**Done in this session, and not.** Done, because none of it depends on the
answer: the membership confirmed and the field widened to twenty-four; the
four families measured and the two partials named; the case above; three
findings filed under `invariant-test-gaps`; `check_named_tests`'s docstring no
longer states the drifted count. Not done, because each depends on it: the
four clauses written into `docs/MODEL.md` and the tool's docstring;
`check_bound_families`; the member re-pointing; the three annotation passes
re-scoped.
