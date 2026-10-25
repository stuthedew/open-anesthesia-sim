---
id: PL-2T6S
title: The untied-restatement check skips figures in math spans, slash-joined lists such as 6/33/14.5 L, and lowercase units such as l/min
priority: P2
effort: M
status: done
classes: defect
feature: one-source-of-truth
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md
added: 2026-10-25
closed: 2026-10-25
payoff: a stored value restated in docs/MODEL.md as part of a slash list, with a lower-case unit, or as a symbol given a number in math can no longer go stale without an error
verify: uv run pytest -q tests/unit/test_doc_check.py -k 'list_a_lower_case_unit or inside_an_equation' && uv run python tools/doc_check.py check
reenters: PL-JS6P
---

**Problem.** The untied-restatement check skips figures in math spans, slash-joined lists such as 6/33/14.5 L, and lowercase units such as l/min

**Why it matters.** `PL-JS6P`'s check refuses a figure in `docs/MODEL.md` or `README.md` that equals a stored value and has no marker. It reads a figure only in the forms `PROSE_FIGURE_RE` reads. The second blind review of `PL-JS6P` found restatements in three forms it does not read: a figure inside a math span, such as $`Q = 5`$ L/min; a list joined by slashes, such as "0.76/0.18/0.06" or "6/33/14.5 L"; and a unit in lower case, such as "4 l/min". A stored value restated in one of those forms can go stale with no error. `tools/doc_check.py` and the convention text in `docs/MODEL.md` state the limit.

**Done when.** Each of the three forms is either read by the check, with its figures marked in both documents, or recorded as out of scope with the reason. A test covers each form that is read.

**What was done.** `tools/doc_check.py` now reads each number of a list joined
by slashes, with the list's unit; a unit written in lower case (`UNIT_CASES`:
`l/min`, `l/s`, `l`); and a math span that ends by giving a symbol a number,
such as $`V_A = 2.5`$ L or $`\Delta t = 0.1\ \mathrm{s}`$. Any other number in
a math span stays unread, and that limit is recorded with its reason in the
check's docstring and in `docs/MODEL.md`'s convention text. On 2026-10-25,
128 numbers inside math spans in `docs/MODEL.md` shared a value with some
stored value, and nearly all were exponents and coefficients, such as the 10
in $`10^{-12}`$. Reading the new forms found nine figures with no
marker, all in `docs/MODEL.md`. Each is now marked: the 2.5 l functional
residual capacity is tied to `alveolar_gas_volume_l`, and the rest, which quote
a source or a superseded method, are declared `not-restated`.

**Generator check.** A re-entry of `PL-JS6P`, closed today, whose check these
forms slipped past. Recorded as `reenters: PL-JS6P`.

