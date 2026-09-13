---
id: PL-L9FC
title: README's validation paragraph states only the wash-in half, so a reader takes a passing validation for the whole of what the Yasuda comparison found
priority: P2
effort: S
status: ready
classes: docs
feature: project-introduction
touches: README.md
added: 2026-09-07
verify: python3 tools/doc_check.py check && grep -qF 'F_{A0}' README.md
---

**Problem.** README's validation paragraph states only the wash-in half, so a reader takes a passing validation for the whole of what the Yasuda comparison found

`README.md`'s validation paragraph (around line 160) says that
`tests/reference/test_published_wash_in_and_elimination.py` compares each agent's
$F_A/F_I$ at 30 minutes against Yasuda et al. and that all three land inside
the measured spread, then gives two of the module's four caveats. That was the
whole of the module when the paragraph was written. The module now compares two
directions on the same volunteers, and the second one does not agree: the
5-minute elimination ratio misses every cohort by +1.1 to +5.1 published SD in
the shipped rebreathing condition, and `PL-W21J` added a test-only open-circuit
driver under which three of the four cohorts come inside the spread and
desflurane crosses to 2.33 SD on the other side.

So the README states a validation result and omits the direction that
disagrees. Nothing in it is false, which is why this is a capture rather than a
defect: a reader who stops at the README takes "all three land inside the
measured spread" for the whole of what the comparison found, and the module's
own rule - that the breathing-system caveat belongs beside any statement of the
elimination result wherever it is restated - has nowhere to attach in the one
document most readers open.

The work is a judgment about README voice rather than a fact to transcribe.
`PL-N092` rewrote this file specifically to stop it descending into detail that
belongs in `docs/MODEL.md`, so the answer is probably one or two sentences
naming the second direction and its disagreement, with the numbers left in
`docs/MODEL.md` § "Published wash-in and elimination validation test" - not the four-row table.

**Why it matters.** The README states a validation result and omits the
direction that disagrees. Nothing in it is false, which is why this is a capture
rather than a defect - but a reader who stops at the README takes "all three
land inside the measured spread" for the whole of what the Yasuda comparison
found, when the module now compares two directions on the same volunteers and
the second one misses every cohort by +1.1 to +5.1 published SD in the shipped
rebreathing condition.

The module's own rule - that the breathing-system caveat belongs beside any
statement of the elimination result wherever it is restated - has nowhere to
attach in the one document most readers open. For a simulator whose README is
its front door, an over-clean validation claim is the claim most likely to be
repeated by somebody who read nothing else.

**Done when.** `README.md`'s validation paragraph names the second direction and
that it disagrees, in one or two sentences, with the numbers left in
`docs/MODEL.md` § "Published wash-in and elimination validation test" - not the four-row table,
per `PL-N092`'s rewrite of this file's voice.

**`verify:` rewritten 2026-09-13, because it started passing without the
work.** It was `python3 tools/doc_check.py check && grep -qi 'elimination'
README.md`, and `PL-B9VL` renamed the module this paragraph cites to
`test_published_wash_in_and_elimination.py` - so the case-insensitive grep now
matches the *filename* in the citation while the paragraph still states only
the wash-in half. `docket check --verify` caught it on the same branch, which is
the mechanism working: a command that proves nothing would have let `docket
verify` ACCEPT a branch that did none of this item's work.

It now greps for `F_{A0}`, the elimination ratio's own symbol, which appears
nowhere in `README.md` today (0 occurrences, measured) and which any honest
statement of the second direction has to name. That leaves the wording to
whoever writes it, which is the judgment this item is about, while still
failing until the direction is actually stated.
