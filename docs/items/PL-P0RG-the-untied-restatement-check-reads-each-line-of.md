---
id: PL-P0RG
title: The untied-restatement check reads each line of docs/MODEL.md on its own, so a math span that hard wrapping splits across two lines, such as one ending V_A = and the next starting 2.5, is read on neither line and its figure goes unchecked
priority: P3
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-10-25
closed: 2026-10-25
pr: 1810
payoff: the untied-restatement check's docstring says why a split math span cannot hide a figure on a passing run, and a test holds that
verify: uv run pytest -q tests/unit/test_doc_check.py -k 'split_across_two_lines_is_refused'
---

**Problem.** The untied-restatement check reads each line of docs/MODEL.md on its own, so a math span that hard wrapping splits across two lines, such as one ending V_A = and the next starting 2.5, is read on neither line and its figure goes unchecked

**Closed without the join, on a measurement.** A math span split across
two lines cannot pass `make check` at all. GitHub renders inline math only
within one line, so the split span shows as literal text.
`check_math_delimiters` already refuses both halves, `$`` on the first line
and ``$` on the second. Measured 2026-10-25 on a scratch repository: the
wrapped span `$`V_P =` then `0.5`$ L` gave two unpaired-delimiter errors and
no untied-restatement error. With the span joined onto one line, the
untied-restatement check asked about the figure, as it should.

So no figure can go unchecked on a run that passes. The writer has to join
the span to make the document pass, and the joined span is read. Joining
lines inside `check_untied_restatements` would only read a document that
fails anyway. The defect was in the check's docstring, which said a split
span "is not checked" without saying that the math check refuses it first.
The docstring now says so, and
`test_a_math_span_split_across_two_lines_is_refused_before_its_figure_is_read`
holds both halves of the argument.

**Generator check.** A one-off. The check reads each line as the math check
does, and the math check's refusal is what covers the gap.
