---
id: PL-L4YG
title: Triage has no write command, so every triage answer is hand-edited front matter
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.28
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/store.py
added: 2026-09-02
closed: 2026-09-19
pr: 679
verify: uv run pytest subprojects/docket/tests/test_cli.py -k new_captures && grep -q 'def test_set_writes_fields_in_canonical_order' subprojects/docket/tests/test_cli.py
root-cause-of: PL-7K8Y, PL-LBR6, PL-NF6N, PL-YTDN, PL-Z9K5
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

**Recorded as a generator (2026-09-17, `PL-VX5H`).** This is one of the six
clusters `PL-6ZQY` found under "the apparatus infers a fact it could have
recorded", and it is the one whose remedy is a *writer*. Five open items exist
because there is not one: `PL-NF6N` is this finding re-filed ten days later;
`PL-YTDN` is nine item files whose slug drifted from a title edited in place;
and `PL-LBR6`, `PL-7K8Y` and `PL-Z9K5` are all `bin/docket record` - the only
other writer - renaming a file or reordering a hand-typed front-matter block as
a side effect of inserting `pr:`, which then reads as a content edit to the
close-out audit. Each of the five is the second cost this brief already names:
"field order and formatting drift, because the convention lives only in the
existing files". A writer that emits canonical order removes the population all
five sit in.

So `docket next` now offers this above every band but `P0`. Scope is unchanged
by the mark - `docket set`, refusing an unknown field, and nothing more.

Deliberately not named, though `PL-6ZQY`'s cluster sentence reaches them:
`PL-8JY7`, `PL-RWBV` and `PL-T86P` are gaps in `docket check` rather than in
the writer - a path that does not exist, a `needs-decision` item with no
`Decision needed` section - and a write command closes none of them. `PL-FX0K`
is `parse_item` misreading a YAML-list `touches:`, which is the reader.

**Closed 2026-09-19.** `bin/docket set <id> --priority P2 --effort S ...`
shipped, with `store.rewrite_item` beneath it: the named fields are written in
`render_item`'s order, the file keeps its name, and the write is refused where
it would add an error `docket check` did not already report - measured as the
difference between the store's errors with and without the write, so no rule
is restated in the command. Two choices worth knowing. `status` is exempt from
the overwrite refusal, because every valid item carries one and a flag typed
on every triage guards nothing. A file spelling a key twice or carrying an
unknown field is refused outright, since a rewrite would collapse or drop it
on nobody's decision. Measured on the store the day it landed: 144 of 1,189
item files would change under a rewrite - 96 in key order, a few more in list
spacing, 39 in the blank line under the front matter, one in a trailing
newline - and 7 filenames had drifted from their titles. That is the
population `PL-7K8Y`, `PL-Z9K5` and `PL-YTDN` sit in, which this shrinks as
items are triaged with it and does not clear. `record` still writes through
`write_item`; switching it to `rewrite_item` is `PL-LBR6`'s one line, left to
that item because it owes its own test.
