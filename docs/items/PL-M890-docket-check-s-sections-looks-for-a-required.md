---
id: PL-M890
title: docket check's _sections looks for a required brief heading's closing ** anywhere below it rather than on its own line, so a heading that never closes reads the next heading's words as its own text - where its comment says a heading that never closes has nothing under it - and brief_gaps passes it whenever any bold text follows; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a required heading that never closes is reported as having nothing under it, whatever bold text follows it
verify: grep -qF '"brief sections, ' tests/unit/test_doc_check.py
---

**Problem.** docket check's _sections looks for a required brief heading's closing ** anywhere below it rather than on its own line, so a heading that never closes reads the next heading's words as its own text - where its comment says a heading that never closes has nothing under it - and brief_gaps passes it whenever any bold text follows; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`checks.py`. `_sections` finds each required heading of a brief, then its
closing `**` with `scan.find` from the heading's end to the end of the brief.
The brief's headings are read a line at a time by design (`PL-6G8T`), so the
closer can only be on the heading's line, and emphasis pairs only within one
block's inline content (CommonMark 0.31.2 § 6.2), which a blank line ends
(§ 4.8). The function's own comment gives the intended answer: a heading that
never closes has nothing under it.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0:

```text
**Problem.** x

**Why it matters.** y

**Done when. The suite passes.

**Generator check.** None.
```

The Done-when section's text read as the next heading's words, from `Generator
check.` on, and `brief_gaps` reported no gap. The same unclosed heading placed
last read as empty text and `brief_gaps` reported the missing Done-when, so one
fault is reported or not by whether any bold text follows it. markdown-it reads
the unclosed line as a paragraph with a literal `**`, and the next heading as a
paragraph of its own. `_stub_above_brief` reads `_sections` and misses an
unclosed stub heading the same way. Latent: no required heading in the store
closes outside its own paragraph.

**Why it matters.** `brief_gaps` refuses an item missing a required section, so an unclosed heading passes or fails by whether any bold text happens to follow it, and `_stub_above_brief` misses an unclosed stub heading the same way.

**Generator check.** A member of `PL-R417`: a reader searches for the end of a
statement past the line, and the paragraph, that holds it.

**Done when.** `_sections` looks for the closer on the heading's own line, as
its comment says, pinned by a `brief sections, ` case in `PL-R417`'s guard for
both placements, failing on today's reader.
