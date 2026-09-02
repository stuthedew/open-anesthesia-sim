---
id: PL-L4YG
title: Triage has no write command, so every triage answer is hand-edited front matter
priority: P2
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/store.py
added: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_cli.py -k new_captures && grep -q 'def test_set_writes_fields_in_canonical_order' subprojects/docket/tests/test_cli.py
---

**Problem.** `bin/docket` has one write command, `new`. Everything triage
decides - `priority`, `effort`, `classes`, `feature`, `touches`, `status`,
`verify`, `reason` - is written by hand into YAML front matter, or by a
throwaway script the session invents and discards. `docket triage` prints the
questions and the rules; nothing accepts the answers.

**Why it matters.** Three costs, and the third is the one that has already
been paid.

- It is deterministic work left to the model. Setting a field in a known
  format, in a known place, in a known order is the exact shape `CLAUDE.md`'s
  "prefer deterministic tooling" section says to move into code: paid for once
  and then free, against being re-derived at full context in every triage
  session.
- Field order and formatting drift, because the convention lives only in the
  existing files. A session that writes `verify:` above `added:` produces a
  file that passes `docket check` and reads differently from every other one.
- Hand-editing front matter is how `PL-BR4G` happened - `parse_front_matter`
  silently kept the last of a duplicate key, so two branches writing the same
  field merged into a corrupt item the checker passed. That specific hole is
  closed, but the class of failure is open for as long as the only way to
  answer triage is to retype the block.

**Measured 2026-09-02**, triaging fifteen items in one pass: the session
wrote a 25-line Python helper to set front matter in canonical order, used it
for eleven of the fifteen, and threw it away. The next triage session writes
it again.

**Where.** `subprojects/docket/src/docket/cli.py` for the subcommand,
`subprojects/docket/src/docket/store.py` for the write. `model.py` already
holds the field vocabulary and `checks.py` the rules, so the validation half
exists; what is missing is a writer that round-trips a file without
reformatting the body.

**Scope this narrowly.** A `docket set <id> --priority P2 --effort S ...` that
writes named fields in canonical order and refuses an unknown field is the
whole of it. Not an editor, not a wizard, not a triage workflow - the
judgment stays in the session, and `CLAUDE.md`'s rule against scripting the
judgment half applies here as much as anywhere. The one behaviour worth
adding past plain assignment is refusing to write a field that is already
present with a different value unless told to overwrite, since that is the
duplicate-key hazard arriving through the front door.

**Done when.** A triage session can set every field `docket triage` asks for
without hand-editing a file, the written block comes out in the same field
order as the rest of the store, and an unknown field name is refused rather
than written.
