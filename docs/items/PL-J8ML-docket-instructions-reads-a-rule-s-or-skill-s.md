---
id: PL-J8ML
title: docket.instructions reads a rule's or skill's front matter a line at a time, silently, wherever docket.frontmatter.keys declines any line of the block, so a key whose continued value keys could have delimited is cut into dated fragments; and it reads a sentence across the blank line inside a block-scalar value, so an older dated record is hidden behind a newer one; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket.instructions reads a rule's or skill's front matter a line at a time, silently, wherever docket.frontmatter.keys declines any line of the block, so a key whose continued value keys could have delimited is cut into dated fragments; and it reads a sentence across the blank line inside a block-scalar value, so an older dated record is hidden behind a newer one; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.release`, `docket.instructions` and the
notes readers. `instructions._front_matter`, new in `#1389`, catches
`frontmatter.Unread` and then reads every non-blank line of the block as its
own statement, with nothing said. A key's plain value continued on indented
lines is one statement (YAML 1.2.2 § 7.3.3), and `keys` could still have
delimited it: only some other line was unreadable. Separately, `parse` splits
a key's value into sentences with `SENTENCE_BREAK`, which needs a period,
exclamation or question mark, so a blank line inside a `>` or `|` value - a
line break YAML keeps (§ 8.1) and the end of a statement in the Markdown half -
does not end one.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against PyYAML 6.0.3 and ruamel.yaml 0.19.1:

```text
---
description: A rule (measured 2026-01-01, re-verified
  2026-10-04).
paths: a
stray line
---

---
description: >
  Measured 2026-01-01

  Re-verified 2026-10-04
---
```

The first gives two assertions, the first dated 2026-01-01 and reported stale,
where without the stray line it gives one dated 2026-10-04; both references
refuse the whole block, and nothing in docket's report says a line went
unread (`tools/rules_paths_check.py` names an unreadable block for a rule, and
nothing does for a skill). The second gives one assertion dated 2026-10-04,
where the same text in the body gives two; PyYAML reads the value with a line
break where the blank line was.

Latent: `docket.frontmatter.keys` raises `Unread` on none of the 12 front
matters in the 24 instruction files, and none holds a block scalar.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1389`.

**Done when.** A front matter `keys` cannot read whole is reported by name in
the instructions report rather than read a line at a time, and a blank line
inside a block-scalar value ends a sentence as a paragraph end does in the
body; a test pins both forms above.
