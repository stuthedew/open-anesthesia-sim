---
id: PL-J8ML
title: docket.instructions reads a rule's or skill's front matter a line at a time, silently, wherever docket.frontmatter.keys declines any line of the block, so a key whose continued value keys could have delimited is cut into dated fragments; and it reads a sentence across the blank line inside a block-scalar value, so an older dated record is hidden behind a newer one; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/frontmatter.py, subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_instructions.py, subprojects/docket/tests/test_checks.py, tools/doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1447
payoff: the instructions audit names a front matter it cannot read and dates a block-scalar record by its own sentence, so an old dated claim is neither split nor hidden behind a newer one
verify: grep -q 'def test_a_front_matter_keys_cannot_read_is_reported_by_name' subprojects/docket/tests/test_instructions.py && grep -q 'def test_a_blank_line_inside_a_block_scalar_ends_a_sentence' subprojects/docket/tests/test_instructions.py
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

**Re-confirmed 2026-10-11** on main at `16a20a4f`: `instructions._front_matter`
is gone, moved by `#1392` into `docket.frontmatter.statements`, which keeps the
line-at-a-time fallback on `Unread` and now says so in its docstring.
`instructions.parse` still gives the first form two assertions, dated
2026-01-01 and 2026-10-04, against one dated 2026-10-04 without the stray
line, and the second form one assertion dated 2026-10-04 where the same text
in the body gives two.

**Why it matters.** The instructions audit exists to surface dated claims that
have gone old. A record cut into fragments is reported stale after it was
re-verified, a record hidden behind a newer sentence never reaches the report,
and in neither case does the audit say it could not read the block.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1389`. Latent, so an ordinary item under that head's `spent` verdict: found live in a tracked file, it reopens `PL-R417` (2026-10-11 triage).
`PL-JTP1` (untriaged) groups it with five other callers that lose a shared
reader's decline, and proposes the type-level fix that would close them together.

**Done when.** A front matter `keys` cannot read whole is reported by name in
the instructions report rather than read a line at a time, and a blank line
inside a block-scalar value ends a sentence as a paragraph end does in the
body; a test pins both forms above.

**Fixed 2026-10-12** in `#1447`. `instructions.parse` reads a front matter's
statements through `frontmatter.key_statements`, `statements` without its
line-at-a-time fallback, so a block `keys` declines is read for no sentence;
`instructions.unread_front_matter` names each such file with `keys`' reason,
and `docket check` lists it under "Not checked" through `analyze`'s
`unread_instructions`, as `unread_notes` carries a release-notes bullet the
notes reader declined. Not a partial reading of the keys around the bad line:
`keys` is the one reader of the grammar and refuses the block whole, and a
second reader beside it is what `CLAUDE.md`'s single source of truth refuses.
`_sentences` now ends a sentence at a blank line as well as at
`SENTENCE_BREAK`, which `tools/doc_check.py`'s host-claim check shares, and a
Markdown body statement never holds one. The two forms above are pinned by
`test_a_front_matter_keys_cannot_read_is_reported_by_name` and
`test_a_blank_line_inside_a_block_scalar_ends_a_sentence` (`>`, `|` and `>-`),
and the report by
`test_a_front_matter_the_reading_declined_is_named_as_not_checked`.
`tools/fact_home_check.py` reads 107 second readers against a baseline of 107
before and after: the fix removes no entry, since the only one in the files it
changes is `instructions._markdown_under`'s walk, which it leaves alone, and it
adds no reader.
