---
id: PL-J7MM
title: assets/branding/ has held only a .gitkeep since the bootstrap commit and nothing in the tree references it
priority: P3
effort: S
status: done
classes: infra
milestone: v0.4.26
touches: assets
added: 2026-09-15
closed: 2026-09-15
pr: 589
verify: python3 tools/doc_check.py check && ! test -e assets/branding
---

**Problem.** assets/branding/ has held only a .gitkeep since the bootstrap commit and nothing in the tree references it

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried this paragraph under item 38, "The project's name and look". In it, "this item" means item 38, and "above" and "below" point within that section as it then stood.

> *There is no placeholder to build on.* `PL-J7MM` removed the empty branding asset directory on 2026-09-15, the day before this was raised. The directory had held one placeholder file since the bootstrap commit, and nothing referenced it. This line is where the intent lives until someone scopes it.
