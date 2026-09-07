---
id: PL-5GBV
title: Two items were filed three days apart for one defect and both reached ready and entered the frozen v0.5.0 gate, which counted the same work twice
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py
added: 2026-09-07
---

**Problem.** Two items were filed three days apart for one defect and both reached ready and entered the frozen v0.5.0 gate, which counted the same work twice

**Why it matters.** `PL-D188` and `PL-JL2M` describe one defect - `docket new`'s
template stranded above a later-written brief. `PL-JL2M` was captured
2026-09-02 and `PL-D188` on 2026-09-05, both triaged to `ready` with a
`verify:` command each, both classed `defect, infra`, and both frozen into the
v0.5.0 gate. The gate therefore reported 121 entries where 120 were distinct,
and `docket next` would have offered the second to a session that had just
finished the first.

The cost is not the wasted item file, which is nearly free. It is that a gate
is a *count* the project steers by - `docket wave`'s beat line reads "97 of
121 still open" - and a duplicated entry inflates the remaining work in the one
number nobody re-derives. It also splits the reasoning: `PL-JL2M` carried the
better analysis (two candidate fixes, with an argument for one) and `PL-D188`
carried the better evidence (the 2026-09-05 measurement), and a session
starting either would have seen half.

**Where.** `subprojects/docket/src/docket/checks.py`. The decidable part is
narrow and the judgment half is real, so the check must not try to decide
"same defect" - it can only surface candidates. Something like: an open item
whose title shares an unusual run of words with another open item's, reported
as a grooming advisory naming both, for a reader to judge. `docket triage`
already prints each untriaged body, so the cheaper half may simply be to run
the comparison there, where somebody is reading the item anyway.

Note the shape this pair had that a title comparison would have caught: both
titles name `docket new` and a template that is appended to rather than
replaced.

**Done when.** Two open items describing the same defect are surfaced to a
reader before both are triaged to `ready`, without the tool claiming to decide
that they are the same.
