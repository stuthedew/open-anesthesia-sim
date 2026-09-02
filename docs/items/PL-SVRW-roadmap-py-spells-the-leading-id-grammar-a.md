---
id: PL-SVRW
title: roadmap.py spells the leading-id grammar a second time, which vcs.py's own comment says must not happen
priority: P3
effort: S
classes: infra
status: ready
feature: dev-tooling
touches: subprojects/docket
not-delegable: Touches subprojects/docket, and the question is whether two implementations of one grammar agree in every case rather than whether a command passes.
added: 2026-09-02
---

**Problem.** `vcs.py` and `roadmap.py` each define their own `leading_ids`
over the same idea — the run of item ids a line opens with. `vcs.py:158`
returns `list[str]` from `LEADING_IDS_RE`; `roadmap.py:422` returns
`tuple[str, ...]` from its own pattern. Neither imports the other.

**Why it matters.** `vcs.py` states the rule that forbids this, a few lines
below its own copy, about a different constant: *"The id grammar comes from
`store` rather than being spelled again here: two spellings of it would drift,
and the one that drifted would silently stop recognising items."* That is
exactly the exposure here, and drift is silent in the direction that matters —
`docket flight` and `docket next` would keep working while quietly disagreeing
with the release train about which ids a subject names.

Found while making `vcs.leading_ids` public so `tools/pr_title_check.py` could
reuse it instead of respelling it a third time (`PL-2XTF`). The third spelling
was avoided; these two remain.

**Where.** `subprojects/docket/src/docket/vcs.py:158` and
`subprojects/docket/src/docket/roadmap.py:422`.

**Not urgent.** Both are exercised by their own suites and agree today. This is
a consolidation, not a live defect, which is why it is `P3` rather than filed
as one.

**Done when.** One implementation of the leading-id grammar exists, both
callers use it, and the return type difference is resolved rather than
papered over at the call sites.
