---
id: PL-CN6L
title: ROADMAP.md's v0.7.0 required scope entry 12 and its definition of done still require fixing the copy editor, which PL-GL45 removed on 2026-11-14; the release cannot meet a done line about a tool that no longer exists
status: untriaged
touches: docs/items/
added: 2026-11-14
---

**Problem.** ROADMAP.md's v0.7.0 required scope entry 12 and its definition of done still require fixing the copy editor, which PL-GL45 removed on 2026-11-14; the release cannot meet a done line about a tool that no longer exists

**Found 2026-11-14** in a review of the night's merges. `ROADMAP.md` § "v0.7.0 - the schematic" still has required scope entry 12, "Fix the copy editor, then make the five `docs/MODEL.md` rewrites that wait on it", and a definition-of-done line, "The copy editor cuts text that its reader does not need and keeps good text as it is, as `PL-HGZS`'s stress test judges." #2149 (`PL-GL45`) removed the copy editor and said in its body that `ROADMAP.md` was "left as history", but the definition of done is a present-tense condition the v0.7.0 cut checks, and nothing can now meet it as written.

Every item entry 12 names (`PL-HGZS`, `PL-HRPK`, `PL-PS5H`, `PL-XBJ3`, `PL-XT53`, `PL-YVL0`) is done, so the entry's work is finished. What is open is the wording: the owner added entry 12 to v0.7.0 (project owner, 2026-11-04), so changing what the release promises is the owner's call.

**Recommendation.** Keep entry 12 as history with one sentence saying the owner removed the copy editor on 2026-11-14 (`PL-GL45`) after its rewrites merged, and replace the done line with "The five `docs/MODEL.md` rewrites that waited on the copy editor have merged", which is true today.

**Done when** `ROADMAP.md`'s v0.7.0 definition of done names nothing the tree no longer holds.
