---
id: PL-9J2W
title: CLAUDE.md warns three times that the apparatus may become the work and never states when investing in it is correct, so every session re-derives a too-much-tooling critique the owner then answers by hand
status: done
priority: P2
effort: S
classes: docs, session-cost
feature: planning-cadence
touches: CLAUDE.md, docs/resident-instructions.md
verify: python3 tools/doc_check.py check && grep -q 'not judged by its share of the queue' CLAUDE.md
added: 2026-09-05
closed: 2026-09-05
---

**Problem.** `apparatus` appeared in `CLAUDE.md` three times and every one was a
warning or a demotion: it "is at permanent risk of becoming the work instead"
(§ "What this project is"); it is held to "a lower and different bar" and "where
the two compete for a session, the simulator wins" (§ "Proactive expert review
and domain best practices"). `.claude/rules/apparatus-standard.md` adds that
polishing it "is the most common way this project wastes a session". The single
sentence in the file that argues for paying for internal quality is scoped away
from the apparatus by its own words - "internal quality **in the simulator** is
worth paying for".

So a session that computed the product/apparatus ratio had three warnings and no
counterweight. It reliably concluded the project was overinvesting in tooling
and said so.

**Why it matters.** The project owner reports this happening in nearly every
review session: the session says too much effort is going into apparatus and the
work belongs on the product, he replies that this is a solo hobby project on a
multi-year horizon that must not become unmanageable and that he needs help
managing it, and the session concedes. The concession is never written down, so
the next session re-derives the same objection from the same asymmetry.

That is `CLAUDE.md`'s own compounding-friction test met on the second limb - the
finding "is being routed around", and the routing-around is the owner
re-explaining by hand. It is not a wrong answer silently given; it is a right
answer the owner has to supply, repeatedly, at his own cost.

**Why the priors were already there and did not reach.** § "What this project
is" already states the horizon, the absence of a deadline, and that the failure
being guarded against is "years of effort abandoned when the codebase becomes
unmanageable, not a feature shipping late". A session reading that still reached
the opposite conclusion, because nothing connected the horizon to the *apparatus*
specifically, and three sentences pointed the other way. This is the shape
`PL-WWDT` found for the expert-review standard - the text was present and the
moment still went unserved - with the difference that here the sentence that
needed writing did not exist at all.

**Where.** `CLAUDE.md` § "What this project is", closing paragraph;
`docs/resident-instructions.md` § "What stays resident, and on what argument",
under the group that already covers this section.

**Approach.** Write the *test*, not a defence. The general objection is
foreclosed and the specific one is preserved: an objection to the balance is a
finding when it names the mechanism that should not have been built and what it
cost. This matters because the ratio may genuinely be wrong - `dev-tooling` is
the largest feature in the queue by a wide margin - and a paragraph that
immunised the project against hearing so would be worse than the recurring
argument it replaces.

**Alternative considered and refused.** Putting the counterweight only in
`docs/consultant-brief.md`, at zero resident cost. Refused because the owner
reports the critique arriving in ordinary working sessions too, and a document
pasted into consultant sessions cannot reach those - it would fix the one place
he already has a workaround and no others.

**Done when.** `CLAUDE.md` § "What this project is" states that the apparatus is
not judged by its share of the queue and gives the test an objection must meet,
`docs/resident-instructions.md` records the argument, and the "permanent risk"
sentence still stands unweakened.

**Worked.** Both edits made. Resident total rose, which is the expected
direction here and is reported by `doc_check` against `origin/main`. The two
sentences were read together afterwards to confirm they do not contradict: the
risk of the apparatus becoming the work is unchanged, and what the new paragraph
rejects is *share of the queue* as the instrument for detecting it.
