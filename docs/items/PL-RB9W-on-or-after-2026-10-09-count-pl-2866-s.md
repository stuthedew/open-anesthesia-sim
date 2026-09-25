---
id: PL-RB9W
title: On or after 2026-10-09, count PL-2866's falsifier: apparatus findings that blocked or were captured during product items, against simulator items closed since the 2026-09-25 switch; the blocking rule is wrong above about 1 per 10
priority: P2
effort: S
status: ready
classes: infra
feature: workflow-stress-2026-09
touches: docs/items/PL-RB9W-on-or-after-2026-10-09-count-pl-2866-s.md
added: 2026-09-25
payoff: The owner learns from a count fixed in advance whether letting product sessions defer apparatus findings is costing product work, and so whether product focus's blocking rule should be reopened
verify: grep -q '^\*\*Counted 20' docs/items/PL-RB9W-*.md
---

**Problem.** On or after 2026-10-09, count PL-2866's falsifier: apparatus findings that blocked or were captured during product items, against simulator items closed since the 2026-09-25 switch; the blocking rule is wrong above about 1 per 10

**How.** `PL-2866` pre-registered it. Its blocking rule (an apparatus finding stops a product session only when it blocks it) is wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items. The baseline is 7 apparatus defects found during product work against 72 simulator items closed, 2026-09-15..25, counted by the inflow scripts in `docs/stress-2026-09-25/evidence.tar.gz`. Re-run them over 2026-09-25..10-09 and count two things apart: findings that *blocked* a product item, so it stopped for them, and findings captured during one and deferred. A deferred one that later bit a product session counts against the rule. Not before 2026-10-09, the two weeks the decision named.

**Why it matters.** `PL-2866`'s blocking rule was ratified, so ordinary evidence reopens it, and this count is the evidence it named in advance. Left uncounted, a rule that lets product sessions defer apparatus findings stands whether or not the deferred ones are biting product work.

**Not before 2026-10-09, and how the store says so (triage, 2026-09-25).** The store has no field for a date. `blocked-by` takes an item id or a milestone version only (`subprojects/docket/README.md` § "`blocked` means "not first", and that is the whole of it"), and `model.py`'s `FIELD_ORDER` holds no date field. Adding one would be a new field, which the generator pause holds. So the date rides the title's first words, which `next` and the digest print, and the item is `ready`. A session offered it before 2026-10-09 leaves it: counted early, the window falls short of the two weeks the decision named.

Re-confirmed 2026-09-25 against 46954a81: `PL-2866`'s brief states the falsifier ("wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items"). In the archive, `inflow/classify.py` puts the 7 in discovery class (i), found in or captured by a simulator item. `inflow/inflow.py` hard-codes its window (`D0, D1` and `W0`), and `inflow/run_all.sh` the stress session's scratch paths, so the re-run re-points both.

**Done when.** This brief carries a `**Counted YYYY-MM-DD.**` section with both counts over 2026-09-25..10-09 against simulator items closed in the window: findings that blocked a product item, and findings captured during one and deferred, with how many of those later bit a product session. It says whether the rate is above about 1 per 10. Above it, the blocking rule goes back to the owner as a decision on a new item; at or below it, the count is recorded and the rule stands.

**Generator check.** Bookkeeping: a measurement the owner's decision pre-registered (`PL-2866`), with no misread fact behind it.
