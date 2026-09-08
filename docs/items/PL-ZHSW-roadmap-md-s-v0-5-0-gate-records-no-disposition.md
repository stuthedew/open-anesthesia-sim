---
id: PL-ZHSW
title: ROADMAP.md's v0.5.0 gate records no disposition for PL-HX5C, so tools/doc_check.py's disposition test fails on origin/main and every branch cut from it
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: planning-cadence
reason: Duplicate of PL-33WM, which recorded PL-HX5C's Gate 2 disposition and merged as #480 at 7bb54673 while this session was measuring the same failure. Kept rather than deleted so the finding is not raised a third time.
touches: ROADMAP.md
added: 2026-09-08
closed: 2026-09-08
not-delegable: Nothing to do - the fix merged on main before this item was triaged.
---

**Problem.** ROADMAP.md's v0.5.0 gate records no disposition for PL-HX5C, so tools/doc_check.py's disposition test fails on origin/main and every branch cut from it

**Dropped.** 2026-09-08. Found by measuring `make check` on this branch, which
was red on `tools/doc_check.py`'s disposition test at `88e9b082`. `PL-33WM`
(record `PL-HX5C`'s gate disposition) had the same finding and merged as `#480`
at `7bb54673` about twenty minutes later, so `origin/main` was already green by
the time this item was triaged. `origin/main` is merged into this branch here
rather than the disposition being written twice.
