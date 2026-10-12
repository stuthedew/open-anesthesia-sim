---
id: PL-TJ1S
title: docket.markdown does not take a lazy continuation line for a table's header row where the delimiter row under it sits inside the list item or block quote, so a table cmark-gfm renders inside the container is read as the paragraph above it going on; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
milestone: v0.5.24
touches: subprojects/docket/src/docket/markdown.py, subprojects/docket/tests/test_markdown_reference.py, subprojects/docket/tests/test_roadmap.py, docs/items/PL-TJ1S-docket-markdown-does-not-take-a-lazy.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1435
payoff: docket.markdown reads a table under a lazy header row as cmark-gfm does, or says plainly where it does not.
verify: grep -q 'def test_a_lazy_header_row_over_a_delimiter_row_inside_a_container' subprojects/docket/tests/test_markdown_reference.py
recurrences: 2026-10-12 PL-NNVJ withdrawn 2026-10-12 PL-TJ1S, 2026-10-12 PL-D23H withdrawn 2026-10-12 PL-TJ1S
---

**Problem.** docket.markdown does not take a lazy continuation line for a table's header row where the delimiter row under it sits inside the list item or block quote, so a table cmark-gfm renders inside the container is read as the paragraph above it going on; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
docket's shared readers. `markdown._parse` reads a
table where its header row and delimiter row both match the open containers.
A lazy continuation line (CommonMark 0.31.2 § 5.1, § 5.2) can be a table's
header row in cmark-gfm when the delimiter row under it is inside the
container (GFM 0.29 § 4.10), and the module's docstring says tables are read
where cmark-gfm reads one.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against cmark-gfm 0.29, which renders a paragraph and then a table
with rows `a | b` and `c | d` inside the list item:

```text
- x
a | b
  --|--
  c | d
```

docket gives one paragraph over all four lines; the block-quote form reads the
same. The references split: markdown-it-py 4.2.0 makes a top-level table and
ends the list, and pandoc's commonmark-hs reads as docket does. GitHub renders
with cmark-gfm. Latent: table counts agree with cmark-gfm across all 2,508
tracked Markdown files.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, under python3 3.13.16:
`markdown.read` gives one paragraph over all four lines for the list form and
the block-quote form alike; cmark-gfm (cmarkgfm 2025.10.22) renders each as a
paragraph and then a table with rows `a | b` and `c | d` inside the container.
The module docstring states the rule docket keeps - its header row "is a
paragraph line, not a lazy one" - as cmark-gfm's reading, which this form shows
it is not.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is a shared
reader's own gap: the paragraph is read past the point where cmark-gfm ends it.
Latent, so an ordinary item under the head's spent ruling (re-checked
2026-10-11).

**Two recurrences recorded on this item are not it** (2026-10-12). `PL-NNVJ`
is doc_check, roadmap, instructions and notes copying block readers
`docket.markdown` already holds, and `PL-D23H` is doc_check reading a fence's
lines short of a last line its container closes. Neither reads a lazy line as
a table's header row, so both are withdrawn.

**Why it matters.** Every block reader here takes `docket.markdown`'s reading,
and the module promises cmark-gfm's for tables, so a docstring stating as
GitHub's a rule GitHub does not follow is a confident answer that is wrong. A
table read as a paragraph going on has its rows judged as prose by the readers
that skip tables. Latent, so today's cost is the docstring's claim.

**Done when.** `docket.markdown` reads the form above as cmark-gfm does, or the
module's docstring and its markdown-it test name it as a departure; a test
pins the choice.
