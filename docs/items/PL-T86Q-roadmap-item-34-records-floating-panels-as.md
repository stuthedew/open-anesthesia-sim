---
id: PL-T86Q
title: ROADMAP item 34 records floating panels as permanently not admitted, which is a hard never the project owner did not take - they asked for tiled first with floating kept open as a later option, and the real constraint is on silent occlusion of a required value rather than on floating
priority: P2
effort: S
status: done
classes: planning, docs
touches: ROADMAP.md, docs/items/
added: 2026-09-15
closed: 2026-09-15
pr: 601
verify: python3 tools/doc_check.py check && grep -qF 'What is refused is silent occlusion, not floating' ROADMAP.md
---

**Problem.** ROADMAP item 34 records floating panels as permanently not admitted, which is a hard never the project owner did not take - they asked for tiled first with floating kept open as a later option, and the real constraint is on silent occlusion of a required value rather than on floating

**What was wrong.** `PL-4D1M` recorded the project owner's 2026-09-15 window
decision into item 34, and wrote of floating panels overlapping the tiled areas
within a window that they "are a different mechanism and are not admitted".
That is a permanent refusal. What the owner said was "I don't want to make a
hard decision to never do floating windows" - tiled only at first is fine, and
the option to take a tiled window out into a floating one is wanted later. The
session wrote a never where the owner had asked for a not-yet, which is the
single most consequential way a roadmap statement can misrepresent a decision:
a refusal recorded in `ROADMAP.md` is what a later session cites to refuse the
feature.

**Why it happened, since the mechanism generalises.** The safety argument for
tiling is sound and the session let it travel one step too far. "A panel
drawn over the dashboard can cover a required value silently" supports a
constraint on *occlusion*; it does not support a constraint on *floating*, and
the session recorded the second because the second was the mechanism in front
of it. A safety argument licenses the narrowest rule that removes the hazard,
never the widest rule the hazard could motivate.

**The fix, and it is better than the sentence it replaces.** Item 34 now says
floating is deliberately not foreclosed, that tiled-first is sequencing rather
than a rule, and that what is refused is **silent occlusion of a required
value** - stated once, on the display, rather than per window type. That one
rule covers the in-window floating panel and the broken-out window dragged back
over the main one, which the old wording had to argue separately and got
different answers for. `PL-WLWY` is named as where it is settled, and was
extended to cover the in-window case so item 34's pointer is true.

**Done when.** Item 34 records floating as a later option rather than a
refusal, and the constraint it is subject to is stated as a property of the
display. Closed 2026-09-15 with the edit in the same commit.
