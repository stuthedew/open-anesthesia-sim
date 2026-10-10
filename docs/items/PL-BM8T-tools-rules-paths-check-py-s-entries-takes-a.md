---
id: PL-BM8T
title: tools/rules_paths_check.py's entries takes a #-led line under paths: for a YAML comment even inside a quoted or block scalar YAML carries onto it, so a rules file's glob is read from its first line alone and refused as unanchored with a garbled remedy, where YAML reads one sound glob; and it and doc_check's is_path_scoped read a quoted value a lenient parser carries onto a line at column 0 or at the item's column as a new key or a new glob; latent
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/frontmatter.py, tools/rules_paths_check.py, tools/doc_check.py, subprojects/docket/tests, tests/unit, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a rule's paths: scope is read whole or refused by name, so the rules check stops refusing a sound glob with a remedy nobody can apply, and a paths: line inside another key's quoted value no longer takes a resident rule out of the resident total
verify: grep -qF '"rules paths, a hash-led line inside a quoted' tests/unit/test_doc_check.py && grep -qF '"rules paths, a block scalar is refused by name"' tests/unit/test_doc_check.py && grep -qF '"rules paths, is_path_scoped reads no key inside another key' tests/unit/test_doc_check.py
---

**Problem.** tools/rules_paths_check.py's entries takes a #-led line under paths: for a YAML comment even inside a quoted or block scalar YAML carries onto it, so a rules file's glob is read from its first line alone and refused as unanchored with a garbled remedy, where YAML reads one sound glob; and it and doc_check's is_path_scoped read a quoted value a lenient parser carries onto a line at column 0 or at the item's column as a new key or a new glob; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
smaller tools and `tools/doc_check.py`. `entries`, the one reader of a rules
file's `paths:`, skips a line whose first non-blank character is `#` as a
comment, in its list loop and in the look-ahead it runs after an inline value.
In YAML 1.2.2 a `#` inside a quoted scalar (§ 7.3.1, § 7.3.2) or a block
scalar's content (§ 8.1) is content, never a comment (§ 6.6), so a scalar YAML
carries onto a `#`-led line is read from its first line only. The docstring
promises that any other continuation raises `Unreadable` naming it; this one
does not.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against PyYAML 6.0.3, five spellings YAML 1.2.2 allows:

```text
paths: "/src/**
  #x"

paths:
  - "/src/**
    #x"

paths: '/src/**
  #x'

paths:
  - '/docs
    #/x'
  - /tools/**

paths: >-
  #/src/**
```

`entries` gives `"/src/**`, `"/src/**`, `'/src/**`, `'/docs` and `/tools/**`,
and `>-`, quote and indicator included. PyYAML gives `/src/** #x` for the first
three, `/docs #/x` and `/tools/**`, and `#/src/**`. End to end, the second
spelling as a rules file with `src/` present makes `problems` report the glob
as matching at any depth and offer a replacement with the quote inside it,
where PyYAML's glob is anchored and sound. It always fails closed, since every
fragment opens with a quote or an indicator, but as a false finding with a
remedy nobody can apply.

Three further spellings are accepted by PyYAML and ruamel.yaml but not by a
strict YAML 1.2.2 reading, which wants a quoted scalar's continuation indented
past its parent (§ 6.3, `s-flow-line-prefix`): a continuation at column 0
(`entries` gives `"/src/**`), one at the item's own column opening `- `
(`entries` gives two globs, `"/src/**` and `/tests/**"`, where PyYAML gives
one), and, in another key's value, a column-0 continuation opening `paths:`:

```text
description: "Loads at launch, since no
paths: key defers it"
```

There `doc_check.is_path_scoped`, through `PATHS_KEY_RE` matched one line at a
time, calls the rule path-scoped and drops it from the resident total, and
`entries` returns the glob `key defers it"`; PyYAML reads one `description` and
no `paths` key. Latent: all 25 globs under `.claude/rules/` are one-line
double-quoted scalars, every rules file's front matter holds only `paths:`, and
`tools/rules_paths_check.py` exits 0.

**Why it matters.** `rules_paths_check` is the one check that a path-scoped rule
reaches the files it names, and `is_path_scoped` decides which rules count
toward the resident total that `CLAUDE.md` asks every edit to the resident set
to pay for. Read from a fragment, a sound glob is refused with a replacement
nobody can apply, and a resident rule whose quoted description carries a line
opening `paths:` drops out of the total, so the instruction budget reads
smaller than what loads at launch.

**Generator check.** A member of `PL-R417`: two readers take a physical line of
a YAML front matter for a statement YAML carries across lines. `PL-PPNV` fixed
`entries` for an over-indented dash, and `PL-GVDP`, open and filed beside the
head, is its trailing comment on the glob's own line; neither reaches these
forms, though one reading of the front matter as YAML would settle all three.

**Done when.** `entries` reads a quoted or block scalar whole or raises
`Unreadable` for one it does not read - a value whose opening quote its own
line does not close, and an inline block indicator, are the two cases to
decline - and `is_path_scoped` takes a line for the `paths:` key only where no
quoted scalar is still open above it, each pinned by a `rules paths, ` case in
`PL-R417`'s guard that fails on today's reader.

**Decided 2026-10-06.** The rule files' front matter gets one reader, which
`rules_paths_check.entries` and `instructions.parse` both take, in
`PL-R417`'s YAML batch (project owner, 2026-10-06, ratified, over patching
each reader in place).
