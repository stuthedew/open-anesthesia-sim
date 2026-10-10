---
id: PL-P6D5
title: doc_check's _check_reference_files_exist reads REFERENCE_FILE_RE's code spans in docs/references/README.md a line at a time, so a code span carried across a line ending is read as two, and a filename CommonMark renders as prose is held to the reference folder; live in form
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-10
payoff: the reference index is read for the filenames a renderer shows in code spans, wrapped across a line or not
verify: grep -qF '"reference files, a code span carried across a line ending"' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _check_reference_files_exist reads REFERENCE_FILE_RE's code spans in docs/references/README.md a line at a time, so a code span carried across a line ending is read as two, and a filename CommonMark renders as prose is held to the reference folder; live in form

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s third part.
`REFERENCE_FILE_RE` is a code-span pattern applied to each line of
`docs/references/README.md`. A code span crosses a line ending (CommonMark
0.31.2 § 6.1), so its backticks pair across lines, and a backtick on a later
line can be the closer of a span opened above rather than the opener of a
filename.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against cmark-gfm 0.29, which renders `wrapped span` as the code span
and the filename as prose:

```text
# Refs

A `wrapped
span`x.pdf` tail.
```

The check reports that `x.pdf` is not in the reference folder. Live in form:
the index holds a code span carried across a line ending today, with no
filename in it, so no verdict changes.

**Why it matters.** `docs/references/README.md` is the index the
reference check holds to the folder of source documents behind the model's
parameters. A filename misread there is either a false error that fails
`make check` on a correct index, or a filed source whose name, wrapped in its
span, the check never compares.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is
older than the head; no member's fix reached it.

**Done when.** The index's filenames are read from the code spans
`_code_spans` gives a statement at a time, with a test on the form above.
