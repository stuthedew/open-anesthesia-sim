---
id: PL-ZZ03
title: Triage classes a second copy of a fact the repository already holds as refactor, though CLAUDE.md's one-source-of-truth rule makes it a defect, and no document says when to use defect and when refactor
priority: P2
effort: S
status: done
classes: defect
feature: one-source-of-truth
milestone: v0.6.2
touches: .claude/skills/docket/modes/triage.md, docs/dead-ends.md, tools/dead_ends.py, docs/items/PL-84G1-core-circuit-py-set-circuit-volume-checks-the.md, docs/items/PL-F9TC-src-anesthesia-sim-app-re-checks-quantities.md, docs/items/PL-YHWH-core-parameters-py-restates-three-rules-that.md, docs/items/PL-M85T-three-core-class-defaults-restate-data-file.md, docs/items/PL-Q3G9-app-dashboard-frame-py-s-parameter-controls.md
added: 2026-10-24
closed: 2026-10-24
pr: 1735
payoff: a search for open defects finds every second copy of a shared fact, and each one ranks as owed work rather than as optional cleanup
verify: grep -qF 'even while the copies agree' .claude/skills/docket/modes/triage.md && grep -qF 'Working out a fact by hand where the repository already holds it' docs/dead-ends.md
---

**Problem.** Triage classes a second copy of a fact the repository already holds as refactor, though CLAUDE.md's one-source-of-truth rule makes it a defect, and no document says when to use defect and when refactor

**Why it matters.** `CLAUDE.md`'s core design principle, "A shared fact has one
source of truth", says that a second copy of a fact the repository already
holds is fixed by its shape. Its fix-in-place condition 1 counts a breach of "a
rule this repository states" as a defect. So a second copy is a defect even
while the copies agree. Triage has been classing such items `refactor`
instead, on the reasoning that no wrong answer exists yet. That ranks them as
optional cleanup, and a search for open defects does not find them.
`docket.toml`'s `known_classes` lists 14 class names, but no document says when
to use `defect` and when to use `refactor`. So nothing tells a session at the
moment it sets an item's class. The project owner raised this on 2026-10-24.

On 2026-10-24, six open `one-source-of-truth` items whose subject is a second
copy were not classed `defect`. `PL-4X5B`, `PL-84G1`, `PL-F9TC` and `PL-YHWH`
carried `refactor` alone, and `PL-M85T` and `PL-Q3G9` carried
`safety, refactor`. `PL-TSXD` and `PL-LGDV` are the same case, and their own
branches reclassify them.

**Reproduced 2026-10-24.** `grep -rnw refactor` over `.claude/skills/docket/`,
`subprojects/docket/README.md`, `ROADMAP.md` and `CLAUDE.md` finds the class
only in lists of the debt classes and in descriptions of particular items. No
line says when an item is `refactor` rather than `defect`.

**Decision.** The route is one sentence in the triage mode that classes a
second copy as a defect, together with the check that `PL-TSXD`'s branch adds
(project owner, 2026-10-24, ratified, over classing a copy `refactor` until the
copies disagree). The owner also asked for one `docs/dead-ends.md` entry
against working out a fact by hand where the repository already holds it. It
cites the three heads that this approach gave 22, 15 and 26 items, as
`bin/docket generators` counted them on 2026-10-24: `PL-PVW2`, `PL-KGYT` and
`PL-5DZ8` (project owner, 2026-10-24).

**Done when.** `.claude/skills/docket/modes/triage.md`, at the point where a
triage pass sets an item's classes, says in at most two sentences that an item
whose subject is a second copy is classed `defect`, and `safety` as well where
the safety-critical standard applies, even while the copies agree. It also says
that `refactor` is for a change of structure that no stated rule requires.
`docs/dead-ends.md` holds the one entry described above, under "Process claims
that did not survive checking". `PL-84G1`, `PL-F9TC`,
`PL-YHWH`, `PL-M85T` and `PL-Q3G9` carry `defect` in place of `refactor`.
`PL-4X5B` is left to `claude/pl-4x5b-name-layout-literals`, the branch that
claimed it on 2026-10-24.

**Room made 2026-10-24.** The owner's entry is 325 bytes. The file had emitted
3,175 bytes, 25 below the 3,200-byte nudge, and
`tests/unit/test_dead_ends.py` keeps the shipped file below that nudge. So this
item removed two entries, each in an edit of its own, as the file's preamble
asks. The coordinator chose which two. "Writing `pr` from a CI job fired by the
merge" (`PL-N5WZ`) came out because `bin/docket record` and the close-out mode
now carry that mechanism. "Raising the apparatus capture bar on the
self-generation rate" (`PL-LKGL`) came out because its refutation already loads
in every session, as the worked example in `.claude/rules/expert-review.md`. The
file now emits 3,101 bytes. The test is intended, and the prose around it was
what was missing. So the "Size warns" paragraph of `docs/dead-ends.md` and the
"Size never fails" paragraph of `tools/dead_ends.py`'s docstring now say that
the test keeps the file below the nudge, and that a session adding an entry
makes room for it in the same commit.

**Generator check.** One-off. The fact this item's readers misread is which
class a second copy of a fact takes while the copies still agree, and no head's
`misread:` states it. It is not a member of `PL-5DZ8`, whose fact is which
spelling of a repeated predicate is the answer when tools, hooks and docket
each spell it. `PL-5DZ8` closed `spent` after a sweep of `tools/`,
`.claude/hooks/` and `subprojects/docket/src/docket/`, and the five items
reclassified here are under `src/`. The wrong class created no second copy and
caused no item to be filed. It left at least eight items with the wrong
class, five of which this item corrects. So it delayed the fix of copies rather
than producing them. No closed head is re-entered, so no `reenters:` field is
owed.
