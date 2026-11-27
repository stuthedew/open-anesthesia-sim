---
id: PL-9GBS
title: Check whether make release and tools/doc_check.py say they could not answer on a shallow clone: the v0.6.19 cut on a shallow thread checkout asked for no pointer lines in v0.6.18's notes, and after git fetch --unshallow doc_check named #2103 and #2118 as inside v0.6.18's tag span
priority: P2
effort: S
status: ready
classes: defect
feature: release-process
touches: tools/doc_check.py, subprojects/docket/src/docket/release.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: a release cut on a shallow clone says it could not read the history instead of leaving out pointer lines without a word
---

**Problem.** Check whether make release and tools/doc_check.py say they could not answer on a shallow clone: the v0.6.19 cut on a shallow thread checkout asked for no pointer lines in v0.6.18's notes, and after git fetch --unshallow doc_check named #2103 and #2118 as inside v0.6.18's tag span

**Why it matters.** A release cut on a shallow clone may leave out pointer lines that the release notes owe, with no warning. A tool that cannot read history must say so rather than answer as if the history were empty.

**Done when.** The answer is recorded here with its date: whether `make release` and `tools/doc_check.py` each report that they could not read the tag span on a shallow clone. Where one does not, a test shows it now says so.

**Generator check.** The fact is whether the local history is deep enough to answer. `PL-Z1ZT` (a prediction count taken on a shallow clone) is a second reader of it, and is in flight elsewhere; if a third appears, the fact is a generator.
