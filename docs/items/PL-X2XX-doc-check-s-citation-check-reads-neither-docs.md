---
id: PL-X2XX
title: doc_check's citation check reads neither docs/items/*.md nor source docstrings, so nothing holds the queue's or the code's citations to the docs they name
priority: P2
effort: M
status: ready
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_citation_in_an_item_brief' tests/unit/test_doc_check.py
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-01
---

**Problem.** `check_citations` (`tools/doc_check.py:1187`) resolves every path
and section a documentation file cites, and it is the check that would catch a
citation naming a heading that no longer exists. It runs only over the files
`DOC_GLOBS` (`tools/doc_check.py:118-127`) collects, and that tuple reaches
neither of the two places this project actually writes citations from:

- `docs/*.md` does not match `docs/items/*.md`, so not one of the 222 item
  briefs has its citations checked, though items routinely cite
  `docs/MODEL.md`, `ROADMAP.md` and `docs/WORKING_NOTES.md` by section.
- No `.py` file is read at all, so a module docstring pointing at a document
  is unchecked.

Both instances found on 2026-09-01 (`PL-8B1K`) are in exactly those two
blind spots, and `python3 tools/doc_check.py check` reports 0 errors with
both present.

A second, smaller hole is in the pattern rather than the globs:
`CITATION_RE` (`tools/doc_check.py:221-225`) recognises `see "…"`, `under
"…"` and `"…" above|below`. The `PL-042` instance writes the bare form
`` `docs/WORKING_NOTES.md`, "Splitting error outside the gate's operating
point" ``, which no branch of that pattern matches, so widening the globs
alone catches one of the two.

**Why it matters.** `CLAUDE.md` treats stale documentation as a safety issue
rather than tidiness, and holds that the decidable half of a documentation
question belongs in a script rather than in a session's judgement. Whether a
cited heading exists is fully decidable; it is already implemented; it is
simply not pointed at the queue, which is where this project writes most of
its prose. The cost of the gap is paid per stale citation, silently, since
`make check` passes.

**Where.** `tools/doc_check.py`: `DOC_GLOBS` (`:118-127`), `read_docs`
(`:436`), `check_citations` (`:1187`) and `CITATION_RE` (`:221-225`); tests in
`tests/unit/test_doc_check.py`.

**Watch for.** Widening the globs makes 222 item files documents for *every*
check in `read_docs`'s consumers, not only this one — the math-rendering check
is the one to think about, since `PL-TH9V` already swept items for math syntax
and would now be enforcing it. Decide per check whether items are in scope,
rather than letting the widened tuple decide for all of them. Adding a
citation-only document set is the alternative if that turns out to be the
answer for most of them.

**Done when.** A citation from an item brief or a source docstring that names
a heading no document has is a `make check` error, the two instances in
`PL-8B1K` are among the errors it reports before they are fixed, and each new
check reached by the widened set was deliberately included or excluded rather
than inherited.
