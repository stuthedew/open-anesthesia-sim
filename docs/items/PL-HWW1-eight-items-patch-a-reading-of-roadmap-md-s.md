---
id: PL-HWW1
title: Eight items patch a reading of ROADMAP.md's prose because milestone membership is scraped rather than recorded: decide whether it becomes a recorded fact
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: generator-heads
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/plan.py, ROADMAP.md, docs/items
added: 2026-09-17
root-cause-of: PL-4PC5, PL-C4RS, PL-7CSP, PL-B5DW, PL-Y1L0, PL-J45M, PL-SVRW, PL-6P9Y
---

**Problem.** Scope membership is inferred by scraping item ids out of
`ROADMAP.md`'s prose under a fixed heading vocabulary, with no representation
of exclusion and none of arrangement. The roadmap's own decisions about what is
*not* in a milestone cannot reach the ranking, two structures can disagree
about what is, and a section's position in the document is read as a fact about
the release train. Eight open items correct one reading each.

**Why it matters.** This is `PL-6ZQY`'s mechanism - *the apparatus infers a
fact it could have recorded* - in the document the `docket` skill tells every
session to read **before** the queue. `bin/docket wave` is that read, and it is
wrong in both directions today: it counts ids cited in a `Required scope`
section's prose as scope entries, so v0.5.0 reads 21 ids against the section's
own stated eighteen (`PL-4PC5`), while a milestone's `### Explicitly out of
scope` list is read as silence, so an id the roadmap has explicitly ruled out
ranks ahead of work nobody has ruled on (`PL-6P9Y`).

The self-generating half is the one that makes it a generator rather than a
bug. Following the roadmap's own citation idiom - naming an id in the prose
around an entry, which is how the document is written for a human reader -
creates a new false scope entry every time somebody re-briefs an entry. So the
count drifts as the document is maintained correctly, and each drift is found
and filed separately.

**Why this item is the head, and no member is.** Confirmed against the store on
2026-09-18. `PL-6P9Y` is the closest candidate and is too narrow by its own
brief - it adds one placement for one heading and records why it is `P3`: "it
moves exactly one id today (`PL-Z7LY`)". `PL-4PC5` attacks the other half but
its outcome is a corrected *count*, so the inference survives it. `PL-C4RS`
says the two "have to land agreeing with each other", which is the shape of a
cluster rather than of a head. Nothing in the store proposes recording
membership instead of parsing it.

**Decision needed.** Whether milestone membership stays a reading of
prose or becomes a recorded fact the roadmap and the tooling share - and if
recorded, where, since `ROADMAP.md` is also the document a person reads. Three
parts, and they may not have the same answer:

- **Membership**, including exclusion, which the parse cannot currently express
  at all (`PL-6P9Y`, `PL-C4RS`, `PL-4PC5`).
- **Arrangement** - which row of the release train a section belongs to, read
  today from its position (`PL-J45M`, `PL-Y1L0`) and from the anchor two
  commands describe differently (`PL-B5DW`).
- **Sequencing** - whether a blocker is scheduled before a gate or scheduled by
  nothing, which `wave` prints identically (`PL-7CSP`).

**The items this explains (8, confirmed 2026-09-18 against each brief).**
`PL-4PC5`, `PL-C4RS`, `PL-7CSP`, `PL-B5DW`, `PL-Y1L0`, `PL-J45M`, `PL-SVRW`,
`PL-6P9Y`.

Seven are the 2026-09-17 candidate list, each re-read and still open. `PL-6P9Y`
is added: the 2026-09-17 pass named it only as a rejected head and never as a
member, and it is the clearest instance of the diagnosis's own "no
representation of exclusion". `PL-SVRW` is the weakest of the eight and is kept
deliberately - `roadmap.py:422` holds a second `leading_ids` spelling because
ids have to be scraped out of a prose document at all, which is the mechanism
producing a duplicate constant rather than a stale count.

**Considered and left out.** The other open items naming `ROADMAP.md` are
stale *statements* rather than mis-parses - `PL-B8V1`, `PL-0VFF`, `PL-C25K`,
`PL-N32Y`, `PL-FV7G` - and they belong to `PL-4FBP`'s cluster (a document
sentence whose link to the tree lives only in the reader's head), where
`PL-B8V1` is already named. The split is worth stating: this cluster is what
the tooling *reads out of* the roadmap, that one is what the roadmap *says*.

**Done when.** The question above is decided; if membership becomes recorded,
the structure exists and `roadmap.py` reads it rather than scraping prose, with
`ROADMAP.md` still readable by a person; and the eight members are re-pointed
at the decision or dropped against it.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found only two with a causing item in the store (`PL-BHVM`,
`PL-L4YG`); this item was filed to record that this cluster had none. On
2026-09-18 it became the head itself rather than a tracker of one, which is the
cheaper of the two endings its own `Done when` offered.
