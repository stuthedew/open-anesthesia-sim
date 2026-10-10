---
id: PL-2MLT
title: docket's instructions.parse and notes.read read a file's YAML front matter as Markdown, where its keys are one setext heading, so a dated key is dated by the next key's newer date and a key naming an item opens a notes thread about it; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/notes.py, subprojects/docket/src/docket/frontmatter.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: each dated front-matter key in the instruction set is dated by its own newest date, and a notes file's front matter opens no thread, so an old record is not hidden behind a newer key's date
verify: grep -qF '"instruction audit, a front matter' tests/unit/test_doc_check.py && grep -qF '"notes, a front matter' tests/unit/test_doc_check.py
---

**Problem.** docket's instructions.parse and notes.read read a file's YAML front matter as Markdown, where its keys are one setext heading, so a dated key is dated by the next key's newer date and a key naming an item opens a notes thread about it; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`instructions.py` and `notes.py`. Each key of a YAML 1.2.2 front matter is its
own statement, ending at the next key. Read as CommonMark, the block between the
two `---` lines is one paragraph whose closing `---` is a setext underline
(§ 4.3), so the line breaks between keys are soft breaks. `instructions.parse`
reads its statements through `markdown.statement_lines` and `notes.read` its
headings through `docket.markdown`, both from the file's first line.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against PyYAML and markdown-it-py 4.2.0 with `mdit_py_plugins`' front-matter
plugin:

```text
---
name: example
description: Decided by the project owner on 2026-06-01
paths: src/**, re-checked 2026-10-04
---

Body.
```

`instructions.parse` gave one assertion, on line 4, dated 2026-10-04, whose text
runs from `name:` to the closing `---`, so the 2026-06-01 record is hidden
behind the newer date; the references give three separate keys and no heading.
For notes, a file opening with a front matter of `title: Working notes` and
`see: PL-BBBB`, then a heading opening a thread on `PL-CCCC`, gave a phantom
thread at line 2 titled from both keys and about `PL-BBBB`, beside the real
one; the references' only heading is the thread's. Plain CommonMark, with no
front-matter extension, reads both files as docket does, so the readings differ
only once front matter is recognised - which is how this repository's files
carry it. Latent: 12 of the 24 files in the instruction set carry front matter
and none of it holds a date; `docs/WORKING_NOTES.md` has none.

**Why it matters.** The instruction audit is what tells a grooming pass which
dated records in the instruction set are due for re-checking, and `bin/docket
show` points at the notes threads about an item. Read as one paragraph, a front
matter hides an old dated key behind the next key's newer date, so the record
is never named as due, and a key naming an item opens a thread about it that
the notes file never wrote.

**Generator check.** A member of `PL-R417`: a statement that ends at the next
key is read as continuing through every key to the fence. `PL-B1D0` and
`PL-HKHP`, both members, fixed these two readers for the Markdown forms and
left the front matter.

**Done when.** Both readers split a front matter off before reading Markdown -
`vcs._markdown_statements` already does - reading each key as one statement,
where they read it at all, and keeping the body's line numbers, pinned by an
`instruction audit, ` and a `notes, ` case in `PL-R417`'s guard that fail on
today's readers.

**Decided 2026-10-06.** The rule files' front matter gets one reader, which
`rules_paths_check.entries` and `instructions.parse` both take, in
`PL-R417`'s YAML batch (project owner, 2026-10-06, ratified, over patching
each reader in place).
