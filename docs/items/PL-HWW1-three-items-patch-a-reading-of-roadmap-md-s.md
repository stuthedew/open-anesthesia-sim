---
id: PL-HWW1
title: Three items patch a reading of ROADMAP.md's Required scope because membership is cited rather than declared: make the declaration the record
priority: P2
effort: M
status: ready
classes: defect, infra
feature: generator-heads
touches: subprojects/docket/src/docket/roadmap.py, tools/doc_check.py, ROADMAP.md, docs/items
added: 2026-09-17
verify: uv run pytest subprojects/docket/tests/test_roadmap.py && grep -q 'def test_required_scope_places_only_declared_ids' subprojects/docket/tests/test_roadmap.py
root-cause-of: PL-4PC5, PL-6P9Y, PL-C4RS
---

**Problem.** A milestone's `### Required scope` has no grammar. An id is a
member of that scope because it is *written under the heading*, so a
provenance citation inside an entry's prose becomes a member of the release,
and the one heading that does have a grammar - `### Explicitly out of scope
for vX.Y.Z`, whose whole meaning is exclusion - is parsed into
`MilestoneSection.excluded_ids` and then not consulted. Membership is read
rather than recorded, and three open items correct one reading each.

**Why it matters.** This is `PL-6ZQY`'s mechanism - *the apparatus infers a
fact it could have recorded* - in the document the `docket` skill tells every
session to read **before** the queue. `bin/docket wave` is that read, and it is
wrong in both directions: it counts ids cited in an entry's prose as scope
entries, so v0.5.0's `Required scope` parses at 26 ids against the section's
own stated twenty (`PL-4PC5`), while a milestone's `### Explicitly out of
scope` list is read as silence, so an id the roadmap has explicitly ruled out
ranks ahead of work nobody has ruled on (`PL-6P9Y`).

The self-generating half is what makes it a generator rather than a bug.
Naming the id that changed an entry, in the prose around that entry, is how
this document is written throughout and is load-bearing provenance. Following
that idiom creates a new false scope entry every time somebody re-briefs an
entry, so the count drifts as the document is maintained *correctly*, and each
drift is found and filed separately.

## Narrowed 2026-09-19 from eight members to three, on a measurement

The 2026-09-18 list held eight. Four of them - `PL-Y1L0`, `PL-J45M`,
`PL-7CSP`, `PL-B5DW` - are a different mechanism and are now `PL-2T03`'s:
they re-derive the release train's **arrangement** by comparing version
numbers, where § "The timeline" is already a parsed, grammar-checked table
whose row order *is* the arrangement. That is *re-derives a fact it already
has*, not *infers a fact it could have recorded*, and neither decision
constrains the other. `PL-SVRW` (two spellings of the leading-id grammar) was
dropped from the list outright: it is a consolidation that survives either
answer here, and it stays an ordinary `dev-tooling` item.

What is left is membership, which is the question the title asks.

## The measurement, 2026-09-19

**How far the over-read reaches.** Parsing each `Required scope` entry's
*head* instead of the whole subsection drops 9 ids across the two unreleased
scoped milestones - 6 in v0.5.0 (`PL-011`, `PL-5328`, `PL-ZMRT`, `PL-2R2C`,
`PL-HLD5`, `PL-GVXP`) and 3 in v0.6.0 (`PL-HJPY`, `PL-3J2P`, `PL-C842`). The
resulting counts are 20 and 22, and those sections state "Twenty items" and
carry 19 entries declaring 22 ids. So the stated sizes and the parsed sizes
agree once the citations stop counting.

**And the number that decides it.** A narrower *parse* is right only if what
it suppresses does not matter. Eight of the nine are `done` or `dropped`: they
inflate a progress figure and nothing else. **The ninth, `PL-HJPY`, is open
and `blocked`**, and v0.6.0's Required-scope entry 1 names it as what settles
a property that entry requires - what owns the window set, which the serialized
root must have from version 1 or become a schema migration against files a
learner has saved. `bin/docket show PL-HJPY` reports `placed by v0.6.0`
**today only because of the over-read**, and a head-slot parse would silently
make it placed by nobody.

That is the finding. The current parse says `PL-HJPY` is in scope by accident;
a tightened parse would say it is not, also by accident; and **nothing in the
document settles it either way**. Both readings are guesses about a live item,
which is the argument for recording rather than for a better grammar over
prose.

**What recording would cost, counted.** The document already uses one
declaration form - `(queue item ` + backtick-id + `)` after the entry's bold
title. Across all `Required scope` sections, 58 of 76 entries carry it. Of the
18 that do not, 16 are v0.1.0's and v0.2.0's, written before the queue existed
and naming no ids at all, which place nothing under either answer. **The two
unreleased scoped milestones are already at 39 of 39.** The real editing cost
is 2 entries in the shipped v0.4.26 section, one of which (`Required scope`
entry 8) deliberately declares six ids in a bare list and would be rewritten to
put them in the same slot.

## The decision, and the recommendation

**Decided: membership becomes a declaration in `ROADMAP.md` itself, as a slot
on each `Required scope` entry, enforced by `tools/doc_check.py`** (project
owner, 2026-09-19, **ratified** - this was a session's recommendation, chosen
over leaving the scrape in place, over a head-slot parse with no declaration
rule, and over a sidecar data file or fenced id block; `CLAUDE.md`'s lower bar
to reopen therefore applies, and the measurement below is what would have to be
answered to do it). The reasoning was put in the reply of 2026-09-19 and is
kept here because that reply is gone.

Concretely: ids
inside an entry's `(queue item[s] ...)` parenthetical are that milestone's
membership; every other id under the heading is prose and places nothing;
`doc_check` fails a declared id the store does not hold, and fails an entry
whose stated ids disagree with the section's own count. `excluded_ids` then
becomes a fourth answer from `Scope.placement`, which is `PL-6P9Y` and is one
line, because the parse already collects it.

Three reasons, in order of weight:

1. **The project already runs this pattern and it works.** § "The timeline" is
   a table with a stated grammar; `parse_timeline` returns its breaches as
   `problems` and `doc_check` fails on them. Nothing about scope needs a new
   kind of thing - only the same promotion from convention to checked rule.
2. **One statement, not two.** A sidecar data file or a fenced id block would
   duplicate what the entries already say, and the duplicate can disagree with
   the prose - which is `PL-C4RS` exactly, reproduced in a new place. A
   `milestone:` field on each item has the same defect from the other side, and
   a worse one: scoping is a single editorial act in the document a person
   reads, and the ordering ("in the order the dependencies allow") and the
   per-entry reasoning have nowhere to live in 20 item files.
3. **It costs nothing where it matters.** 39 of 39 in the two unreleased
   milestones, 2 edits in a shipped section.

**What would make this wrong, stated before the count was run:** it is wrong if
declaring membership suppresses ids that genuinely belong to the milestone. The
answer is one - `PL-HJPY` - and a declaration does not suppress it, it *asks*
about it. **That question is now answered** (project owner, 2026-09-19,
ratified - chosen over leaving it placed by the over-read): v0.6.0's
`Required scope` entry 1 reads `(queue items ` + `PL-1FT6` + ` and ` +
`PL-HJPY` + `)`, so the multi-window relation is declared scope of that
milestone rather than inferred from a citation. The edit is on this branch and
is inert under today's parser, which already counted it.

**Not recommended, and why each:** leaving the scrape (the drift is generated
by correct maintenance, so it does not stop); a head-slot parse with no
declaration rule (same arithmetic, no loud failure, and it un-places
`PL-HJPY` in silence); a sidecar file or fenced block (two statements, and
they drift).

## Why this item is the head, and no member is

Confirmed against the store on 2026-09-18 and unchanged by the 2026-09-19
narrowing. `PL-6P9Y` is the closest candidate and is too narrow by its own
brief - it adds one placement for one heading and records why it is `P3`: "it
moves exactly one id today (`PL-Z7LY`)". `PL-4PC5` attacks the other half but
its outcome is a corrected *count*, so the inference survives it. `PL-C4RS`
says the two "have to land agreeing with each other", which is the shape of a
cluster rather than of a head. Nothing in the store proposes recording
membership instead of parsing it.

## Considered and left out

The other open items naming `ROADMAP.md` are stale *statements* rather than
mis-parses - `PL-B8V1`, `PL-0VFF`, `PL-C25K`, `PL-N32Y`, `PL-FV7G` - and they
belong to `PL-4FBP`'s cluster (a document sentence whose link to the tree lives
only in the reader's head), where `PL-B8V1` is already named. The split is
worth stating: this cluster is what the tooling *reads out of* the roadmap,
that one is what the roadmap *says*.

**Done when.** `roadmap.py` reads `Required scope` membership from each
entry's declaration slot rather than from every id under the heading;
`tools/doc_check.py` fails a declared id the store does not hold and an entry
in a declaring section that declares none; `Scope.placement` answers
`out-of-scope` from the anchor's own `excluded_ids`, which is `PL-6P9Y` and is
one line the parse already supports; v0.4.26's two non-conforming entries move
their ids into the slot; `ROADMAP.md` is still readable by a person; and the
three members are closed against it or re-briefed with what is left.

**What a fresh session needs, and where.** The grammar is the existing idiom
promoted to a rule - `(queue item ` + backtick-id + `)` or
`(queue items A and B)` after an entry's bold title - and the entry unit is one
top-level list item, bullet **or** numbered, since v0.6.0's list is numbered
and v0.5.0's is bulleted. `_gate_entries` already implements that unit for the
frozen list, with `BULLET_RE` needing the numbered form added.
`_subsection_ids` and `SECTION_ID_RE` in
`subprojects/docket/src/docket/roadmap.py` are what change; `SECTION_ID_RE`'s
long comment states the current rule and is the thing to rewrite rather than
delete. The two entries needing edits are v0.4.26's `Required scope` entries 6
(`The two checks that read the theme`) and 8 (`The queued fixes named below`,
which lists six ids in its body deliberately, so `ships_with` can read them -
move them into the slot rather than dropping them). v0.1.0's and v0.2.0's
entries name no ids at all and must stay passing.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found only two with a causing item in the store (`PL-BHVM`,
`PL-L4YG`); this item was filed to record that this cluster had none. On
2026-09-18 it became the head itself rather than a tracker of one. On
2026-09-19 the membership was measured and the cluster split in two.
