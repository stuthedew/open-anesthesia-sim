---
id: PL-NNVJ
title: doc_check, roadmap, instructions and notes copy Markdown block readers docket.markdown and instructions already hold - container markers, table cells, list markers, a front matter blanked from the body (three copies) and _markdown_under - and the container-marker regexes read 'a' then '    > b' differently
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
milestone: v0.5.28
touches: tools/doc_check.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/notes.py, subprojects/docket/src/docket/frontmatter.py, subprojects/docket/src/docket/checks.py, tools/fact_home_check.py, tests/unit/test_doc_check.py, tests/unit/test_inline_reference.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1566
payoff: a document's block structure is read by docket.markdown wherever docket or a tool reads it
verify: grep -q 'def test_a_four_column_quote_marker_is_paragraph_text' tests/unit/test_doc_check.py
---

**Problem.** doc_check, roadmap, instructions and notes copy Markdown block readers docket.markdown and instructions already hold - container markers, table cells, list markers, a front matter blanked from the body (three copies) and _markdown_under - and the container-marker regexes read 'a' then '    > b' differently

- Container markers on a continued line: `markdown.unmarked` beside `doc_check.SOFT_BREAK`, `SPAN_BREAK_RE` and `CONTINUATION_RE` (read by `_normalized`). On `a` followed by `    > b`, markdown reads the four-column line as paragraph text and keeps `> b`; `CONTINUATION_RE` drops the `>`. `PL-BCZQ` and `PL-Z1R7` fixed single cases and kept the regexes.
- Table cells: `markdown.cells` and `_CELL_BREAK` beside `doc_check._cells` and `CELL_BREAK_RE`, the same regex; they agree.
- List markers: `markdown._MARKER` beside `roadmap.ENTRY_MARKER_RE`; they agree on every line markdown opens an item on, and part on `* * *`, a thematic break.
- A body with its front matter blanked: `doc_check._body_lines`, inline in `instructions` and in `notes`; they agree.
- [superseded 2026-10-12: `PL-J4YY` folded it, and `doc_check` imports `instructions`' copy, which reads the tracked-file list] `_markdown_under`: a verbatim copy in `instructions` and `doc_check`; they agree, though doc_check's roots add `.claude/CLAUDE.md`.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** doc_check, roadmap, instructions and notes take these from `docket.markdown` (or one export each), and a test pins the four-column `> b` line.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
