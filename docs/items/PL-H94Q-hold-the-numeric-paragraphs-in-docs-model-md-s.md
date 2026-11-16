---
id: PL-H94Q
title: Hold the numeric paragraphs in docs/MODEL.md's model sections (selected method, alveolar gas, mass balance, agent amount, concentrations) to named tests
priority: P1
effort: S
status: ready
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py, tests, docs/items
blocked-by: PL-19W8
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): the paragraphs it would hold are docs/MODEL.md prose that no displayed string carries, so no learner can see a wrong value now
added: 2026-11-02
payoff: the numbers in the model sections of docs/MODEL.md are computed by a named test, so a wrong one fails the build rather than waiting for a reader
verify: grep -q 'heading="Selected method (as implemented)"' tools/doc_check.py
---

**Problem.** These `docs/MODEL.md` sections state figures with a unit in
paragraphs that carry no test, marker, source or date. Counted 2026-11-02
with `_numeric_paragraph_members`, as unheld of numeric paragraphs:

- "Selected method (as implemented)", "Alveolar gas", "Mass-balance
  identity", "Agent amount" and "Concentrations": 1 each

**Why it matters.** A figure about what the model computes that no test
computes can be wrong, or lose its condition, and nothing notices.
`PL-B6YV`'s members were seven such sentences.

**The rule.** `docs/MODEL.md` § "How this document is held to the tree"
says a computed claim names the test that computes it (`PL-B6YV`, project
owner, 2026-11-02, ratified). In a section listed in `BOUND_FAMILIES` with
`_numeric_paragraph_members`, `make check` fails each paragraph that states a
number with a unit and carries none of the accepted forms. `PL-B6YV` added
"Displayed precision" as the first such section. Each pass names an existing
test where one computes the claim, writes a test where none does, and
otherwise uses ``no test yet (`PL-XXXX`)`` against an open item. A figure
that is a published value is cited by a DOI, a PubMed id, an ISBN or a
journal locator. The pass then adds its sections to `BOUND_FAMILIES` in the
same change, so the check stays green.

[superseded 2026-11-14: PL-19W8 closed and found five wrong claims, so this pass runs]
**Blocked on `PL-19W8`, the first pass.** If that pass finds no computed
claim wrong or missing a condition in "Known limitations" and "Displayed
precision" together, this item is dropped and the check stays on those two
sections (`PL-B6YV` § "What would make this wrong").

**Done when.** Each section above is in `BOUND_FAMILIES` with
`_numeric_paragraph_members`, every one of its numeric paragraphs carries an
accepted form, and this brief records how many computed claims the pass
found wrong or missing a condition.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). Four of the five paragraphs were in `docs/MODEL.md` at `817a4d88`. The agent-amount paragraph came with `c95177a6` (2026-10-26).
