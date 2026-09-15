---
id: PL-J7MM
title: assets/branding/ has held only a .gitkeep since the bootstrap commit and nothing in the tree references it
priority: P3
effort: S
status: done
classes: infra
touches: assets
added: 2026-09-15
closed: 2026-09-15
pr: 589
verify: python3 tools/doc_check.py check && ! test -e assets/branding
---

**Problem.** assets/branding/ has held only a .gitkeep since the bootstrap commit and nothing in the tree references it
