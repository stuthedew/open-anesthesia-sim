---
id: PL-8NPN
title: doc_check's title, group and math patterns misread within a line or a container - MARKER_RE and TAGS_MARK_RE read no bold title after an ordered marker, a nested bullet or a block quote, GATE_GROUP_RE reads a count past an opening emphasis run, and MATH_SPAN_RE pairs a dollar inside one code span with one inside another - so a citation is refused, a count misread, or prose blanked; latent
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: a bold title, a tags claim, a gate count and a math span are each read where CommonMark places them, so a correct section citation is not refused and no count or TeX span is checked against the wrong text
verify: grep -q 'def test_a_bold_title_inside_a_container_is_a_citable_section_title' tests/unit/test_doc_check.py && grep -q 'def test_a_tags_claim_inside_a_container_is_read' tests/unit/test_doc_check.py && grep -q 'def test_an_emphasised_note_stating_a_count_is_no_gate_group' tests/unit/test_doc_check.py && grep -q 'def test_dollars_in_two_code_spans_pair_as_no_math_span' tests/unit/test_doc_check.py
---

**Problem.** doc_check's title, group and math patterns misread within a line or a container - MARKER_RE and TAGS_MARK_RE read no bold title after an ordered marker, a nested bullet or a block quote, GATE_GROUP_RE reads a count past an opening emphasis run, and MATH_SPAN_RE pairs a dollar inside one code span with one inside another - so a citation is refused, a count misread, or prose blanked; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`tools/doc_check.py`.

```text
1. **Ordered title.** Text.
- top
  - **Nested title.** Text.
> **Quoted title.** Text.

*Note.* This list was frozen on 30 September - three entries were admitted later.

Run `echo $HOME` and then `cost $`.
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `_headings` returns none of the three titles, so a citation of one is
reported as a missing section (loud); `TAGS_MARK_RE` reads no tags statement
inside a container; `GATE_GROUP_RE` matches the emphasised line as a group
heading counting `three`; `MATH_SPAN_RE` pairs the two dollars across the
code spans and blanks the prose between. Latent: none in today's documents
changes a verdict (one closed brief holds the code-span form with no TeX).

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `_headings` reads a
top-level bullet's bold title beside the three forms above and none of the
three; `TAGS_MARK_RE` matches neither a block-quoted nor a nested-bullet
`**Tags.**`; `GATE_GROUP_RE` reads the emphasised line's count as `three`. The
math line as written above does not reproduce - `MATH_SPAN_RE` needs a dollar
standing against a backtick, and it holds one - but this form does, the
pattern pairing the dollar that ends the first span with the one that opens
the second, and `_without_code` blanking the prose between them:

```text
Run `echo $` and then `$ cost`.
```

**Why it matters.** Each pattern decides something a check acts on: which bold
titles a section citation may name, where a `**Tags.**` claim's region starts,
how many entries a frozen gate group states, and which text the math rules
read. Misread, a correct citation is refused, or a count or a TeX span is
checked against the wrong text.

**Generator check.** Not members of `PL-R417`: each reads within one line or
reads the wrong container.

**Done when.** Each pattern reads its construct where CommonMark places it,
inside containers and outside code spans, or declines by name; a test pins
each form above.
