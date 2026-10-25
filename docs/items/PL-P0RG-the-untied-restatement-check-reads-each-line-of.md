---
id: PL-P0RG
title: The untied-restatement check reads each line of docs/MODEL.md on its own, so a math span that hard wrapping splits across two lines, such as one ending V_A = and the next starting 2.5, is read on neither line and its figure goes unchecked
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** The untied-restatement check reads each line of docs/MODEL.md on its own, so a math span that hard wrapping splits across two lines, such as one ending V_A = and the next starting 2.5, is read on neither line and its figure goes unchecked

**Next steps, written 2026-10-25 by the thread that filed it, which stopped for length.** `check_untied_restatements` in `tools/doc_check.py` calls `_untied_figures(prose, raw)` once per line, and `MATH_SPAN_RE` needs both of a span's delimiters on that line. A likely fix is to join a line that opens a math span without closing it to the following lines until the span closes, read the joined text, and report any figure at the first line. `_without_code` blanks code and math per line too, so check that the joined reading and the blanked prose agree. Add a two-line case to `test_a_figure_in_a_list_a_lower_case_unit_or_a_math_span_is_asked_about` in `tests/unit/test_doc_check.py`. No span in `docs/MODEL.md` or `README.md` was split on 2026-10-25.
