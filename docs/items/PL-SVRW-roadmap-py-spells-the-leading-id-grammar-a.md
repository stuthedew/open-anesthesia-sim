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

**Problem.** Three readers in docket each spell their own grammar for the run
of item ids a line opens with. `vcs.leading_ids` reads commit subjects and pull
request titles: ids joined by `,`, `&` or `and`, in any case. `roadmap.py`'s
`_leading_ids` reads a debt gate's entries: ids wrapped in `*` or `_` emphasis,
joined by `and` or by whitespace alone. `_declared_ids` walks `DECLARED_ID_RE`
over a `Required scope` entry's `(queue item ...)` slot: ids in backticks,
joined by commas, `and`, or both. All three take the id itself from
`store.ID_PATTERN`; what each spells again is how a run is wrapped and joined.
`vcs.leading_ids` returns `list[str]`, the other two `tuple[str, ...]`.

**Why it matters, re-confirmed 2026-10-01, which changed the shape.** The
filing saw two readers; `_declared_ids` arrived later, with `PL-HWW1`. Its
reason was also a level off:
both modules already take the id grammar from `store`, which is all the quoted
`vcs.py` comment asks, and the release train never reads a commit subject, so
the two cannot disagree "about which ids a subject names". What the copies do
cost, measured over the corpus each reader serves:

- **Each drops the ids another's syntax writes, silently.** Given the 1,578
  subjects on `origin/main`, the gate-entry reader reads 405 differently: 404
  lose the ids a comma or `&` joined, and one gains an id joined by a space
  alone. Given `ROADMAP.md`'s 438 gate entries, the subject reader loses
  `PL-SWFM` from `PL-Z4GF **and PL-SWFM**`. So a gate entry joined the way
  `CLAUDE.md` tells a subject to join ids, `PL-A, PL-B`, would be read as
  `PL-A` alone, and the debt gate would read clearer than it is.
- **One grammar can serve all three, with one exception that is the
  document's meaning rather than its syntax.** A backtick cannot be a wrapper
  for a gate entry: `ROADMAP.md` cites ids as code in the bullets that explain
  a gate, five of them on 2026-10-01, three naming the items v0.6.0 deferred
  *off* its gate, and a reader taking backticks would put those items back on.
  So the slot unwraps its own backticks before reading, and the shared grammar
  takes `*` and `_` around an id and one or more of `,`, `&` and `and` between
  ids, in any case. Ids joined by whitespace alone stop being a run for the
  gate and the slot, as they never were for a subject; nothing in `ROADMAP.md`
  is written that way.

Found while making `vcs.leading_ids` public so `tools/pr_title_check.py` could
reuse it instead of respelling it (`PL-2XTF`).

**Where.** `subprojects/docket/src/docket/vcs.py` (`LEADING_IDS_RE`,
`leading_ids`) and `subprojects/docket/src/docket/roadmap.py`
(`LEADING_ID_RE`, `_leading_ids`, `DECLARED_ID_RE` and the walk in
`_declared_ids`).

**Not urgent.** No line in the tree is misread today. A consolidation, which is
why it is `P3`.

**Done when.** One implementation of the leading-run grammar exists -
`vcs.leading_ids`, which seven modules already import, three of them tools,
rather than a new home beside `store.ID_PATTERN` that would move all seven for
no behaviour; the gate entries and the declaration slot read through it; it
returns `tuple[str, ...]`; and every parse the three readers make of the
current corpus - each gate entry and slot in `ROADMAP.md`, each subject on
`origin/main` - comes out the same before and after.
