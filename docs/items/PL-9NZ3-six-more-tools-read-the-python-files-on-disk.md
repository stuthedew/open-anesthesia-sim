---
id: PL-9NZ3
title: Six more tools read the Python files on disk where tracked_files asks git - import_boundary, core_vocabulary and literal_home's _sources, contrast_check.app_modules, agent_identity.read_modules, workflow_paths_check.problems - and doc_check measures nested .claude/rules files that rules_paths_check never reads
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/import_boundary_check.py, tools/core_vocabulary_check.py, tools/literal_home_check.py, tools/contrast_check.py, tools/agent_identity_check.py, tools/workflow_paths_check.py, tools/doc_check.py, tools/rules_paths_check.py, tools/fact_home_check.py, docs/apparatus.md, docs/WORKING_NOTES.md, tests/unit/test_import_boundary_check.py, tests/unit/test_rules_paths_check.py, tests/unit/test_workflow_paths_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-12
pr: 1457
payoff: every check reads the files the repository holds, by one list
verify: grep -q 'def test_an_untracked_module_is_not_read' tests/unit/test_import_boundary_check.py
recurrences: 2026-10-12 PL-8W1J, 2026-10-12 PL-J4YY
---

**Problem.** Six more tools read the Python files on disk where tracked_files asks git - import_boundary, core_vocabulary and literal_home's _sources, contrast_check.app_modules, agent_identity.read_modules, workflow_paths_check.problems - and doc_check measures nested .claude/rules files that rules_paths_check never reads

- Which Python files a check reads: `rglob` over the disk in `import_boundary_check`, `core_vocabulary_check` and `literal_home_check`'s `_sources`, `contrast_check.app_modules`, `agent_identity_check.read_modules` and `workflow_paths_check.problems`, beside `workflow_paths_check.tracked_files`, which asks git. An untracked `src/anesthesia_sim/core/scratch.py` is read by every walk and left out by `tracked_files`. `PL-HNXS`, `PL-QJ5F` and `PL-2P5L` hold three other walks of the same fact and name none of these.
- Which files are rule files: `doc_check.measure_resident` (an `rglob`) and `DOC_GLOBS` (`.claude/rules/**/*.md`) beside `rules_paths_check.problems`' top-level glob. A nested `.claude/rules/sub/x.md` is measured as a rule and its `paths:` never read.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** The walks read one tracked-file list (the one `PL-HNXS`, `PL-QJ5F` and `PL-2P5L` settle on), rules_paths_check reads nested rule files, and a test pins an untracked module and a nested rule. Work it with those three.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
