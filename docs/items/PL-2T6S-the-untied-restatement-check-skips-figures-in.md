---
id: PL-2T6S
title: The untied-restatement check skips figures in math spans, slash-joined lists such as 6/33/14.5 L, and lowercase units such as l/min
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** The untied-restatement check skips figures in math spans, slash-joined lists such as 6/33/14.5 L, and lowercase units such as l/min

**Why it matters.** `PL-JS6P`'s check refuses a figure in `docs/MODEL.md` or `README.md` that equals a stored value and has no marker. It reads a figure only in the forms `PROSE_FIGURE_RE` reads. The second blind review of `PL-JS6P` found restatements in three forms it does not read: a figure inside a math span, such as $`Q = 5`$ L/min; a list joined by slashes, such as "0.76/0.18/0.06" or "6/33/14.5 L"; and a unit in lower case, such as "4 l/min". A stored value restated in one of those forms can go stale with no error. `tools/doc_check.py` and the convention text in `docs/MODEL.md` state the limit.

**Done when.** Each of the three forms is either read by the check, with its figures marked in both documents, or recorded as out of scope with the reason. A test covers each form that is read.
