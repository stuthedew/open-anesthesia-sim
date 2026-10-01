---
id: PL-PFD9
title: Five path-containment tests restate docket.model.is_under: checks's _inside, verify's _within, workflow_paths_check's is_covered and two prefix loops in vcs
status: untriaged
feature: read-facts-through-docket
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, tools/workflow_paths_check.py, subprojects/docket/src/docket/vcs.py
added: 2026-10-01
---

**Problem.** Five path-containment tests restate docket.model.is_under: checks's _inside, verify's _within, workflow_paths_check's is_covered and two prefix loops in vcs

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `subprojects/docket/src/docket/checks.py:1091` (`_inside`), `subprojects/docket/src/docket/verify.py:1600` (`_within`), `tools/workflow_paths_check.py:186` (`is_covered`), and `subprojects/docket/src/docket/vcs.py:3162` and `:3257`. The sweep reported inputs on which `checks.py`'s and `vcs.py`'s answer differently (a root written with a trailing slash; a `touches` entry with a leading slash), not confirmed here.
