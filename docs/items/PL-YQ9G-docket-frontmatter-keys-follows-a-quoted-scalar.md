---
id: PL-YQ9G
title: docket.frontmatter.keys follows a quoted scalar or flow collection to its close only when it opens on its key's own line, so one opened on the line below - the value itself, or a list item under the key - is read by indentation alone, and a first-column line inside it becomes a top-level key with nothing raised: a rule reads as path-scoped, or a sound paths list is refused as written twice; live in form
status: untriaged
feature: one-answer
added: 2026-10-10
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

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The module is
new in `#1389`: the gap closed `PL-BM8T`'s fix left,
which reached the node opened on the key's line only.

**Done when.** A quoted scalar or flow collection opened below its key is
followed to its close as one opened on the key's line is, or `Unread` names it;
a test pins each form above against PyYAML's reading.
