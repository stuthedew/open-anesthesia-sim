---
id: PL-KQHN
title: PL-VFD8 made v0.4.26 reserved, so ROADMAP.md's Qt-port paragraph now says both that a patch cut takes this section's number and that the guard withholds it, and the policy question was never put to the owner
priority: P2
effort: S
status: done
classes: docs, planning
feature: release-roadmap-seam
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF "deliberate act rather than the release path's default" ROADMAP.md
---

**Problem.** PL-VFD8 made v0.4.26 reserved, so ROADMAP.md's Qt-port paragraph now says both that a patch cut takes this section's number and that the guard withholds it, and the policy question was never put to the owner

**Found 2026-09-16** by the panel that triaged `PL-SYG4`, three days after
`#606` merged, and it is a correction to that session's own sweep.

**The two statements, a few lines apart in one paragraph.** `ROADMAP.md`
§ "v0.4.26 - the interface moves to Qt", under the heading "**The one risk,
recorded rather than engineered around - and it has happened once**", says a
patch cut before the port lands "takes this section's number ... It will move
again if another patch is cut before this lands - a rename each time, not a
re-scope." `#606` then appended, to that same paragraph: "The guard no longer
adds to that risk ... so a bump arriving at this section's number is withheld
and named rather than offered as free." One paragraph now records the
collision as an accepted mechanic and as something the apparatus prevents.

**The roadmap says it three times, and the project has executed it once with
approval.** Quoted rather than cited by line, because two of the three have
already moved since this was measured at `16f3ce0`. The `v0.4.x` timeline row:
"`docket release` offers the next free number to whatever is finished, so any
patch cut before the exact step lands would take it." The port's risk paragraph,
this one: "a patch cut before this lands takes this section's number."
Planned-milestone item 29: "a patch cut before this work lands takes it." And
`PL-G7RD`'s own title is
"Cut v0.4.25 from the ten finished items, **renumbering the Qt port's section to
v0.4.26 as ROADMAP.md's own risk paragraph provides for**", `P2`, owner-approved,
with `ROADMAP.md` in `touches` and the rename asserted by its `verify`.

**So `#606` answered a direction question by implication.** `PL-188T` asked for
the port's number to be reserved and cited this same risk paragraph as its
warrant, reading "records that collision as the port's one risk" as a hazard to
prevent. The paragraph reads at least as naturally as an accepted mechanic. The
fix was right on the evidence it was given and the question behind it was never
put: **does a patch cut on the `v0.4.x` track still take the port's number?**
Sessions now read a paragraph that answers both ways.

**Why it matters.** It is `.claude/rules/apparatus-standard.md`'s floor applied
to the plan rather than to a tool: what a session reads here must be true, and
this paragraph cannot be. The practical reach is narrow today - the reservation
bites only when the mechanical bump arrives at `0.4.26`, which needs a shippable
set with no feature-classed work in it - and it is not narrow in kind, because
`ROADMAP.md` is the file `CLAUDE.md` calls the authoritative version and
milestone map. A reader deciding whether to cut a patch mid-port gets opposite
instructions from one paragraph.

**Done when.** `ROADMAP.md` § "the interface moves to Qt" states one answer
rather than two, and the answer is the owner's rather than a session's; where it
is "the guard should withhold it", the risk paragraph's "takes this section's
number" sentences at lines 306, 1495 and 4043 are corrected to match, and
`PL-G7RD`'s precedent is recorded as superseded rather than left reading as
current practice; where it is "a patch still takes it", `PL-VFD8`'s reservation
of a patch-track-adjacent milestone number is narrowed and `PL-SYG4`'s fifth
candidate becomes available.

**This is the first question of `PL-SYG4`'s `Decision needed.`**, carried here
because the contradiction is in `ROADMAP.md` and outlives whichever sentence the
digest ends up printing.

**Decision needed.** Does a patch cut on the `v0.4.x` track still take the Qt
port's section number - as `ROADMAP.md` provides for in three places and
`PL-G7RD` executed once with the owner's approval - or does `PL-VFD8`'s
reservation now withhold it? One paragraph records both today. This decides what
the release train does rather than how a tool reports it, so it is the project
owner's; `CLAUDE.md` puts setting direction on their side of the division of
labour. The **Done when.** above says which sentences change under each answer.

**Decision (project owner, 2026-09-16, ratified).** The reserved-version guard
withholds the Qt port's section number. A patch cut on the `v0.4.x` track no
longer takes `v0.4.26` by default - the number is withheld and named, so a cut
at it is a **deliberate act rather than the release path's default**. Chosen
over keeping the documented mechanic, under which a patch takes the port's
number and the section is renamed each time, and narrowing `PL-VFD8`'s
reservation to match.

Marked `ratified` rather than specified because it arrived as agreement with a
session's recommendation rather than in the owner's own words. `CLAUDE.md`'s
bar to reopen it is therefore ordinary evidence - a measurement, a cost the case
did not carry, a constraint that has since appeared - rather than a compelling
argument.

**Two measurements carried it, neither available when the mechanic was written
down.**

1. **The rename is no longer cheap.** The mechanic was recorded when the
   `v0.4.25` -> `v0.4.26` move carried nothing with it. Counted 2026-09-16,
   eight sites in five files outside `ROADMAP.md` name `v0.4.26`: three in
   `tools/import_boundary_check.py` (two inside error messages a developer
   reads), two in `docs/ARCHITECTURE.md`, and one each in
   `subprojects/docket/src/docket/roadmap.py`, `.claude/skills/docket/SKILL.md`
   and `subprojects/docket/README.md`. Four carry the section-citation form
   `tools/doc_check.py` validates; four name the number bare, where no check
   reads it. The cost rises as the port lands rather than staying flat.
2. **A cut at the port's number silently reverses a decision of record.**
   `PL-Y1L0` measured it: `wave` builds its unreleased set as `section.version
   > current`, so a cut at `0.4.26` *or* `0.4.27` drops the port's section out
   of the plan and moves the beat to v0.5.0 - reversing `PL-RKWB`, the owner's
   2026-09-14 decision to put the port ahead of v0.5.0 - and
   `outstanding_roadmap_edits` returns a byte-identical list at all three
   numbers, so nothing reports it.

**What this supersedes.** `PL-G7RD` cut `v0.4.25` on 2026-09-14 and renumbered
this section to `v0.4.26` with the owner's approval, as the roadmap then
provided for. That execution stands as what happened; it stops being current
practice. A cut at a reserved number is now taken deliberately, with the rename
above as its named cost, rather than arriving as the release path's next free
number.

**What this does not change.** Ordinary patch numbering on the `v0.4.x` track
is untouched: the track still promises no particular patch number, and a cut
still takes the next number that is genuinely free. What changed is what "free"
means - a number the roadmap has given to a milestone section ahead of the
current one is not free, which is exactly what `#606` taught the guard.

**Provenance of the recommendation, recorded because it was reconstructed.**
The recommendation came from the `doc_check` safety-class gate advisory session
(`session_01G4NBvRm2Cbq1UW5BEQjwBL`), whose branch
`claude/doc-check-safety-gate-advisory-gmspbu` was deleted when `#636` merged
and whose reply text is therefore gone. No cross-session channel reached it.
The recommendation was read from that session's own closing-block line -
*"decide `PL-KQHN`: withhold number + fix prose or keep mechanism"* - where the
recommended option is the one carrying its consequence and the alternative is
named in shorthand, and it agrees with the two measurements above, with the
direction `#606` had already moved the apparatus, and with this brief's own
`Done when.`, which states the withhold branch first and in more detail.

**What to change, site by site.** Line numbers are against `ROADMAP.md` at
`0ba9aa4`; the risk paragraph moves under `#639`, which rewrites it.

1. **Line 306, the `v0.4.x` timeline row's closing sentence** - *"`docket
   release` offers the next free number to whatever is finished, so any patch
   cut before the exact step lands would take it."* Narrow rather than reverse:
   a number the roadmap has reserved for a milestone section ahead of the
   current one is not free, and the guard withholds it.
2. **The port's risk paragraph, § "v0.4.26 - the interface moves to Qt"**
   (line 1515 here; rewritten by `#639` into three paragraphs, the last of
   which marks the question open). Replace that last paragraph with the
   decision above. It must contain the phrase **`deliberate act rather than the
   release path's default`** verbatim, which is what this item's `verify:`
   command greps for.
3. **Line 3426, the `### Declined to Gate 2 ...` entry for this item** -
   currently *"it waits on an answer rather than on attention"*. The answer
   exists; the entry becomes the recorded decision, or the item leaves the
   subsection when it closes. Do not touch the subsection's heading count:
   `PL-4RHP` holds that it is unchecked and wrong by other means.
4. **Line ~4750, planned-milestone item 29's version note** - *"a patch cut
   before this work lands takes it"*. Same narrowing as site 1.

**Sequencing, recorded because the decision and the prose landed in two
commits.** `#639` (`claude/awesome-heisenberg-gp7ev6`) was open and rewriting
the risk paragraph at site 2 from `main`'s older text when the decision arrived,
so editing the same lines would have conflicted at merge and discarded that
branch's green run on content it had already proved. The decision was committed
on its own first, so that it survived whichever session landed the edit; `#639`
merged as `4690412` minutes later and the four sites were then corrected on top
of it in this same branch. Both commits are here.
