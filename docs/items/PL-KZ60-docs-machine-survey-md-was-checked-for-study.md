---
id: PL-KZ60
title: docs/machine-survey.md was checked for study-protocol-read-as-practice in section (a2) only, and one of that section's three sources did not support the claim it was cited for
priority: P2
effort: M
status: ready
classes: docs
feature: anesthesia-machine
touches: docs/machine-survey.md
added: 2026-09-20
payoff: stops the machine survey passing unchecked source claims into docs/MODEL.md and the machine abstraction, the route by which section (a2) put a wrong statement about clinical practice behind the simulator's opening fresh gas flow
verify: grep -qF 'Every claim in this document has been checked against the depth its source was read at' docs/machine-survey.md
not-delegable: The deliverable is a per-claim judgment about what a paper establishes against the depth it was read at - the distinction that failed in section (a2), where two protocol ranges read as reports of practice. It needs full-text retrieval through the PubMed MCP server and the private reference corpus, and the verify: pins only the sentence recording the conclusion, never whether the reading behind it happened.
---

**Problem.** docs/machine-survey.md was checked for study-protocol-read-as-practice in section (a2) only, and one of that section's three sources did not support the claim it was cited for

Found while closing `PL-NM7X` (the fresh gas flow default), 2026-09-20.

**What was checked, and what it turned up.** `PL-NM7X` commissioned full-text
confirmation of the three sources `docs/machine-survey.md` § "(a2)" cited for
the claim that *"4 L/min is at the high end of contemporary practice rather than
the middle of it"*. Of the three:

- **Kalmar et al.** (PMID 34978655) supports a narrower claim than the one made
  — it is a recommendation, and its 2 L/min comparator is the practice fact.
- **Candries et al.** (PMID 35318567) does not support it. Its 0.2–6 L/min is a
  Gas Man validation study's protocol range.
- **Hoffmann et al.** (PMID 40073301) does not support it and reads the other
  way: an *in vitro* bench protocol whose range contains 4, 5 and 6 L/min,
  settings that paper describes as reflecting clinical conditions.

So one section of the survey, checked once, was resting on one source out of
three. § "(a2)" is now corrected.

**Why that is a finding about the rest of the document rather than a closed
one.** The failure mode is specific and repeatable: reading *a study's chosen
settings* as *a report of practice*. It is the error
`src/anesthesia_sim/data/machines/reference_circle_system.json`'s De Wolf entry
already exists to forestall for its 1 L/min, which is evidence that the project
has met it before. The survey has roughly thirty references across fourteen
buckets, most read at abstract level in one 2026-09-19 session, and **no other
bucket has been checked this way**. Hoffmann et al. is itself cited twice in the
document for two different purposes, which is the shape that makes the slip easy
to make.

**Why it matters.** The survey is a design input: `PL-FG9D`'s machine
abstraction and `docs/machine-abstraction.md` were decided against it, and
`docs/MODEL.md` now cites it. A claim it carries can reach the specification,
which is exactly the route the § "(a2)" sentence took.

**Done when.** Each of the survey's quantitative or normative claims has been
checked against what its cited source actually establishes, at the depth the
claim needs; every entry records its route and depth per
`.claude/rules/citing-sources.md`; and anything a source does not support is
either withdrawn with the withdrawal recorded, or re-sourced. Scope is
`docs/machine-survey.md` alone — the agent and patient data files were audited
separately under `PL-FN5F` and `PL-QBKQ`.

**Not urgent, and not a generator.** It is one bounded audit of one document, it
causes no other open item, and nothing in the simulator computes from the survey
today.

**What triage checked, 2026-09-20** (`PL-028T`). The finding holds, and one
clause of **Done when.** above is narrower than it reads. Measured against
`docs/machine-survey.md` as it now stands - 803 lines, 23 source entries, 13
variable buckets (a1, a2, b1-b11) plus § "Ruled out":

- **Route and depth are already recorded for 17 of the 23 entries**, so that
  clause is mostly met rather than outstanding. Six carry no depth statement:
  the `ISO 80601-2-13:2022` and `ISO 5360:2016` entries, which § "How a value
  gets into this document" rule 4 exempts by naming standards to number and
  edition only, and four articles that are not exempt - Bashraheel et al.,
  Jakobsson et al., Leijonhufvud et al., Zumsande et al. § "Sources" asserts
  that "The depth of reading is stated on each entry", which is false for those
  four.
- **The depth vocabulary is inconsistent** - "Full text read" and "Read at full
  text" are both in use for the same thing - so a count of one phrasing alone
  undercounts. It cost this triage pass one wrong count before the second
  phrasing was noticed, and it will cost the audit the same.
- **The live clause is depth *adequacy*, not depth recording.** Twelve of the 23
  entries are "Abstract read", and the § "(a2)" failure was exactly an
  abstract-level read: an abstract carries a study's protocol range and not the
  reason the range was chosen, so a protocol reads as a report of practice.
  Kalmar et al. - the one source § "(a2)" still rests on after the other two
  were withdrawn - was upgraded to full text on 2026-09-20 for `PL-NM7X`, and no
  other bucket has had that treatment. So the question to ask per claim is
  whether the depth its source was read at can carry the claim it is cited for,
  and full text is fetched where it cannot.

**The sentence the `verify:` greps for.** The pass records its conclusion in
§ "How a value gets into this document" as: `Every claim in this document has
been checked against the depth its source was read at`. Named here so it is not
guessed at - the command pins that string and nothing else in the tree produces
it.

**Why this is classed `docs` and not `science`, and what would reopen it**
(`PL-028T`, 2026-09-20). Triage set `science`/`P1` first, on the precedent of
`PL-FN5F` and `PL-QBKQ` - the two prior "a cited source does not support the
claim it was cited for" audits, both `science, docs` at `P1`. That was changed,
for two reasons:

- **The closer precedent is `PL-4DCG`**, which wrote this same document with
  these same claims at these same reading depths, and was classed `docs` at
  `P2`. `PL-FN5F` and `PL-QBKQ` differ in the thing that matters: they touch
  `src/anesthesia_sim/data/` and `docs/MODEL.md`, files a displayed clinical
  value is computed from. This touches a design-input document that nothing
  computes from, and the adoption step between it and a displayed value is
  itself governed - `docs/MODEL.md` § "Source hierarchy", the `tier` and
  `adopted` fields, and `.claude/rules/citing-sources.md`. `PL-NM7X` is that
  guard working: the § "(a2)" claim was caught at adoption, by an item that was
  `science`/`P1` because *it* reached the data file.
- **`science` would have moved the v0.5.0 gate.** A `science`-classed item
  re-enters the current gate regardless of presence, so `tools/doc_check.py`
  required it on the frozen list or in `Required scope` - a 176th entry at the
  moment the beat reports the gate two promotions from clear. Worth recording
  that the underlying freeze rule points the other way independently: the gate
  froze 2026-09-06 and `docs/machine-survey.md` was first committed 2026-09-19
  (`PL-4DCG`, `#742`), so the problem is new rather than present-at-freeze and
  defers to the next gate on ROADMAP.md § "The debt gate"'s own terms.

**What would reopen it.** A claim in this survey being adopted into
`docs/MODEL.md` or a data file *without* an adopting item of its own to catch
it, or the project owner deciding that a design-input document's sourcing is
inside the safety-critical standard's reach. Either makes `science`/`P1`
correct and puts this on a gate.

**A second session drew the same line independently, 2026-09-20.** Pull request
#759 and #757 were written in the same hour without sight of each other. #757
triages the other 22 captures and proposes moving v0.5.0's frozen list from 175
to 178, adding three entries under the unconditional safety/science exception -
`PL-D126` and `PL-WJNS`, both `science, docs` at `P1`, and `PL-0RZ0`, `safety`
at `P1`. **All three declare `docs/MODEL.md` or `src/` in `touches`**, and the
two `science` ones are findings from this same machine survey that reach the
model specification. This item declares `docs/machine-survey.md` alone. So the
boundary both passes landed on is the same one: a survey finding that reaches a
computed path is `science`/`P1` and goes on the gate, and the survey document's
own sourcing is not. Stated as what #757 proposes rather than as settled fact,
since those three are still untriaged on the default branch.
