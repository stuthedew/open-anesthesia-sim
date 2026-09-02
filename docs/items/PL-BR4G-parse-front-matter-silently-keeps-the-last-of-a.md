---
id: PL-BR4G
title: parse_front_matter silently keeps the last of a duplicate front-matter key, so two branches writing the same field merge into a corrupt item that docket check passes
status: untriaged
added: 2026-09-02
---

**Problem.** `parse_front_matter` in `subprojects/docket/src/docket/model.py`
builds its field dict with `fields[key] = value` in a loop, so a block carrying
the same key twice keeps the **last** occurrence and discards the first without
a word. `parse_item` then reports `unknown_fields` for a *misspelled* key -
whose comment in `checks.py:151-155` says "a misspelled field is silently
ignored, so it is rejected here" - but nothing detects a *repeated* one.

Demonstrated 2026-09-02 against the real parser:

```
>>> parse_front_matter("---\nid: X\npr: 187\nclosed: 2026-09-02\npr: 999\n---\nbody\n")[0]["pr"]
'999'          # 187 is gone, no error, no advisory
```

**Why it matters.** This is not hypothetical and it is not cosmetic. It reached
`main` the same day:

- `docket check` raised the standing advisory asking for `PL-X0RG`'s `pr` to be
  written in.
- #190 answered it by inserting `pr: 187` **after** `closed:`; #189 answered it
  independently by inserting `pr: 187` **before** `closed:`.
- Different line positions, so git merged both cleanly rather than conflicting.
  `main` carried two `pr:` lines and `bin/docket check` reported **0 errors**.

Both values happened to be `187`, so nothing was actually lost this time. That
is luck, not a guarantee: had the two sessions recovered different numbers - the
realistic case, since each was reading a different merge commit - the store
would have silently recorded one and dropped the other, and the check whose
entire job is provenance would have called it clean. `pr` is the field that
makes a closed item traceable to the change that closed it, which
`CLAUDE.md`'s safety-critical standard names as a requirement rather than a
nicety.

The concurrency that produced it is ordinary here and getting more common: the
advisory is written to be answered by "whatever branch comes next", and more
than one branch can be next. `PL-PRHN` covers the collision itself; this item
covers why the collision was **invisible**. Both are needed - a guard against
concurrent edits still leaves a corrupt file undetected if it lands another way
(a bad hand-edit, a botched conflict resolution, a generated block).

**Where.** `parse_front_matter` and `parse_item` in
`subprojects/docket/src/docket/model.py`; the per-item error block in
`subprojects/docket/src/docket/checks.py` around line 151, beside the
`unknown_fields` rule it should sit next to; `subprojects/docket/tests/test_model.py`
and `subprojects/docket/tests/test_checks.py`.

**Approach.** `Item` already carries `unknown_fields` as a parse-level finding
for `checks.py` to report, which is the exact shape this needs - so add
`duplicate_fields` alongside it, populated in `parse_item`, and report it as an
error next to the unknown-field one. Standard library only, decidable by reading
the file, no judgment to script. Keep it an **error** rather than an advisory:
unlike the advisories around it, there is nothing for a reader to weigh - a
front-matter key appearing twice is always wrong, and the value that was
dropped cannot be recovered from the parsed item.

Worth checking while there whether `render_item` can ever emit a duplicate; if
it cannot, the guard is purely about hand-edited and merged files, which is
where every instance so far has come from.

**Done when.** `bin/docket check` errors on an item whose front matter repeats a
key, naming the key; a test pins that a duplicate is reported rather than
silently resolved; and the error text says which value was kept, so a reader
fixing it knows what the parser had been using.
