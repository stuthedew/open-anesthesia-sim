---
id: PL-T7PY
title: Four item files still gloss the Qt port as v0.5.1 in their deferral blockquote while the citation beneath it reads ROADMAP.md section v0.4.25, so the header and its own citation disagree: PL-7J96, PL-F0L8, PL-NC2P, PL-027
priority: P3
effort: S
status: done
classes: docs
feature: release-roadmap-seam
milestone: v0.4.25
touches: docs/items/
added: 2026-09-14
closed: 2026-09-14
pr: 576
verify: '! grep -rq "^> \*\*The Qt port (.v0.5.1.) moots" docs/items/'
---

**Problem.** Four item files still gloss the Qt port as v0.5.1 in their deferral blockquote while the citation beneath it reads ROADMAP.md section v0.4.25, so the header and its own citation disagree: PL-7J96, PL-F0L8, PL-NC2P, PL-027

**Fixed 2026-09-14 inside `PL-YVM1`'s sweep**, which found the same defect at
fifty-one more places and adopted the rule that closes it: the blockquote now
opens "The Qt port moots or transforms this" and the citation beneath it is
the only place a version appears, where `tools/doc_check.py` checks it.
