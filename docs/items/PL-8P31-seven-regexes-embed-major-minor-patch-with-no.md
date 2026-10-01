---
id: PL-8P31
title: Seven regexes embed MAJOR.MINOR.PATCH with no exported pattern to read - doc_check twice, branch_id_check, roadmap three times and model's MILESTONE_BLOCKER_RE - because docket.release exports only the anchored SEMVER_RE, so each spells the version grammar itself
status: untriaged
feature: read-facts-through-docket
touches: subprojects/docket/src/docket/release.py, tools/doc_check.py, tools/branch_id_check.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/model.py
added: 2026-10-01
---

**Problem.** Seven regexes embed MAJOR.MINOR.PATCH with no exported pattern to read - doc_check twice, branch_id_check, roadmap three times and model's MILESTONE_BLOCKER_RE - because docket.release exports only the anchored SEMVER_RE, so each spells the version grammar itself

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/doc_check.py:583` (`LIST_VERSION_RE`) and `:1974` (`SELF_CLEARED_GROUP_RE`); `tools/branch_id_check.py:156` (`RELEASE_RE`); `subprojects/docket/src/docket/roadmap.py:98`, `:172` and `:323`; `subprojects/docket/src/docket/model.py:146` (`MILESTONE_BLOCKER_RE`). `release` exports only the anchored `SEMVER_RE`, so `.claude/rules/apparatus-standard.md` § "Read the fact from its record; where none exists, write one" points the fix at an exported token pattern each of these reads.
