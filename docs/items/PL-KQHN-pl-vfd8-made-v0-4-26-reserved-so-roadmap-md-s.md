---
id: PL-KQHN
title: PL-VFD8 made v0.4.26 reserved, so ROADMAP.md's Qt-port paragraph now says both that a patch cut takes this section's number and that the guard withholds it, and the policy question was never put to the owner
status: untriaged
added: 2026-09-16
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
approval.** Line 306 (the `v0.4.x` row): "`docket release` offers the next free
number to whatever is finished, so any patch cut before the exact step lands
would take it." Line 1495 (this paragraph). Line 4043 (planned-milestone item
29): "a patch cut before this work lands takes it." And `PL-G7RD`'s own title is
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
