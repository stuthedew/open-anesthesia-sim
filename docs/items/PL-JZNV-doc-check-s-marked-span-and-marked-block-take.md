---
id: PL-JZNV
title: doc_check's _marked_span and _marked_block take the paragraph a provenance, derived or absent marker sits under as every non-blank line above it, so a list item or heading with no blank line before the marked paragraph is read into it: a number or path there satisfies a marker its own paragraph fails, and a stray backtick there hides the marked paragraph's own citation; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a provenance, derived or absent marker is checked against its own paragraph, never a list item or heading above it
verify: grep -qF '"marked span, ' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _marked_span and _marked_block take the paragraph a provenance, derived or absent marker sits under as every non-blank line above it, so a list item or heading with no blank line before the marked paragraph is read into it: a number or path there satisfies a marker its own paragraph fails, and a stray backtick there hides the marked paragraph's own citation; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), by the auditors
of both halves of `tools/doc_check.py`. `docs/MODEL.md` says a marker's stated
value is checked against the paragraph the marker sits under, and that
paragraph is one CommonMark 0.31.2 paragraph (§ 4.8), which also begins after a
list item's start, a heading, a table or a fence's close (§ 4.2, § 5.2), not
only after a blank line. `_marked_span` and `_marked_block`, read by
`check_prose_provenance` and `_absent_paths`, take every non-blank line above
the marker. `_absent_paths` then pairs code spans with `CODE_SPAN_RE` over that
whole span joined, so its backticks pair across the list items it holds.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0. A data file holding 0.65, and a tight list whose
second item carries, on the next line indented two spaces, a provenance marker
stating that coefficient as 0.65:

```text
- Sevoflurane is 0.65.
- Desflurane is 0.42.
```

`check_prose_provenance` reported nothing; markdown-it puts the marker in the
second item, whose paragraph holds 0.42, and with a blank line between the
items `doc_check` reports that the number is not in it. A heading reading
`Coefficient 0.65` directly above a paragraph saying 0.42 passes the same way,
and an absent marker under a second item passes on a path only the first item
cites. The other direction: with the first item writing a stray backtick in
prose and the second citing `tools/gone.py`, deleted, under an absent marker
naming it, `_absent_paths` reported that the paragraph above does not cite the
path, since the stray backtick paired with the second item's opening one;
markdown-it gives the second item the code span `tools/gone.py`. Latent: all
77 tracked markers' spans equal markdown-it's paragraph, and none of the 13
absent markers across 348 sources reads differently.

**Why it matters.** `docs/MODEL.md` holds a provenance, derived or absent marker to the paragraph it sits under, so read past that paragraph a marker's stated value is satisfied by a neighbouring list item or heading, and a stray backtick above it hides the paragraph's own citation.

**Generator check.** A member of `PL-R417`: a reader reads past the start of
the statement it means, the marker's own paragraph, which is the shape of
`PL-FP7J` (a paragraph ended only at a blank line) in two readers that fix did
not list. `PL-GT0J` covered a marker split across lines.

**Done when.** The marked paragraph is the prose block `docket.markdown`
reads as ending nearest above the marker, passing over blank lines and sibling
marker blocks, and `_absent_paths` pairs code spans within it, pinned by a
`marked span, ` case in `PL-R417`'s guard for the tight list, the heading and
the stray backtick, each failing on today's reader.
