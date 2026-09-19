---
id: PL-316G
title: Convert the 150 possessive-form document citations to the section-mark form, which is the only way doc_check can check them without reading prose as a citation
status: needs-decision
added: 2026-09-13
priority: P2
effort: M
classes: docs, infra
feature: dev-tooling
touches: docs/, src/anesthesia_sim/, tests/, tools/, CLAUDE.md, .claude/rules/, ROADMAP.md, README.md
---

**Problem.** Convert the 150 possessive-form document citations to the section-mark form, which is the only way doc_check can check them without reading prose as a citation

**Why it matters.** `PL-V13T` made `doc_check` read the section-mark form, and
the possessive form was deliberately left out because this project writes
`` `CLAUDE.md`'s "..." `` to quote a *sentence* at least as often as to cite a
section - admitting it reported 28 quotations of correct prose as stale
headings. So 150 citations are unchecked by construction rather than by
oversight, and a section rename orphans every one of them silently. That is the
failure `PL-VZL0` exists to prevent, still live over a fifth of the tree's
citations.

**Decision needed.** Whether to convert, and how widely. Converting is not
mechanical: each of the 150 has to be read to say whether it cites a *section*
or quotes a *sentence*, and converting a sentence quotation to `§` would assert
something false. Three shapes:

1. **Convert the simulator half only** - `src/`, `tests/`, `docs/MODEL.md`,
   `docs/ARCHITECTURE.md`, `README.md`. That is where a stale pointer reaches a
   reader of clinical output, which is the whole argument for checking them.
   Smaller diff, and the apparatus keeps a form nobody checks. **This is the
   recommendation.**
2. **Convert everything**, apparatus included. Uniform, and the largest diff -
   it opens `CLAUDE.md` and the rules files, which sit in every session's cached
   prefix.
3. **Convert nothing, and adopt `§` for new citations only.** Costs no diff and
   leaves the 150 unchecked indefinitely; honest only if paired with saying so
   where a session would look.

Expect the conversion to surface stale citations, as `PL-V13T` did - that is
the point rather than a side effect, so budget for the repairs.

**Done when.** Every possessive-form reference inside the agreed scope that is
a section citation reads in the section-mark form:

```text
  `<document>.md` § "Section"
```

every one that quotes prose is left alone and is recognisable as prose, any
staleness the conversion surfaces is repaired, and `make check` is green.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and its count has
grown - but the recommendation's scope was already false when it was written.**
Re-measured today over `*.py` and `*.md`: **211** possessive-form citations
against 782 section-mark ones, where the comment at `tools/doc_check.py:354`
recorded 150 against 353 on 2026-09-13.

The scope this brief recommends - convert the simulator half, "`src/`,
`tests/`, `docs/MODEL.md`, `docs/ARCHITECTURE.md` and `README.md` … that is
where a stale pointer reaches a reader of clinical output" - is **five
occurrences**: `src/anesthesia_sim/app/formatting.py:210`,
`src/anesthesia_sim/core/uptake_system.py:473`,
`src/anesthesia_sim/core/governing_equations.py:66`,
`tests/unit/test_governing_equations.py:8` and
`tests/benchmarks/test_frame_cost.py:17`. `docs/MODEL.md`,
`docs/ARCHITECTURE.md` and `README.md` hold **zero** between them. At the
pre-filing commit `438808b` the same buckets read 3 / 1 / 0 / 0 / 0, because
`PL-VZL0` had already converted `src/core` - see
`src/anesthesia_sim/core/governing_equations.py:317-319`.

So the safety argument for the recommended scope does not hold: 184 of the 211
are in `docs/items/`, which no reader of clinical output opens. The decision
this item still owes should be taken on the queue, not on the simulator - and
whoever takes it should re-measure rather than reuse either number above.
