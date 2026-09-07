---
id: PL-X2XX
title: doc_check's citation check reads neither docs/items/*.md nor source docstrings, so nothing holds the queue's or the code's citations to the docs they name
priority: P2
effort: M
status: done
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_citation_in_an_item_brief' tests/unit/test_doc_check.py
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/items/PL-XF89-readme-s-opening-says-inhaled-anesthetic-where.md
added: 2026-09-01
closed: 2026-09-07
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

```text
`docs/WORKING_NOTES.md`, "Splitting error outside the gate's operating point"
```

which no branch of that pattern matches, so widening the globs alone catches
one of the two.

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

**Measured, 2026-09-07.** The brief above was written on 2026-09-01 and its
premise does not survive contact with the tree. Everything below is counted,
not estimated; the probes are reproducible from `read_docs`, `CITATION_RE`,
`_cites_heading` and `_resolves` as they stand.

- **The store is 687 item files, not 222** - 231 open, 456 closed.
- **Neither `PL-8B1K` instance becomes an error under the widening this brief
  describes.** The `src/anesthesia_sim/core/uptake_system.py` one no longer
  exists: `PL-006` rewrote that docstring, and `grep -n 'near-term to-dos'`
  over the tree now finds it only inside item prose *about* the defect. The
  `PL-042` one survives, and it is missed for two reasons that are both in
  `CITATION_RE` rather than in `DOC_GLOBS` - see the pattern finding below.
- **Widening `DOC_GLOBS` to `docs/items/*.md` yields 16 section-citation
  errors and 143 unresolved path citations, and close to all of them are
  noise.** The section ones are quoted program output (`"do not start these
  again"` from the digest, `"Cannot run alongside"` from `docket concurrent`,
  `"not checked"` from `_check_landed`), a GitHub settings label (`"Require
  status checks to pass"`), ordinary English read as a direction (`ranks
  "irreversible architectural problems" above code style`), this item's own
  `"…"` placeholders, and headings that `ROADMAP.md` genuinely had when a
  closed item cited them. The path ones are removed tools
  (`tools/punch_list.py`), renamed documents (`docs/PLANNING.md`), glob
  patterns (`subprojects/*/uv.lock`), git refs (`origin/`) and illustrative
  filenames; 111 of the 143 are in closed items.
- **Item briefs have no `#` headings at all**, so `_headings` returns `[]` for
  every one of them and each `"X" above|below` written inside an item fails
  automatically. They mark their sections with `**Bold.**` instead.
- **The widened set reaches two latent crashes in `_resolves`**: `ValueError:
  '**' can only be an entire path component`, and `NotImplementedError:
  Non-relative patterns are unsupported`. Either aborts `doc_check` rather
  than reporting anything. Captured as `PL-0M7L`.
- **`check_math_delimiters` is not affected either way.** Its docstring says
  it walks every markdown file rather than `DOC_GLOBS`, and it does, so the
  **Watch for** paragraph's worked example is already answered. The two real
  consumers of `read_docs` are `check_citations` and `check_make_targets`,
  plus `cmd_candidates`; only the first wants items.

**The decidable defect is in the pattern, not the globs.** `CITATION_RE` has
two gaps, and together they are what hides the surviving `PL-8B1K` instance:

1. No branch matches the **document-qualified** form this project actually
   writes - a path in a code span, then the section:

   ```text
   `docs/WORKING_NOTES.md`, "Splitting error outside the gate's operating point"
   ```
2. Both existing branches quote as `[^"\n]+`, so a section name that wraps
   across a source line cannot match. This repository hard-wraps prose at
   about 78 characters, so a long section title is invisible to the check
   **in the documents it already reads**, not only in the ones it does not.
   Captured as `PL-X94L`; it is the more serious of the two, because it is a
   live check reporting success over text it never examined.

**Counted alternative.** A document-qualified branch, made newline-tolerant,
run over `DOC_GLOBS` + `docs/items/*.md` + every `.py` module, class and
function docstring, and applied to **section citations only**, yields **9**
hits across the whole tree. Three are the same `PL-042` citation quoted by
`PL-8B1K` and by this item as the example of the defect, which needs an
exemption or a fenced block; one is a pattern artifact to tighten. The rest
are genuine. That is the shape `CLAUDE.md` asks for - the decidable half in
code, and a signal a reader acts on - against roughly 160 findings of which
five are real if the globs are widened instead.
