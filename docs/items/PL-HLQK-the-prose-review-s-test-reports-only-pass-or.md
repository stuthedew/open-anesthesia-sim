---
id: PL-HLQK
title: The prose review's test reports only pass or fail, so nothing shows how often a run agrees with the owner's verdicts on the paragraphs he rejected and on those he named gold standards
priority: P3
effort: S
status: ready
classes: feature
feature: reader-tested-prose
touches: tools/rejected_prose.py, tests/unit/test_rejected_prose.py
added: 2026-11-03
payoff: a change to the prose review's prompt shows whether it moved the review closer to the owner's verdicts or further from them
verify: grep -q 'def test_check_prints_agreement_for_each_run' tests/unit/test_rejected_prose.py
---

**Problem.** `python3 tools/rejected_prose.py check` reports whether each run
of the current prompt judged every entry as the owner did. It does not say how
close a failing run came, or how a passing run did on each kind of entry. Once
the set holds paragraphs the owner named gold standards (`PL-556C`), the
useful number is the run's agreement with his verdicts: how many rejected
paragraphs it flagged and how many gold standards it kept, out of how many of
each.

This is change 2 of the three that `PL-556C` proposed. The owner approved
change 1 on 2026-11-03 at 03:00Z, on the recommendation that changes 2 and 3
wait until the set holds paragraphs he has named gold standards. Change 3, an accepted version's length as the target for
a rewrite, was already in place through `PL-CWRZ`'s accepted rewrite.

**Why it matters.** A model used as a judge is checked by its agreement with
human verdicts (Zheng L, Chiang WL, Sheng Y, et al. Judging LLM-as-a-Judge
with MT-Bench and Chatbot Arena. NeurIPS 2023 Datasets and Benchmarks Track.
https://arxiv.org/abs/2306.05685, sections 3 and 4). Pass or fail hides
whether a change to the prompt moved the review closer to the owner or further
from him when both runs fail.

**Wait for.** At least one entry in `docs/prose-review/gold/`. With only
rejected entries, agreement is the share flagged, which pass or fail already
shows.

**Done when.** `check` prints, for each run of the current prompt, how many
rejected entries it flagged and how many gold-standard entries it kept, each out of
how many it read.

**Generator check.** One-off: work the owner approved on 2026-11-03 as change 2 of `PL-556C`.

**Triaged 2026-11-03 at `ready`, not `blocked`.** It waits on the owner naming a gold standard, and `blocked-by` takes only an item, a milestone or a date. `docs/prose-review/gold/` held only `.gitkeep` that day. A session that starts this item checks that folder first, and leaves the item if it is still empty.
