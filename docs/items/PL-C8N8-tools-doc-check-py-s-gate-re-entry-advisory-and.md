---
id: PL-C8N8
title: tools/doc_check.py's gate re-entry advisory and two docstrings still describe ROADMAP.md's debt gate as it stood before the restructure: the snapshot section no longer ends with the safety and science exceptions, and beat 4 no longer restates them
status: untriaged
feature: roadmap-structure
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-11-07
---

**Problem.** `tools/doc_check.py` describes `ROADMAP.md`'s debt gate as it stood
before `PL-P0C5` rebuilt it. Three passages are now wrong about the roadmap:

- the `check_gate_reentries` docstring, about line 4620: "`ROADMAP.md` states
  one unconditional rule twice - step 4 of "The cadence" and "The gate is a
  snapshot, not a moving target"". Beat 4 now points to the snapshot section and
  no longer restates the rule.
- the same docstring, about line 4654: "because "The gate is a snapshot" closes
  by saying these". The section now ends with a pointer to the `anticipated`
  carve-out, and the exceptions sit in its subsection § "Which findings re-enter
  the gate".
- the advisory text, about line 4770: "\"The gate is a snapshot\" ends by
  making these two not deferrable".

`tests/unit/test_doc_check.py`, about line 6938, repeats "ends by making" in a
docstring.

**Found by** `PL-P0C5` (slice 2 of the roadmap restructure), 2026-11-07. The
restructure changed only `ROADMAP.md` and item briefs, so the tool's text waits
for slice 4 (`PL-G6DP`), which moves tool descriptions out of the roadmap.

**Why it matters.** The advisory prints on every `make check` that finds an open
`safety` or `science` item without a placement. It sends the reader to a sentence
that is no longer where it says.

**Done when.** The three passages and the test docstring name the section that now
states the rule, § "Which findings re-enter the gate", and say "states" rather
than "ends by" or "closes by". `PL-8C8W` may change the rule itself; if it lands
first, the text follows its answer.

**Generator check.** The cause is a tool's message that says where a document
states a rule, which goes stale when the document is rearranged. This is the
one instance the restructure has found so far, so no generator is recorded. A
second instance in a later slice would make it worth recording.
