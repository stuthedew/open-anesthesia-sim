---
id: PL-KZ60
title: docs/machine-survey.md was checked for study-protocol-read-as-practice in section (a2) only, and one of that section's three sources did not support the claim it was cited for
status: untriaged
added: 2026-09-20
---

**Problem.** docs/machine-survey.md was checked for study-protocol-read-as-practice in section (a2) only, and one of that section's three sources did not support the claim it was cited for

Found while closing `PL-NM7X` (the fresh gas flow default), 2026-09-20.

**What was checked, and what it turned up.** `PL-NM7X` commissioned full-text
confirmation of the three sources `docs/machine-survey.md` § "(a2)" cited for
the claim that *"4 L/min is at the high end of contemporary practice rather than
the middle of it"*. Of the three:

- **Kalmar et al.** (PMID 34978655) supports a narrower claim than the one made
  — it is a recommendation, and its 2 L/min comparator is the practice fact.
- **Candries et al.** (PMID 35318567) does not support it. Its 0.2–6 L/min is a
  Gas Man validation study's protocol range.
- **Hoffmann et al.** (PMID 40073301) does not support it and reads the other
  way: an *in vitro* bench protocol whose range contains 4, 5 and 6 L/min,
  settings that paper describes as reflecting clinical conditions.

So one section of the survey, checked once, was resting on one source out of
three. § "(a2)" is now corrected.

**Why that is a finding about the rest of the document rather than a closed
one.** The failure mode is specific and repeatable: reading *a study's chosen
settings* as *a report of practice*. It is the error
`src/anesthesia_sim/data/machines/reference_circle_system.json`'s De Wolf entry
already exists to forestall for its 1 L/min, which is evidence that the project
has met it before. The survey has roughly thirty references across fourteen
buckets, most read at abstract level in one 2026-09-19 session, and **no other
bucket has been checked this way**. Hoffmann et al. is itself cited twice in the
document for two different purposes, which is the shape that makes the slip easy
to make.

**Why it matters.** The survey is a design input: `PL-FG9D`'s machine
abstraction and `docs/machine-abstraction.md` were decided against it, and
`docs/MODEL.md` now cites it. A claim it carries can reach the specification,
which is exactly the route the § "(a2)" sentence took.

**Done when.** Each of the survey's quantitative or normative claims has been
checked against what its cited source actually establishes, at the depth the
claim needs; every entry records its route and depth per
`.claude/rules/citing-sources.md`; and anything a source does not support is
either withdrawn with the withdrawal recorded, or re-sourced. Scope is
`docs/machine-survey.md` alone — the agent and patient data files were audited
separately under `PL-FN5F` and `PL-QBKQ`.

**Not urgent, and not a generator.** It is one bounded audit of one document, it
causes no other open item, and nothing in the simulator computes from the survey
today.
