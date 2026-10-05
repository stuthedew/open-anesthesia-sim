---
id: PL-HXJY
title: PL-9HD1 gave the front-matter value grammar one reader, but its writers and docs still state it apart: docket new and set write a newline value the reader refuses (PL-0779), the reader keeps a YAML block-scalar header and closes on a ---y line (PL-LNDJ), and cmd_withdraw's docstring calls a folded value one line (PL-WJM4)
priority: P1
effort: M
status: done
classes: defect
feature: front-matter-round-trip
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/README.md, subprojects/docket/tests, docs/items/PL-B1DQ-a-v0-4-8-tag-exists-on-a-commit-whose-pyproject.md, docs/items/PL-K1DL-splitting-make-check-by-path-docket-changes.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1363
payoff: a value any docket command writes is read back exactly as written, so no queue reading starts from a field its writer and its reader disagree on
verify: grep -q 'def test_every_writer_refuses_a_value_the_reader_would_not_read_back' subprojects/docket/tests/test_model.py && grep -q '^generator: spent' docs/items/PL-HXJY-*.md
root-cause-of: PL-0779, PL-LNDJ, PL-WJM4
generator: spent - every front-matter writer now hands the file it would write to model._read_back, which reads it through the one reader and refuses before writing where a value would read back as anything else, so no writer states the grammar apart from its reader and a rule the reader gains reaches them unedited; the reader's own two misreadings (block-scalar header, loose closing fence) are fixed, and the docstrings name _fold rather than describe its extent
misread: The item front-matter value grammar: where a field's value ends and which spellings it may take
---

**Problem.** `PL-9HD1` (closed 2026-09-21, `#826`) gave the front-matter value
grammar one reader, `model._fold` under `parse_front_matter`, so a field's
continuation lines read whole. Thirteen days on, `PL-R417`'s last-slice sweep
filed three more readings of that fact, each outside what the one reader
reaches:

- `PL-0779`: `docket new` and `docket set` write a value holding a newline as
  it stands, and the next `bin/docket check` refuses the file the write made.
  The writers never ask the reader whether it can read the value back.
- `PL-LNDJ`: the reader keeps a YAML block-scalar header (`reason: >-`) as
  part of the value, live on two dropped items, and ends the front matter on
  any line opening `---`.
- `PL-WJM4`: `cmd_withdraw`'s docstring calls the `recurrences:` write a
  one-line replace, where `with_front_matter_value` replaces the key's line and
  every continuation `_fold` gives it.

**Why it matters.** The front matter is what every docket command reads first:
status, priority, `verify:`, the gate's deferral. A value written as one thing
and read back as another is a wrong answer at the root of every queue reading,
the store-level case of the floor in `.claude/rules/apparatus-standard.md`.
`PL-9HD1` fixed the reader and left the grammar restated in three other places,
the writers' serialisation, the reader's subset of YAML and the docstrings, each
free to disagree with the reader; three did within two weeks.

**Shape.** One record of the grammar that writers and docs consult rather than
restate: a write serialises the value, reads it back through
`parse_front_matter`, and refuses before writing when the two differ, so no
writer can produce a file the reader cannot read; the reader reads the
block-scalar headers YAML gives it or declines them by name; and a docstring
points at the one function rather than describing its extent.

**Done when.** `PL-0779`, `PL-LNDJ` and `PL-WJM4` are closed with their own
tests; every front-matter writer in `subprojects/docket/src/docket/` goes
through one write that refuses a value the reader would not read back as
written, pinned by
`test_every_writer_refuses_a_value_the_reader_would_not_read_back` in
`subprojects/docket/tests/test_model.py`; and `generator:` is rewritten `spent`
with the reason.

**Generator check.** The head: three instances of `PL-9HD1`'s fact filed on
2026-10-04, after that head closed on 2026-09-21, which
`.claude/skills/docket/modes/triage.md` counts as a generator whose fix did not
hold. Its `misread:` is `PL-9HD1`'s word for word, so the two sort together.
Not `PL-R417`'s: a value's extent and spelling is the grammar's question, not a
statement continued across lines, which is the sweep's own reading of
`PL-0779` and `PL-LNDJ`.
