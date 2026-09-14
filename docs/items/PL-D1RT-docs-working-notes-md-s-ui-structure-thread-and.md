---
id: PL-D1RT
title: docs/WORKING_NOTES.md's UI-structure thread and PL-037Y still describe the port as following v0.5.0, which the 2026-09-14 reorder makes stale
status: untriaged
added: 2026-09-14
---

**Problem.** docs/WORKING_NOTES.md's UI-structure thread and PL-037Y still describe the port as following v0.5.0, which the 2026-09-14 reorder makes stale

**Found while landing `PL-RKWB`** (the 2026-09-14 decision moving the Qt port
ahead of v0.5.0's display half).

`ROADMAP.md`, the queue and `docs/WORKING_NOTES.md:684` were all re-pointed with
that change. What was not swept is the narrative around planned-milestone item
34, the tiled workspace: `ROADMAP.md` § "Planned milestones" records the timing
question as live against a port that follows v0.5.0, and `PL-037Y` carries a
related UI-structure thread written under the old order. Neither is wrong about
its *substance* - the port still rewrites every layout, and item 34 still waits
on it - but both reason from a sequence that has changed, and § "Planned
milestones" is where a reader goes to find out what is coming.

`tools/doc_check.py` cannot catch this: the citations all resolve, and what is
stale is the reasoning around them rather than any path or section name. That
is the line `CLAUDE.md` draws between the decidable half and the judgment half,
working as intended.

**Done when** item 34's timing paragraph and `PL-037Y` read correctly against a
port that precedes v0.5.0.
