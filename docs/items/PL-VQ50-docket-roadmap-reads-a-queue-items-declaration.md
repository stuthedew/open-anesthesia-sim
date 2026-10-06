---
id: PL-VQ50
title: docket.roadmap reads a queue-items declaration and a gate entry's leading ids from text joined across paragraph ends - the whole Required scope subsection, and each entry with its later paragraphs - so a run of ids left open at a paragraph's end declares or holds the id opening the next paragraph, or the next entry; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** docket.roadmap reads a queue-items declaration and a gate entry's leading ids from text joined across paragraph ends - the whole Required scope subsection, and each entry with its later paragraphs - so a run of ids left open at a paragraph's end declares or holds the id opening the next paragraph, or the next entry; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.roadmap`. `_subsection_text` joins a whole `Required scope` subsection,
blank lines and entries included, and `_declared_ids` reads it for
`own_scope_ids`; `_scope_entries` reads each entry's joined text, later
paragraphs included, with `_declared_ids`, and `_gate_entries` reads it with
`vcs.leading_ids`, whose wrap admits a `*` between ids. A declaration slot, like
the quotations `PL-BYJ5` and `PL-T73L` fixed, is a statement inside the
paragraph it opens in: a paragraph ends at a blank line (CommonMark 0.31.2
§ 4.8) and an item at the next item (§ 5.2, § 5.3).

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0. Four sections, each with a run of ids left open
where its paragraph or entry ends:

```text
Ships the reader (queue items `PL-BC12`,

`PL-CD34` is cited only as background.

* **The reader.** Ships it (queue items `PL-BC12` and
* `PL-CD34` is another entry.

- **The reader.** Ships it (queue items `PL-BC12`,

  `PL-CD34` opens a later paragraph.

- PL-BC12 and

  PL-CD34 is a later paragraph of a debt-gate entry.
```

`own_scope_ids` declared both ids in the first three; `_scope_entries` gave
both ids to the third entry and only the first to the second, so the
subsection-wide and per-entry reads disagree; and the debt-gate entry held both
ids. markdown-it ends the first paragraph at its blank line, reads the second
pair as two items, the third as one item of two paragraphs, and the fourth as
two paragraphs. A slot wrapped by a soft break inside one paragraph declares
both ids in every reader. Latent: reading `ROADMAP.md` one prose block at a time
gives the same ids as the joined read for all 9 sections' own scope and all 536
gate and scope entries.

**Generator check.** A member of `PL-R417`: readers read a declaration past the
end of the paragraph it opens in. `PL-YSMD` and `PL-MFVV`, both members, fixed
where an entry ends, not what is read inside it.

**Done when.** The declaration and leading-id readers read one prose block at a
time, through `docket.markdown.statement_lines`, pinned by a `roadmap
declarations, ` case in `PL-R417`'s guard for each of the four forms, failing
on today's reader.
