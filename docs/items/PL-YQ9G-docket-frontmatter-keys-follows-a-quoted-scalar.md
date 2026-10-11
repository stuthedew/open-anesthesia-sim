---
id: PL-YQ9G
title: docket.frontmatter.keys follows a quoted scalar or flow collection to its close only when it opens on its key's own line, so one opened on the line below - the value itself, or a list item under the key - is read by indentation alone, and a first-column line inside it becomes a top-level key with nothing raised: a rule reads as path-scoped, or a sound paths list is refused as written twice; live in form
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/frontmatter.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-10
closed: 2026-10-10
pr: 1392
payoff: a quoted or flow value opened below its key is read to its close, so no line inside it is taken for a key
verify: grep -qF '"front matter, a double-quoted value opened below its key"' tests/unit/test_doc_check.py && grep -qF '"front matter, a flow mapping opened below its key"' tests/unit/test_doc_check.py && grep -qF '"front matter, a quoted list item under its key"' tests/unit/test_doc_check.py
---

**Problem.** docket.frontmatter.keys follows a quoted scalar or flow collection to its close only when it opens on its key's own line, so one opened on the line below - the value itself, or a list item under the key - is read by indentation alone, and a first-column line inside it becomes a top-level key with nothing raised: a rule reads as path-scoped, or a sound paths list is refused as written twice; live in form

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`docket.frontmatter` and of docket's shared
readers. `keys` and `_past` follow a double- or single-quoted scalar
(YAML 1.2.2 § 7.3.1, § 7.3.2) or a flow collection (§ 7.4) to its close where
it opens on the key's line, and raise `Unread` for every other form they
cannot place. A node opened on the next line is passed over by indentation, so
a first-column line inside it reads as a key. PyYAML 6.0.3 and ruamel.yaml
0.19.1 read that line as the node's continuation, and a strict 1.2.2 reader
refuses it (§ 6.3); under neither is it a key. The module's own docstring says
of the key-line form that the key such a line looks like is no key; the same
holds a line lower.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against PyYAML 6.0.3 and ruamel.yaml 0.19.1, which read one
`description` key and no `paths` key:

```text
---
description:
  "Loads at launch, since no
paths: key defers it"
---
```

`keys` gives `description` and `paths`, so `rules_paths_check` reports the
glob as pointing at nothing and `doc_check.is_path_scoped` takes a resident
rule out of the resident total. With a real block-list `paths:` below, the
same form makes `rules_paths_check` refuse a sound list as written twice. The
single-quoted, flow-sequence and flow-mapping forms read the same way.

Live in form: a quoted node opened below its key stands 25 times in
`.claude/rules/` (each a quoted glob under `paths:`), none continued to the
first column, and `rules_paths_check` exits 0 on today's tree.

**Why it matters.** `docket.frontmatter.keys` is the one reader every
rule's and skill's front matter goes through, and the `paths:` key it reads
decides whether a rule loads at launch or only on a matching read. A key misread
out of a quoted value makes a resident rule read as path-scoped, so it drops out
of the resident total, or makes `rules_paths_check` refuse a sound list, each
with nothing raised.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The module is
new in `#1389`: the gap closed `PL-BM8T`'s fix left,
which reached the node opened on the key's line only.

**Done when.** A quoted scalar or flow collection opened below its key is
followed to its close as one opened on the key's line is, or `Unread` names it;
a test pins each form above against PyYAML's reading.

**Built 2026-10-10 (`#1392`).** `keys` follows a quoted scalar or a flow
collection to its close wherever it opens: on the key's line, alone on the line
under a key or entry holding nothing, after a list entry's `- `, or after a
nested key's `:`. A block scalar's lines and a plain scalar's continuation lines
are read as text, so a quote opening one opens nothing. Five `front matter, `
cases in `PL-R417`'s guard pin the double-quoted, single-quoted, flow-mapping,
flow-sequence and quoted-list-item forms, each failing on main's reader with a
`paths` key read out of the value. `subprojects/docket/tests/test_frontmatter_reference.py`
holds `keys` to PyYAML 6.0.3 over 2,000 generated front matters: all agree, where
main's reader misreads 89 and declines 380.
