---
id: PL-G424
title: Apparatus-side citation drift has no generator head: 27 open items name a tree fact that moved, and PL-4FBP's adopted scope reaches only docs/MODEL.md and README.md
priority: P2
effort: M
status: needs-decision
classes: docs, infra
feature: generator-heads
touches: tools/doc_check.py, docs/items, docs/WORKING_NOTES.md
added: 2026-09-19
root-cause-of: PL-037Y, PL-245B, PL-4HKS, PL-5748, PL-60CQ, PL-75R0, PL-DL4M, PL-MSFB, PL-2GQW, PL-38PN, PL-JXVD, PL-5F26, PL-8T3Z, PL-Z5FG, PL-YZKK, PL-CPLX, PL-WVJ0, PL-21RC, PL-6QZP, PL-QV5Y, PL-880Z
---

**Problem.** `PL-4FBP` established that a document sentence's link to the tree
lives only in the reader's head, and closed 2026-09-19 having fixed the
**product** half: its adopted clause 1 binds the convention to `docs/MODEL.md`
and `README.md`, and its brief states the scope limit outright — "the apparatus
files are not [held to the specialist standard]". That limit was right for what
it decided. It leaves the same mechanism ungoverned on the other side of the
boundary.

A measurement pass on 2026-09-19 clustered the 151 open workflow-lane items by
cause. The largest cluster, at **31 items**, is a doc or brief sentence naming a
tree fact that has since moved. Only **4** of them (`PL-BHJW`, `PL-0R06`,
`PL-C7XV`, `PL-LM8P`) fall inside `PL-4FBP`. The remaining **27 have no head at
all**, and name:

```
 7  docs/items            7  docs/WORKING_NOTES.md      7  individual item briefs
 1  .claude/skills/docket/SKILL.md   1  CLAUDE.md   1  .claude/rules/expert-review.md
```

Store-wide, 28 open items name `docs/items`, 14 name `docs/WORKING_NOTES.md`,
and 11 declare another item's *file* as their `touches`.

**Why it matters.** This is the shape `CLAUDE.md` ranks above everything but
`P0`: a mechanism whose instances are filed and repaired one at a time while
the cause stands. Each of the 27 is a patch. At the workflow lane's measured
self-generation rate of 0.696 — multiplier 3.29 — working them as individual
items entails roughly 89 items of eventual work.

It is also the specific failure the project owner asked to be watched for
(2026-09-19): "an unknown issue that is generating additional bugs that we are
just patching other than fixing the upstream issue". This one is no longer
unknown, and it was invisible to the tooling that should have caught it —
`tools/generator_check.py` is 0-for-7, all seven recorded generators having come
from a manual sweep, and its own docstring records that it "reported **no**
cluster on this tree while `PL-6ZQY` had already named **six**".

**Enumerated 2026-09-19, against the tree.** The commissioned apparatus backlog
review read all 166 open workflow-lane items and checked each against the tree.
`root-cause-of:` now names **21 members**, each one a sentence in an apparatus
document asserting a tree fact that is wrong — verified individually, not
inferred from the clustering pass that produced the count of 27:

| Where the wrong sentence sits | Members |
| --- | --- |
| `docs/WORKING_NOTES.md` (8) | `PL-037Y`, `PL-245B`, `PL-4HKS`, `PL-5748`, `PL-60CQ`, `PL-75R0`, `PL-DL4M`, `PL-MSFB` |
| another item's brief (7) | `PL-2GQW`, `PL-38PN`, `PL-JXVD`, `PL-5F26`, `PL-8T3Z`, `PL-Z5FG`, `PL-YZKK` |
| `.claude/skills/docket/SKILL.md` (2) | `PL-CPLX`, `PL-WVJ0` |
| `CLAUDE.md` and `.claude/rules/` (2) | `PL-21RC`, `PL-6QZP` |
| `Makefile` (1) | `PL-QV5Y` |
| item briefs plus `ROADMAP.md`'s frozen gate (1) | `PL-880Z` |

`PL-880Z` is the one that reaches outside the apparatus, and it is kept because
it is the same mechanism one level up: `PL-XLQ5`'s wrong title is copied
verbatim into `ROADMAP.md:2229` as a frozen gate entry, so the wrong description
carries the standing of a frozen decision. Its own brief independently names
four of this set — "`PL-38PN`, `PL-JXVD`, `PL-TTMF`, `PL-8T3Z` are all the same
shape" — which is corroboration written before this enumeration existed.

**Four exclusions, each deliberate.** `PL-BHJW`, `PL-0R06`, `PL-C7XV` and
`PL-LM8P` are inside `PL-4FBP`'s `root-cause-of:` already and are not claimed
twice. `PL-038` and `PL-1T6T` were considered and left out: their subject is a
`CLAUDE.md` sentence asserting a fact about the *Claude Code runtime* that was
never checked, rather than a tree fact that moved — the same family, but no
route this head can build reaches it, since `doc_check` cannot resolve a claim
about the harness. `PL-TTMF` was a member and was **dropped** by the same sweep,
overtaken.

**The set is 21 rather than 27 because the sweep dropped and re-read.** Of the
166 open workflow-lane items, 12 were dropped as dead (7 overtaken, 5 never an
issue); the rest of the gap is the clustering pass having counted items whose
subject is a missing *check* rather than a drifted *sentence*, which belong to
whatever route this item chooses rather than to its member list.

**Decision needed.** Which of three routes governs apparatus-side citation
drift — they differ in where the rule lives:

1. **Extend `tools/doc_check.py` across the apparatus documents**, applying
   `PL-4FBP`'s live-versus-dated-assertion convention to `CLAUDE.md`,
   `.claude/rules/*`, `SKILL.md`, `docs/WORKING_NOTES.md` and item briefs. The
   mechanism already exists; this is a scope change to the paths it reads.
2. **Bound the surface instead of checking it** — make the apparatus documents
   cite less, so there is less to drift. The cheapest version of this is that a
   brief names an id and never restates what that id says.
3. **Accept drift in item briefs specifically** and check only the standing
   documents. A brief is written once for one piece of work and is arguably
   allowed to age with it; `docs/WORKING_NOTES.md` and the resident files are
   not.

Route 1 is the obvious extension and the most expensive; route 3 is the
cheapest and concedes 14 of the 27. The choice turns on whether a closed item's
brief is a historical record or a live assertion, which nothing in the project
has decided.

**Done when.** The route above is chosen and recorded; the cluster is enumerated
so this item carries a `root-cause-of:` naming its members (three or more, per
`CLAUDE.md`, or it is an ordinary item and this head should be dropped); and
whatever the chosen route requires is in place and proved by a command — for
route 1, `tools/doc_check.py` reading the apparatus documents with a test
pinning it; for routes 2 and 3, the scope decision written where a session
reading a brief will meet it, since a convention nobody loads changes nothing.

**Note for triage.** Filed `untriaged` deliberately. Setting `needs-decision`
here would make it debt under "The debt gate" and leave it undispositioned
against v0.5.0's frozen list — a gate frozen 2026-09-06 and now down to 2 open
entries of 175 — which is the growth freezing exists to prevent. This is
`docs`/`infra`-classed and neither `safety` nor `science`, so it is deferrable;
when triage seats it, it needs either a place on a later gate or a
`### Declined to Gate ...` entry saying why, per the disposition rule. **Do not
drop it as stale in the apparatus backlog sweep** — the cluster it names was
measured on 2026-09-19 and the mechanism is live.
