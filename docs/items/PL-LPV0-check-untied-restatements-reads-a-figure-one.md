---
id: PL-LPV0
title: check_untied_restatements reads a figure one line at a time, so a stored value written with its unit on the next line, such as 2.5 and then L, is never asked about
priority: P2
effort: S
status: ready
classes: defect
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md
deferred-from: v0.7.0 - a new problem: check_untied_restatements came with 5ec0ee9b (2026-10-25 06:17), after the freeze
added: 2026-11-02
payoff: a stored value restated in the documents is checked against its source even when its unit wraps to the next line
verify: grep -q 'def test_untied_restatement_reads_a_unit_on_the_next_line' tests/unit/test_doc_check.py
reenters: PL-R417
---

**Problem.** check_untied_restatements reads a figure one line at a time, so a stored value written with its unit on the next line, such as 2.5 and then L, is never asked about

**Why it matters.** The check asks whether each restated stored value is tied to its source. A figure whose unit wraps to the next line is never asked about, and the check does not report the line it could not read.

**Reproduced 2026-11-03, by reading; not run on a sample.** `check_untied_restatements` in `tools/doc_check.py` loops over `enumerate(prose)`, one line at a time, so a figure and its unit on two lines are never one match.

**Done when.** A figure whose unit is on the next line is read as one figure, and a test in `tests/unit/test_doc_check.py` shows it.

**Generator check.** An instance of `PL-R417`'s fact, filed after that head closed on 2026-10-11: where one statement ends, in a format that lets a statement continue across lines (`reenters: PL-R417`).

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem began after Gate 3 froze at `817a4d88`, so the item stays deferred to the next gate, and its `deferred-from:` names the commit that began it. `check_untied_restatements` came with `5ec0ee9b` (2026-10-25 06:17), with its line-by-line loop.
