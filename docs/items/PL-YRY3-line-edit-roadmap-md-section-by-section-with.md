---
id: PL-YRY3
title: Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed

**Why it waits.** The project owner put structure ahead of every line edit (2026-11-07, over keeping restructures for later): no document is line edited before its structure read's findings are applied. `ROADMAP.md`'s restructure lands in nine slices, `PL-W0TS` to `PL-4BCF`. The repository's remaining copy edits wait until the copy editor no longer drops requirements, qualifiers and reasons (`PL-F0Q2`, project owner, 2026-11-07, ratified, over continuing with an audit of each document).

**How.** Run `python3 tools/copy_edit.py --sections ROADMAP.md`, as `docs/prose-review/README.md` § "Reviewing a whole document" step 3 says. Audit each edited section against the text before it for dropped statements, qualifiers, requirements and reasons, as `PL-95SW` did for `docs/MODEL.md`. Then close-out step 8 is satisfied for every slice's changed passages. The run planned on the owner's Mac on 2026-11-05 left out the frozen lists and § "Current baseline". Decide again whether to: a frozen list is a snapshot of what the gate held, and each release cut rewrites the baseline.

**Done when.** Each section of `ROADMAP.md` has been line edited and audited, and each statement the edit dropped is restored or recorded with its reason.
