---
id: PL-PFD9
title: Five path-containment tests restate docket.model.is_under: checks's _inside, verify's _within, workflow_paths_check's is_covered and two prefix loops in vcs
priority: P3
effort: S
status: ready
classes: refactor
feature: read-facts-through-docket
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, tools/workflow_paths_check.py, subprojects/docket/src/docket/vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: one answer to whether a path is under a root, so a trailing or leading slash cannot put a file inside one check and outside another
verify: ! grep -qF 'def _inside(' subprojects/docket/src/docket/checks.py && ! grep -qF 'def _within(' subprojects/docket/src/docket/verify.py
---

**Problem.** Five path-containment tests restate docket.model.is_under: checks's _inside, verify's _within, workflow_paths_check's is_covered and two prefix loops in vcs

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `subprojects/docket/src/docket/checks.py:1091` (`_inside`), `subprojects/docket/src/docket/verify.py:1600` (`_within`), `tools/workflow_paths_check.py:186` (`is_covered`), and `subprojects/docket/src/docket/vcs.py:3162` and `:3257`. The sweep reported inputs on which `checks.py`'s and `vcs.py`'s answer differently (a root written with a trailing slash; a `touches` entry with a leading slash), not confirmed here.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
