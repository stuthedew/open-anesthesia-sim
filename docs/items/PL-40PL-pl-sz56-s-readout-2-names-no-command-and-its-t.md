---
id: PL-40PL
title: PL-SZ56's readout 2 names no command and its t=0 figures cannot be reproduced by any counting method
priority: P2
effort: S
status: ready
classes: docs, infra
feature: planning-cadence
touches: docs/releases/v0.3.0.md, docs/items/PL-SZ56-assess-the-v0-3-0-loop-trial-against-its-pre.md
added: 2026-09-02
verify: python3 tools/doc_check.py check && grep -qF 'How readout 2 is counted' docs/releases/v0.3.0.md
---

**Problem.** `PL-SZ56` pre-registered five readouts for the v0.3.0 loop trial.
Readouts 1, 4 and 5 name the command that produces them. Readout 2 - net queue
change, the one whose threshold decides whether "the loop generates work faster
than it clears it" - names none, and its recorded t=0 figures (141 items in,
104 closed, net +37, against 70 shipped) cannot be reproduced.

**Two counting methods, and the readout used one for the baseline and the other
for the score.** Measured 2026-09-02 on this checkout:

| Method | v0.2.7..v0.2.8 (t=0) | v0.2.8..v0.3.0 (scored) |
| --- | --- | --- |
| Front-matter dates, whole days | 140 in / 102 closed (+38) | 117 in / 84 closed (+33) |
| `git log <a>..<b> --diff-filter=A` over `docs/items/` | 95 in / 83 closed | **57 in** / 38 closed |
| Recorded in the item / release notes | **141 in / 104 closed (+37)** | **57 in / 37 closed (+20)** |

The scored figure matches the git method almost exactly - 57 is what
`git log v0.2.8..v0.3.0 --diff-filter=A --name-only --pretty=format: -- docs/items/`
returns, and `git log v0.2.8..v0.3.0 -p --pretty=format: -- docs/items/ | grep -c '^+closed:'`
returns 38 against the recorded 37. The t=0 figure matches the front-matter-date
method almost exactly - 140 and 102 against 141 and 104 - and is nowhere near
what git returns for the same window. So the baseline and the comparison were
produced by different rules, and the readout subtracts one from the other.

**A third problem sits underneath both.** The windows are tag to tag - `v0.2.8`
is 2026-09-01 18:57 -0500 and `v0.3.0` is 2026-09-02 13:01 -0500, about
eighteen hours spanning two calendar days - while `added:` and `closed:` are
day-granular. No method reading those fields can resolve a sub-day boundary at
all, which is why the front-matter count for the scored window (+33) and the
recorded score (+20) are not close.

**Why it matters.** Readout 2 was scored "Pass, at the threshold": +20 against
a threshold of <= +20. There is no headroom, so the disposition rests entirely
on a counting rule that is not written down, and the one alternative rule a
reader would reach for scores +33, which fails. `PL-SZ56` exists specifically
to stop the loop being assessed by criteria chosen after the outcome is known,
and it names its own confounds carefully; an unstated counting rule on the one
readout scored at its boundary is the same failure arriving by a different
route. `PL-SZ56` also records that "Gate 1, 2 and 3 will each want this
readout", so the rule is reused three more times unless it is fixed now.

**Approach.** Do not re-open `PL-SZ56` - it is closed and shipped in v0.3.0.
Write the counting rule into `docs/releases/v0.3.0.md`'s `## Loop trial`
section, where the score already lives, as a `**How readout 2 is counted.**`
paragraph: the exact command, what it includes, and what it does not. Prefer
the git-based rule, because it resolves the tag-to-tag window that the date
fields cannot, and note its known imprecision - a renamed item file counts as
an addition, which is the likely source of the 38-against-37 discrepancy.
Then re-score t=0 under the same command so the two ends of the comparison are
commensurable, and say plainly whether the pass survives. If it does not, say
that too: the readout is more useful failing honestly than passing on an
unstated rule.

**Where.** `docs/releases/v0.3.0.md`, `## Loop trial`. The `PL-SZ56` item file
gets a pointer to the recorded rule so the next gate reads it rather than
re-deriving one.

**Done when.** `docs/releases/v0.3.0.md` states the command that produces
readout 2, both windows are counted by that same command, and the v0.3.0
disposition is restated - held or reversed - against the recomputed baseline.
