---
id: PL-LPV0
title: check_untied_restatements reads a figure one line at a time, so a stored value written with its unit on the next line, such as 2.5 and then L, is never asked about
priority: P2
effort: S
status: done
classes: defect
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md
deferred-from: v0.7.0 - a new problem: check_untied_restatements came with 5ec0ee9b (2026-10-25 06:17), after the freeze
added: 2026-11-02
closed: 2026-11-22
pr: 2224
payoff: a stored value restated in the documents is checked against its source even when its unit wraps to the next line
tests: tests/unit/test_doc_check.py::test_a_figure_whose_unit_opens_the_next_line_is_asked_about, tests/unit/test_doc_check.py::test_a_number_ending_a_paragraph_joins_no_unit_from_the_next
reenters: PL-R417
---

**Problem.** check_untied_restatements reads a figure one line at a time, so a stored value written with its unit on the next line, such as 2.5 and then L, is never asked about

**Why it matters.** The check asks whether each restated stored value is tied to its source. A figure whose unit wraps to the next line is never asked about, and the check does not report the line it could not read.

**Reproduced 2026-11-03, by reading; not run on a sample.** `check_untied_restatements` in `tools/doc_check.py` loops over `enumerate(prose)`, one line at a time, so a figure and its unit on two lines are never one match.

**Done when.** A figure whose unit is on the next line is read as one figure, and a test in `tests/unit/test_doc_check.py` shows it.

**Generator check.** An instance of `PL-R417`'s fact, filed after that head closed on 2026-10-11: where one statement ends, in a format that lets a statement continue across lines (`reenters: PL-R417`).

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem began after Gate 3 froze at `817a4d88`, so the item stays deferred to the next gate, and its `deferred-from:` names the commit that began it. `check_untied_restatements` came with `5ec0ee9b` (2026-10-25 06:17), with its line-by-line loop.

**Checked 2026-11-22** against `d4e8200`: still applies. `check_untied_restatements` in `tools/doc_check.py` still loops `for index, line in enumerate(prose)`, one line at a time, and its docstring still says it reads a line at a time. `tests/unit/test_doc_check.py` has no test of a unit on the next line.

**Done 2026-11-22.** `_wrapped_figure` in `tools/doc_check.py` joins a number that ends a prose line with a unit that opens the next one, and `check_untied_restatements` asks about the joined figure. A blank line ends the paragraph and joins nothing. The four provenance documents raised no new error after the change. Files checked: the docstring of `check_untied_restatements`, which now says it, and `docs/MODEL.md`, `docs/INTERFACE.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md`, none of which describes the line-at-a-time reading (searched for "line at a time").
