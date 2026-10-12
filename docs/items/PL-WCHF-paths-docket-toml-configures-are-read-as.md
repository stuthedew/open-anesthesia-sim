---
id: PL-WCHF
title: Paths docket.toml configures are read as literals by tools - the item store in six tools, the version file in tag_release and doc_check, the docket table in workflow_paths_check, pr-bodies in four places, the item-read log in two - so setting items_dir, version_file or a top-level key splits docket from them
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/branch_sweep.py, tools/pr_title_check.py, tools/generator_check.py, tools/dead_ends.py, tools/item_reads.py, tools/doc_check.py, tools/tag_release.py, tools/workflow_paths_check.py, tools/pr_body_check.py, .claude/hooks/item_read_log.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, tests/unit/test_workflow_paths_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: a setting in docket.toml reaches every tool that reads the path it names
verify: grep -q 'def test_settings_are_read_through_docket_config' tests/unit/test_workflow_paths_check.py
---

**Problem.** Paths docket.toml configures are read as literals by tools - the item store in six tools, the version file in tag_release and doc_check, the docket table in workflow_paths_check, pr-bodies in four places, the item-read log in two - so setting items_dir, version_file or a top-level key splits docket from them

- The item store: `config.items_dir` beside `branch_sweep.ITEMS`, `pr_title_check.ITEMS_DIR`, `generator_check.ITEM_DIR`, `dead_ends.ITEMS`, `item_reads.ITEMS` and `doc_check.briefs_of`'s `root/"docs"/"items"`. With `items_dir = "queue"` docket reads `queue/`, `dead_ends.known_ids` reports every cited id as no item and `briefs_of` every cited item as held by no file. `PL-F66M` (ready) covers normalizing the setting, not these literals.
- The version file: `config.version_file` beside `tag_release.VERSION_FILE` and three `pyproject.toml` literals in doc_check; docket bumps a configured file and tag_release tags from `pyproject.toml`.
- The settings table: `config.load` reads `data.get("docket", data)` with typed fallbacks; `workflow_paths_check.declared_workflow_paths`, `declared_product_paths` and `declared_gate_paths` read `data.get("docket", {})` bare. A top-level `workflow_paths` is read by docket and reported absent by the check; `workflow_paths = "tools"` gives docket `()` and the check five letters; an absent `gate_paths` takes docket's defaults and the check's `()`.
- The pull-request body records: `claims.RECORDS`, `arming.RECORDS`, `pr_body_check.RECORD_PATH` and `doc_check.DATED_RECORDS`; they agree, and `PL-F6MM` pins only the first pair.
- The item-read log: `item_read_log.LOG_NAME` beside `item_reads.LOG`; they agree. The roadmap path: `doc_check.ROADMAP` beside `config.roadmap_file`.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** The tools read each path through `docket.config`, and a test sets a non-default `items_dir` and a top-level key and asserts the tools follow.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
