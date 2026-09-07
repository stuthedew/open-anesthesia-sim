---
id: PL-5GBV
title: Two items were filed three days apart for one defect and both reached ready and entered the frozen v0.5.0 gate, which counted the same work twice
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-07
verify: uv run pytest -q subprojects/docket/tests/test_cli.py && grep -q 'def test_triage_names_an_open_item_with_a_near_identical_title' subprojects/docket/tests/test_cli.py
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

**A second live instance, found 2026-09-07 by the `PL-2B7B` triage pass.**
`PL-BKDP` and `PL-KFWL` were filed hours apart the same day, from two sessions,
for one event - the `v0.4.8` tag pushed onto a commit where no release was cut.
`PL-BKDP` reached `P1 - needs-decision` and `PL-KFWL` arrived untriaged, so the
pair was invisible until a `bin/docket status` read happened to print both
features. `PL-YMW8` carries that close-out.

It is the harder case for the check proposed here, and worth designing against
rather than around: the two titles share no distinctive run of words at all
beyond the version string `v0.4.8`. One leads with the tag and the commit, the
other with the tag and `doc_check`. A comparison over unusual word runs would
have found this only on `v0.4.8` itself - which argues for treating a shared
rare token (a version, an id, a file path) as a candidate signal in its own
right, not only a shared phrase.

**Done when.** Two open items describing the same defect are surfaced to a
reader before both are triaged to `ready`, without the tool claiming to decide
that they are the same.
