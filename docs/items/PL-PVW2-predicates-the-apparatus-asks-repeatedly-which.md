---
id: PL-PVW2
title: Predicates the apparatus asks repeatedly - which ids a subject leads with, which files a branch changed, the pull-request number, the origin slug, the default ref, captures-only, how a shell command splits - are spelled again wherever they are needed, and the spellings disagree
priority: P2
effort: L
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests, tools/generator_check.py, tools/pr_body_check.py, tools/doc_check.py, tools/open_pull_requests.py, tools/main_ci_status.py, tools/required_checks_check.py, tools/pr_title_check.py, tools/left_behind_check.py, .claude/hooks/, tests/unit/test_generator_check.py, tests/unit/test_open_pull_requests.py, tests/unit/test_required_checks_check.py, tests/unit/test_pr_body_check.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_gate_status_guard.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head, triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
payoff: the next tool or hook imports the one answer to each question the apparatus keeps asking instead of copying a spelling that disagrees, the way PL-KR69's and PL-8HSX's did on the protected-path audit
verify: grep -q 'def test_creation_parents_reads_leading_ids_as_docket_does' tests/unit/test_generator_check.py && grep -q 'def test_a_non_ascii_protected_path_is_rejected' subprojects/docket/tests/test_verify.py && grep -q 'def test_repo_slug_reads_a_token_bearing_url' tests/unit/test_open_pull_requests.py && grep -q 'def test_default_branch_ref_follows_docket_on_a_master_only_clone' tests/unit/test_pr_body_check.py && grep -q 'def test_pull_request_number_reads_both_subject_shapes' subprojects/docket/tests/test_vcs.py && grep -q 'def test_an_unspaced_separator_still_ends_a_command' tests/unit/test_floor_interpreter_guard.py
root-cause-of: PL-KR69, PL-YYDT, PL-2TV9, PL-GNCB, PL-0JGZ, PL-BBV7, PL-6P0F, PL-8HSX, PL-GVFC, PL-GJPD, PL-LFNK, PL-0T5X, PL-NK1L, PL-Y2L6, PL-PQ0R
generator: live - PL-8HSX arrived after the audit, found while fixing PL-KR69, whose fix single-sourced the rename flag and left core.quotePath spelled at one caller; tools/ and .claude/hooks/ still spell each listed predicate locally, so each new caller copies whichever spelling it finds
misread: Which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it
---

**Problem.** Predicates the apparatus asks repeatedly - which ids a subject leads with, which files a branch changed, the pull-request number, the origin slug, the default ref, captures-only, how a shell command splits - are spelled again wherever they are needed, and the spellings disagree

The audit enumerated the questions the apparatus asks and found every implementation. Nine questions have two or more that disagree on a constructed input, one of them on the protected-path audit (PL-KR69). Four questions are already single-sourced (who holds an item, gate parity, canonical form, item id grammar) and have produced no disagreement since - which is the evidence that consolidation holds.

**Re-confirmed 2026-09-25 against 46954a81**, after #1015, #1016 and #1017: every open member's disagreement reproduces on today's tree, and each member's brief carries its own line. `PL-KR69` (done, #1015) stays a member. Its fix put `--no-renames` into `vcs.changed_path_args` and left `-c core.quotePath=false` spelled at `claims.work_under_record` alone, which is `PL-8HSX`: the next instance, found while fixing the first.

**Members added at triage, 2026-09-25.**

- `PL-8HSX` - which files a branch changed, quoting half.
- `PL-GVFC` (filed 2026-09-23) - how a shell command splits. The floor guard's plain `shlex.split` glues a `;` to the word before it, a case `gate-status-guard.sh`'s `punctuation_chars` already handles. Its other clause, the `GUARDED` lookbehind, is a cause of its own.
- `PL-GJPD` (filed 2026-09-19) - captures-only. `_carried_work` reads through `vcs._annotates_only`, which counts `docs/items/` alone, while `claims.in_queue` knows a triage pass also writes `ROADMAP.md` and the notes. It is also `PL-HMZZ`'s member, because the carrying-pull-request inference is its other cause.

`PL-YYDT` stays here and does not go to `PL-HMZZ`. Its disagreeing parsers are the squash-only ones (`Landing.pull_request`, `doc_check`, `pr_body_check`), and `PL-HMZZ`'s inference (`_merges_naming`, `_number_closing`) already reads both subject shapes through `PR_SUBJECT_RE`.

**Generator check.** This head states the fact. Two members reached the queue before the audit enumerated anything (`PL-GJPD`, `PL-GVFC`), and one arrived after it (`PL-8HSX`), out of the fix for another. No function holds any listed predicate for `tools/` and `.claude/hooks/` to import. The four questions already single-sourced were closed by narrower heads: `PL-7TVT`, `PL-8FJK` and `PL-MB2W` for who holds an item, `PL-0HPV` for gate parity, `PL-L4YG` for canonical form and `PL-ZJ6X` for item ids. Each of those fixes is an instance of this one.

**Working order.** `PL-6P0F` goes first (`impairs-generators`, S), then `PL-8HSX` (P1, the protected-path audit). `PL-0JGZ` waits on its own decision, which is why `verify:` below leaves it out. `PL-GJPD` is likelier to close under `PL-HMZZ`'s recorded `pr:` than here.

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** Each listed question has one implementation that every caller imports, with `tools/` importing `subprojects/docket/src` as `branch_id_check` already does; a test per question holds the disagreeing input.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
