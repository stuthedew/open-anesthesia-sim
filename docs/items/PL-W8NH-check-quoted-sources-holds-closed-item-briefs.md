---
id: PL-W8NH
title: check_quoted_sources holds closed item briefs to current prose, which the ratified citation-drift rule says is not a finding, so the first `§` citation to drift in a done brief hard-fails make check on a non-finding
status: dropped
added: 2026-09-21
closed: 2026-09-21
reason: Duplicate of PL-ZM8P, which diagnosed the same defect from the release cut that hit it and is already done on origin/claude/serene-heisenberg-x0tycm (v0.5.1)
---

**Problem.** check_quoted_sources holds closed item briefs to current prose, which the ratified citation-drift rule says is not a finding, so the first `§` citation to drift in a done brief hard-fails make check on a non-finding

**Mechanism.** `_quoting_sources` in `tools/doc_check.py` yields every
`docs/items/*.md` with no status filter, and `check_quoted_sources` then
requires the quoted text to be in the cited file *now*. A brief at `done` or
`dropped` is a historical record: it says what was true when the work was done.
`.claude/rules/citation-drift.md` (project owner, 2026-09-19, ratified) decides
exactly this - drift in a closed brief is not a finding, is not to be repaired,
is not to be filed against, and is not to be counted when sizing a cluster.

**Why it matters.** The two have not collided yet only because no `§`-form
citation in a closed brief has drifted; the check reports zero errors on
2026-09-21. The first one that drifts hard-fails `make check`, and the remedy
it implies is to repair a closed brief, which the ratified rule forbids. A
check that refuses correct content is one `CLAUDE.md` retires rather than
teaches around, and this one would refuse it on a rule the project had already
written down. The check shipped in `#451`; the rule was ratified afterwards and
nobody reconciled them.

**Measured 2026-09-21.** Admitting the possessive to `CITATION_CONNECTIVE` as
an experiment - see `PL-316G`, which holds the full measurement - produced 40
errors, **34 of them in `done` or `dropped` briefs**. That is the size of the
collision this check is one drift away from, and it is why `PL-316G`'s
recommended shape carries the exemption rather than the repairs.

**Done when.** `check_quoted_sources` skips briefs whose `status` is `done` or
`dropped`, `tests/unit/test_doc_check.py` holds a closed brief quoting absent
text through a clean run and the same quotation in an open brief as reported,
and the exemption names `.claude/rules/citation-drift.md` as its authority.

## Dropped 2026-09-21: `PL-ZM8P` had it first, and better

Filed from `PL-316G`'s measurement, where the collision was still latent - 34
of 40 findings in closed briefs, but zero errors on the tree, so the argument
was that the first `§` citation to drift would hard-fail on a non-finding.

`PL-ZM8P`, filed the same day on `origin/claude/serene-heisenberg-x0tycm` while
cutting v0.5.1, reached it from the other end: the cut *hit* it. `ROADMAP.md`'s
`## Current baseline` section is replaced wholesale at every release, so every
heading in it is guaranteed to vanish at the next cut, and `PL-DL4M` - closed
in that same release - went red quoting two of them. That is a sharper
diagnosis than this item's, because it names why the collision is periodic
rather than merely possible, and it identifies the real defect as the two
checks disagreeing: `check_line_citations` already went through
`_live_item_briefs`, and `check_quoted_sources` globbed every brief.

It is fixed there: `_quoting_sources` now yields `_live_item_briefs(root)`, so
both checks draw the same line from the same helper, with a second test holding
the exemption narrow. Nothing is left for this item to do.
