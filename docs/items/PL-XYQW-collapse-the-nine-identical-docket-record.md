---
id: PL-XYQW
title: Collapse the nine identical docket record advisories that fire on every healthy run
priority: P3
effort: S
status: ready
classes: infra
feature: queue-hygiene
touches: subprojects/docket
added: 2026-09-13
verify: grep -q 'def test_the_record_advisory_names_every_owed_item_once' subprojects/docket/tests/test_checks.py && uv run pytest subprojects/docket/tests/test_checks.py
root-cause-of: PL-W7WL, PL-3HMQ, PL-K4BN, PL-66X4, PL-2M5T, PL-WXX8
generator: live - pr: is stored though closures_on_base derives it, so every writer and reader of the lag breeds a defect; PL-K4BN on 09-22 is the latest (PL-KVDK)
---

**Problem.** Collapse the nine identical docket record advisories that fire on every healthy run
**Why it matters.** The `record` advisory prints one full paragraph per item
owed a pull request number, and every paragraph is the same sentence with a
different id in front of it. The capture saw nine; `bin/docket check` on
2026-09-13 reported seven advisories of which two were this one. The count is
not the point - the repetition is. `CLAUDE.md` says a check earns its place
every run or it is retired, and that an advisory firing so routinely that nobody
reads it is a candidate for retirement rather than promotion. Nine identical
paragraphs on a healthy run train a session to skim the advisory block, which is
where a real finding also appears. The advisory itself is worth keeping: the
remedy is one command and it is genuinely owed.

**Done when.** The `record` advisory prints once, naming every item owed a
number in a single line with the remedy stated once; a test in
`subprojects/docket/tests/test_checks.py` pins the multi-item case; and the
advisory total `bin/docket check` reports counts it as one finding rather than
one per item.
