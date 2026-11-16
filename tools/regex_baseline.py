"""The regular expressions the tree held without a reason when `tools/regex_check.py` landed.

Each entry is a file, then the enclosing function or class and the function
called, then how many such calls that place holds. `tools/regex_check.py`
fails on a count above its entry and on an entry the tree no longer fills, so
this table only shrinks. Lower or delete an entry in the change that removes a
call or gives it a `regex:` reason. Never add one: a new call carries its
reason beside it instead.

Taken on 2026-11-03 (`PL-7JYV`): 346 calls in 73 files, under 126 keys.
`PL-3WFF` reviewed the six under `src/`, kept each one and wrote its reason
beside it, so none is listed here. Reviewing the rest for a parser or string
method that does the job better is `PL-8FT2`.
"""

GRANDFATHERED_REGEX: dict[str, dict[tuple[str, str], int]] = {
    "subprojects/docket/src/docket/arming.py": {("<module>", "compile"): 3},
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
    "tools/doc_check.py": {("<module>", "compile"): 8},
}
