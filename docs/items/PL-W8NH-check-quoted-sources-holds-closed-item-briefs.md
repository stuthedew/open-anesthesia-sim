---
id: PL-W8NH
title: check_quoted_sources holds closed item briefs to current prose, which the ratified citation-drift rule says is not a finding, so the first `§` citation to drift in a done brief hard-fails make check on a non-finding
status: untriaged
added: 2026-09-21
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
