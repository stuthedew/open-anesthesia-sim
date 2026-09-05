---
id: PL-6SBB
title: CLAUDE.md's apparatus-only standard sits three sentences from its subject and reads as a whole-repo aphorism, so a session applied polishing it past sufficient to src/
priority: P2
effort: S
status: done
classes: docs
feature: worker-instructions
touches: CLAUDE.md, .claude/rules/apparatus-standard.md
added: 2026-09-05
closed: 2026-09-05
pr: 339
verify: grep -q 'apparatus-standard.md' CLAUDE.md && grep -q 'paths:' .claude/rules/apparatus-standard.md && grep -q 'Polishing it past sufficient' .claude/rules/apparatus-standard.md
---

**Problem.** `CLAUDE.md` § "Two standards, deliberately unequal" is one
paragraph carrying both halves of the split. The apparatus half ends:

> It is scaffolding, not product; nobody evaluating this project will read it.
> Polishing it past sufficient is the most common way this project wastes a
> session.

The subject of both sentences is "the workflow apparatus", named three
sentences earlier. Read alone — which is how a sentence is recalled rather than
re-read — the second is a whole-repo aphorism: it names *this project* and
wastes *a session*, with nothing in it scoped to anything. On 2026-09-05 a
session quoted it as the standard for comment density in `src/`, which is the
half `CLAUDE.md` holds to the opposite standard in the same paragraph. The
project owner caught it: "That is for docket."

**Why it matters.** This is a wrong answer that arrives silently. The sentence
is true, resident, and quotable, so a session applying it out of scope is
confident and cites the right file; nothing in a diff or a check can show that
the scope was dropped. Applied to `src/` it argues for less than the specialist
standard, which is the direction that costs the simulator.

**The inventory, and a better diagnosis.** Two more claims in this file have the
same defect, and one points the other way — so this is not a one-sentence slip:

- **Line 23.** "internal quality that a one-year project could rationally trade
  for speed is worth paying for here" — no scope, in the opening section, *374
  lines before* the paragraph that scopes it. This is the mirror image: a
  session in `tools/` or `subprojects/docket/` can quote it to justify
  polishing the apparatus, which is the failure the two-standards paragraph
  exists to name. It is the likelier of the two to fire, because it sits in the
  section a session reads first.
- **Line 399.** "Recommendations should reflect the standard expected from a
  top-tier specialist in the relevant field" — the specialist bar stated with
  no scope; the scope arrives in the *next* paragraph. Quoted alone it applies
  the specialist standard to the apparatus.

The pattern is not the distance from a pronoun to its antecedent, which is how
this item first described it. In all three cases **the standard is stated first
and the scope arrives later** — one sentence later, two sentences later, 374
lines later. A reader who stops at the claim has a complete-sounding rule and no
scope, and stopping at the claim is the normal case.

That sharpens the fix. Reordering so scope precedes claim would work but has to
be got right in three places and in every sentence added afterwards. Routing
fixes all three at once and needs no ongoing discipline: a session that never
opens an apparatus file never loads the apparatus standard, whatever order its
sentences are in.

**A minimal disambiguation landed with this capture** — the two sentences now
name the apparatus instead of saying "it", and the second says what it does not
cover. That stops the specific misreading. It does not stop the class.

**Where — the real fix, to decide.** Route the apparatus half out of the
resident file into a `.claude/rules/*.md` scoped to `subprojects/docket/**`,
`tools/**`, `.claude/**` and `docs/worker.md`. A session working in `src/`
would then never load it, so the sentence could not be misapplied rather than
merely being harder to misapply — which is the difference between a wording fix
and a structural one. What stays resident is the part a session needs before
opening any file: that two standards exist, which paths are on each side, and
that the simulator wins where they compete.

Two things to weigh against it. The paragraph is one argument, and splitting it
puts the halves where neither reader sees the contrast — the contrast is much of
what makes each half land. And `.claude/` is itself on the apparatus side, so
the rule would load when a session edits the rule, which is right but reads
oddly.

Note what this is not: a check. Whether a session dropped a sentence's scope is
not answerable from the tree, and `CLAUDE.md`'s own line is that scripting the
judgment half is worse than no tool. The fix is where the sentence lives.

**Done when.** A session working only in `src/` cannot load the apparatus
standard, or — if the routing is rejected — every sentence in the paragraph
names its own subject and the decision is recorded here.

**What was done (2026-09-05, project owner approved the routing).**
`.claude/rules/apparatus-standard.md`, scoped to `subprojects/docket/**`,
`tools/**`, `.claude/**` and `docs/worker.md`, now carries the apparatus half:
what "streamlined" means, what to cut and what never to cut, scaffolding not
product, and the polishing sentence. Inside a file whose entire scope is the
apparatus, "it" is unambiguous, which is the second half of the fix.

`CLAUDE.md` keeps a four-sentence stub: both standards, the paths on each side,
that **nothing in the apparatus rule reaches the simulator**, and that the
simulator wins where they compete. The guard is stated resident, where a
session that opens no apparatus file will see it.

**Routing alone did not cover the other two, so both were scoped in place.**
The reply that proposed this said routing fixed all three at once; that was
wrong. Line 23 is a product-side claim and line 399 states the specialist bar —
neither moves when the apparatus half leaves, so each gained its scope in the
sentence: "internal quality **in the simulator**", and "Recommendations **for
the simulator** should reflect the standard expected from a top-tier
specialist".

**What it cost.** The two-standards paragraph fell from 1334 characters to 901.
`make check` reported the resident total unchanged at 548 lines, because the
paragraph is one physical line either way — which is `PL-QV1F`.
