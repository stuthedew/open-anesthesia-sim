---
id: PL-8P31
title: Seven regexes embed MAJOR.MINOR.PATCH with no exported pattern to read - doc_check twice, branch_id_check, roadmap three times and model's MILESTONE_BLOCKER_RE - because docket.release exports only the anchored SEMVER_RE, so each spells the version grammar itself
priority: P3
effort: S
status: ready
classes: refactor
feature: read-facts-through-docket
touches: subprojects/docket/src/docket/release.py, tools/doc_check.py, tools/branch_id_check.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/model.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: the version grammar is written once, so a change to it reaches every reader rather than the one it was made in
verify: ! grep -qF 'r"v(?P<version>\d+\.\d+\.\d+)"' tools/doc_check.py && ! grep -qF 'r"^v\d+\.\d+\.\d+$"' subprojects/docket/src/docket/model.py
---

**Problem.** Seven regexes embed MAJOR.MINOR.PATCH with no exported pattern to read - doc_check twice, branch_id_check, roadmap three times and model's MILESTONE_BLOCKER_RE - because docket.release exports only the anchored SEMVER_RE, so each spells the version grammar itself

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/doc_check.py:583` (`LIST_VERSION_RE`) and `:1974` (`SELF_CLEARED_GROUP_RE`); `tools/branch_id_check.py:156` (`RELEASE_RE`); `subprojects/docket/src/docket/roadmap.py:98`, `:172` and `:323`; `subprojects/docket/src/docket/model.py:146` (`MILESTONE_BLOCKER_RE`). `release` exports only the anchored `SEMVER_RE`, so `.claude/rules/apparatus-standard.md` § "Read the fact from its record; where none exists, write one" points the fix at an exported token pattern each of these reads.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
