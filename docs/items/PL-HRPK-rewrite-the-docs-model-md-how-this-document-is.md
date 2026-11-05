---
id: PL-HRPK
title: Rewrite the docs/MODEL.md § 'How this document is held to the tree' paragraph on numeric paragraphs for its two readers: the clinician needs only that each number with a unit in a listed section is backed by a test, a date, a published source or a declared gap, and the check's mechanics (its function name, the marker kinds, the author-year exclusion, how a developer note holds paragraphs) belong in a developer note the section does not yet have; the PL-W8FL prose review proposed this on 2026-11-04 and it was left for its own item because it rewrites sentences that branch did not change
priority: P2
effort: S
status: done
classes: docs
feature: prose-quality
touches: docs/MODEL.md, tools/doc_check.py, tests/unit/test_doc_check.py
blocked-by: PL-HGZS
added: 2026-11-04
closed: 2026-11-05
pr: 2040
payoff: a clinician reading how the specification is checked learns what backs each number without reading the check's internals
verify: ! grep -q '`check_bound_families` enforces this rule one section at a time' docs/MODEL.md
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability for a clinician is judged by a person: no command can tell whether the paragraph now leads with what that reader needs.
---

**Problem.** Rewrite the docs/MODEL.md § 'How this document is held to the tree' paragraph on numeric paragraphs for its two readers: the clinician needs only that each number with a unit in a listed section is backed by a test, a date, a published source or a declared gap, and the check's mechanics (its function name, the marker kinds, the author-year exclusion, how a developer note holds paragraphs) belong in a developer note the section does not yet have; the PL-W8FL prose review proposed this on 2026-11-04 and it was left for its own item because it rewrites sentences that branch did not change

**Checked 2026-11-04.** The paragraph is the one in § "How this document is held to the tree" that opens "`check_bound_families` enforces this rule one section at a time". It names the check's function, the three marker kinds, the author-and-year exclusion, and how a note for developers covers the paragraphs above it. The section has ended in a "**For developers.**" note since `d509244e3` (`PL-T3KB`, 2026-11-03), so the mechanics can move there or into a new note directly below the paragraph. `tools/model_rewrite.py ids` already passes on the section, so it cannot prove this item.

**Why it matters.** A clinician reading the specification needs to know what backs a number they read. They do not act on the check's function name or its marker grammar, and those sentences stand between them and that one fact.

**Done when.** The paragraph tells the clinician, in a sentence or two, that each number with a unit in a covered section is backed by a test, a date, a published source or a declared gap. The check's mechanics are in a note for developers, with every rule they state kept. `tools/model_rewrite.py lost` shows no value, code span or citation dropped.

**Generator check.** An instance of `PL-J1ZM`'s fact, what a reader can do without, filed while that head is open. The `PL-W8FL` review found it and could not rewrite it, because the review rewrote only the units its branch changed. Added to `PL-J1ZM`'s `root-cause-of`.

**Applied 2026-11-05.** The whole section is now the copy editor's run 20 of it (`PL-HGZS` debug record, section 1), which the project owner approved on 2026-11-05 at 02:05Z. It was made from the same text as `main` holds, which a row-by-row comparison confirmed. Two sentences were then changed by the session. The `check_gate_counts` sentence, which the copy editor queried and left, now names the rule on counts (`PL-6VBY`). "Software of this class", which it queried, now points at § "Software safety classification: Class C, for the whole application". The rewrite drops the clause numbers, so the six comments in `tools/doc_check.py` and `tests/unit/test_doc_check.py` that cited "clause 2", "clause 3" or "clause 4", and the one in § "Minimum displayed outputs", now name the rule instead.
