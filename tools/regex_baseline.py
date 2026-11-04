"""The regular expressions the tree held without a reason when `tools/regex_check.py` landed.

Each entry is a file, then the enclosing function or class and the function
called, then how many such calls that place holds. `tools/regex_check.py`
fails on a count above its entry and on an entry the tree no longer fills, so
this table only shrinks. Lower or delete an entry in the change that removes a
call or gives it a `regex:` reason. Never add one: a new call carries its
reason beside it instead.

Taken on 2026-11-03 (`PL-7JYV`): 346 calls in 73 files, under 126 keys.
Reviewing them for a parser or string method that does the job better is
`PL-3WFF` for the six under `src/` and `PL-8FT2` for the rest.
"""

GRANDFATHERED_REGEX: dict[str, dict[tuple[str, str], int]] = {
    ".claude/hooks/shell_split.py": {("<module>", "compile"): 2},
    ".claude/hooks/thread_hooks.py": {("_matches", "fullmatch"): 1},
    "src/anesthesia_sim/app/agent_cost.py": {("<module>", "compile"): 1},
    "src/anesthesia_sim/app/currency_code.py": {("<module>", "compile"): 1},
    "src/anesthesia_sim/app/preferences.py": {("<module>", "compile"): 1},
    "src/anesthesia_sim/app/view_registry.py": {("<module>", "compile"): 1},
    "src/anesthesia_sim/layout/run_identity.py": {("<module>", "compile"): 1},
    "src/anesthesia_sim/layout/tree.py": {("<module>", "compile"): 1},
    "subprojects/docket/src/docket/arming.py": {("<module>", "compile"): 4},
    "subprojects/docket/src/docket/checks.py": {
        ("<module>", "compile"): 12,
        ("_answered_beneath", "finditer"): 1,
        ("_answered_beneath", "search"): 1,
        ("_blanked", "sub"): 1,
        ("_cue_pattern", "compile"): 1,
        ("_heading_words", "compile"): 1,
        ("_marks_recommendation", "search"): 1,
    },
    "subprojects/docket/src/docket/claiming.py": {("<module>", "compile"): 1},
    "subprojects/docket/src/docket/claims.py": {("<module>", "compile"): 2},
    "subprojects/docket/src/docket/frontmatter.py": {("<module>", "compile"): 2},
    "subprojects/docket/src/docket/grep.py": {
        ("<module>", "compile"): 1,
        ("_phrase", "compile"): 1,
    },
    "subprojects/docket/src/docket/instructions.py": {("<module>", "compile"): 2},
    "subprojects/docket/src/docket/markdown.py": {("<module>", "compile"): 22},
    "subprojects/docket/src/docket/model.py": {("<module>", "compile"): 7},
    "subprojects/docket/src/docket/notes.py": {("<module>", "compile"): 1},
    "subprojects/docket/src/docket/release.py": {("<module>", "compile"): 10},
    "subprojects/docket/src/docket/roadmap.py": {("<module>", "compile"): 11},
    "subprojects/docket/src/docket/sessions.py": {("<module>", "compile"): 3},
    "subprojects/docket/src/docket/store.py": {("<module>", "compile"): 4},
    "subprojects/docket/src/docket/vcs.py": {("<module>", "compile"): 6},
    "subprojects/docket/src/docket/verify.py": {
        ("<module>", "compile"): 5,
        ("_short", "fullmatch"): 1,
    },
    "subprojects/docket/tests/test_cli.py": {
        ("_grooming_counts.count", "search"): 1,
        ("_lanes_gate_listed", "match"): 2,
        ("test_a_cut_interrupted_inside_the_stamp_loop_is_resumed_whole", "findall"): 1,
        ("test_a_second_filing_extends_the_line_the_first_one_wrote", "search"): 1,
        (
            "test_flight_prints_each_hold_s_kind_and_state_the_lapsed_claims_and_the_unclaimed_work",
            "fullmatch",
        ): 2,
        ("test_new_records_the_filing_on_the_item_it_matched", "search"): 1,
        ("test_next_and_the_digest_say_what_holds_each_item_they_leave_out", "search"): 1,
        ("test_next_reports_the_same_open_count_as_status", "search"): 2,
    },
    "subprojects/docket/tests/test_frontmatter_reference.py": {("front_matters", "sub"): 1},
    "subprojects/docket/tests/test_markdown_reference.py": {("<module>", "compile"): 1},
    "subprojects/docket/tests/test_multisession.py": {
        ("<module>", "compile"): 1,
        ("RandomRun.check", "match"): 1,
        ("World.flight_live", "match"): 1,
        ("World.holder", "search"): 2,
        ("World.offered", "finditer"): 1,
    },
    "subprojects/docket/tests/test_portability.py": {
        ("_floor", "search"): 1,
        ("_ruff_target", "fullmatch"): 1,
    },
    "subprojects/docket/tests/test_release.py": {
        ("test_the_reserved_refusal_names_the_way_out", "findall"): 1
    },
    "subprojects/docket/tests/test_shell.py": {
        ("<module>", "compile"): 4,
        ("_here_document", "search"): 1,
        ("_here_document", "sub"): 1,
    },
    "subprojects/docket/tools/migrate_from_punch_list.py": {
        ("<module>", "compile"): 7,
        ("blockers_from", "findall"): 1,
        ("blockers_from", "search"): 1,
        ("convert_inbox", "match"): 1,
        ("convert_open", "search"): 1,
        ("touches_from", "search"): 1,
    },
    "tests/integration/test_simulation_view.py": {
        ("<module>", "compile"): 2,
        ("test_agent_header_badge_is_bordered_against_the_panel", "search"): 1,
        ("test_the_interface_never_predicts_a_time_to_wake_up", "compile"): 1,
        ("test_the_interface_never_predicts_a_time_to_wake_up", "finditer"): 1,
    },
    "tests/reference/test_mac_awake_washout_figures.py": {("_one", "findall"): 1},
    "tests/unit/test_ci_concurrency.py": {("<module>", "compile"): 4, ("_concurrency", "match"): 1},
    "tests/unit/test_config_home_check.py": {("_letters", "findall"): 1},
    "tests/unit/test_direct_merge_guard.py": {
        ("_matches", "fullmatch"): 1,
        ("_matches", "search"): 1,
        ("_matches", "split"): 1,
    },
    "tests/unit/test_gate_status_guard.py": {
        ("test_the_tracked_makefile_runs_no_recipe_under_a_dry_run", "fullmatch"): 1,
        ("test_the_tracked_makefile_runs_no_recipe_under_a_dry_run", "match"): 1,
    },
    "tests/unit/test_generator_check.py": {("<module>", "compile"): 1},
    "tests/unit/test_inline_reference.py": {("<module>", "compile"): 1},
    "tests/unit/test_item_store_guard.py": {("<module>", "compile"): 1},
    "tests/unit/test_makefile_reference.py": {("<module>", "compile"): 2},
    "tests/unit/test_quality_step_order.py": {
        ("<module>", "compile"): 12,
        (
            "test_an_apparatus_pull_request_skips_the_costly_tests_and_the_coverage_threshold",
            "search",
        ): 1,
        ("test_checks_needs_every_other_job", "search"): 1,
    },
    "tests/unit/test_run_series.py": {
        ("test_a_window_refusing_the_wash_in_ratio_names_a_method_that_forms_it", "findall"): 1
    },
    "tests/unit/test_source_tier_counts.py": {("<module>", "compile"): 1},
    "tests/unit/test_tools_portability.py": {
        ("_bare_python_floor", "search"): 1,
        ("_concrete_pins", "findall"): 1,
        ("_ruff_target", "fullmatch"): 1,
    },
    "tests/unit/test_update_armed.py": {("FakeGitHub.get", "search"): 3},
    "tools/branch_id_check.py": {("<module>", "compile"): 1},
    "tools/config_home_check.py": {
        ("Place.values", "finditer"): 1,
        ("_paths", "findall"): 1,
        ("_quoted", "findall"): 1,
        ("_tools", "findall"): 1,
    },
    "tools/contrast_check.py": {("<module>", "compile"): 5},
    "tools/core_vocabulary_check.py": {("<module>", "compile"): 1},
    "tools/dead_ends.py": {("<module>", "compile"): 2},
    "tools/diff_mutation.py": {("<module>", "compile"): 3},
    "tools/doc_check.py": {
        ("<module>", "compile"): 75,
        ("_blanked_span", "sub"): 1,
        ("_entity_kind", "compile"): 1,
        ("_is_path_citation", "fullmatch"): 1,
        ("_runs_on_pull_requests", "split"): 1,
        ("_without_destinations", "sub"): 1,
        ("mentions", "finditer"): 1,
    },
    "tools/doc_quote_check.py": {("<module>", "compile"): 3},
    "tools/duplicate_code_check.py": {("<module>", "compile"): 1},
    "tools/fact_home_check.py": {("<module>", "compile"): 1},
    "tools/fixture_id_check.py": {("<module>", "compile"): 5},
    "tools/headless_worker.py": {("tool_version", "match"): 1},
    "tools/hook_blocks.py": {("<module>", "compile"): 1},
    "tools/model_doc_review.py": {("<module>", "compile"): 1, ("sections", "sub"): 1},
    "tools/model_home_check.py": {("<module>", "compile"): 1},
    "tools/model_rewrite.py": {("<module>", "compile"): 9},
    "tools/possessive_section_check.py": {("<module>", "compile"): 1},
    "tools/pr_body_check.py": {("<module>", "compile"): 3},
    "tools/rejected_prose.py": {
        ("<module>", "compile"): 1,
        ("rewrites", "sub"): 1,
        ("verdicts", "sub"): 1,
    },
    "tools/required_checks_check.py": {
        ("<module>", "compile"): 1,
        ("_branch_pattern", "compile"): 1,
        ("_branch_pattern", "fullmatch"): 1,
    },
    "tools/rules_paths_check.py": {("_prose_list", "findall"): 1},
    "tools/skill_start_eval.py": {("<module>", "compile"): 1},
    "tools/type_ignore_check.py": {("<module>", "compile"): 1},
}
