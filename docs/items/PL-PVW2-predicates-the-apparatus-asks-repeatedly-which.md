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
verify: grep -q 'def test_creation_parents_reads_leading_ids_as_docket_does' tests/unit/test_generator_check.py && grep -q 'def test_a_non_ascii_protected_path_is_rejected' subprojects/docket/tests/test_verify.py && grep -q 'def test_repo_slug_reads_a_token_bearing_url' tests/unit/test_open_pull_requests.py && grep -q 'def test_default_branch_ref_follows_docket_on_a_master_only_clone' tests/unit/test_pr_body_check.py && grep -q 'def test_pull_request_number_reads_both_subject_shapes' subprojects/docket/tests/test_vcs.py && grep -q 'def test_an_unspaced_separator_still_ends_a_command' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_path_listing_is_read_one_way' subprojects/docket/tests/test_vcs.py && grep -q 'def test_digest_counts_this_branch_as_here' subprojects/docket/tests/test_cli.py && grep -q 'def test_a_roadmap_only_branch_is_queue_work_but_not_armable' subprojects/docket/tests/test_claims.py
root-cause-of: PL-KR69, PL-YYDT, PL-2TV9, PL-GNCB, PL-0JGZ, PL-BBV7, PL-6P0F, PL-8HSX, PL-GVFC, PL-GJPD, PL-LFNK, PL-0T5X, PL-NK1L, PL-Y2L6, PL-PQ0R, PL-R5RF, PL-63TT, PL-39LD
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

**Split, 2026-09-26.** The `L` is built one question per pull request, and its members already are that decomposition, so no item is added. In order:

1. The tools' own spellings of the pull-request number, the default branch, the origin slug and the GitHub token (`PL-YYDT`, `PL-GNCB`, `PL-2TV9`), onto `vcs.subject_pull_request`, `vcs.default_base`, `vcs.github_slug` and `vcs.github_token`.
2. How a shell command splits, for the three Bash guard hooks (`PL-BBV7`, `PL-GVFC`). Landed in #1064 while the first was being built - as matching lexer settings, not as a splitter the hooks import, and it is being handed members again: `PL-R5RF`, `PL-63TT` and `PL-39LD` arrived on 2026-09-26, each a place where the hooks' copies of the split still diverge from bash or from each other. Reopened for that splitter, which takes all three.
3. How a changed-path listing is read (`PL-NK1L`, `PL-PQ0R`, `PL-Y2L6`, `PL-0T5X`). It is the one question still being handed members, four since `PL-8HSX`, and it goes third rather than first because it is the widest, 19 call sites across five files, and its four members are untriaged; the first two are what `verify:` below names, which passes once both have landed.
4. `PL-LFNK`, then `PL-0JGZ`, whose decision the owner answered on 2026-09-26.

The head closes with the last of them, when `verify:` passes and `generator:` can say spent. Once the first two landed, `verify:` passed while the head was still open, so on 2026-09-26 it gained the test each remaining step creates: `test_a_path_listing_is_read_one_way` in `subprojects/docket/tests/test_vcs.py` for step 3, `PL-LFNK`'s own `test_digest_counts_this_branch_as_here`, and `test_a_roadmap_only_branch_is_queue_work_but_not_armable` in `subprojects/docket/tests/test_claims.py` for `PL-0JGZ`. A step that names its test otherwise updates this line.

**Step 3 built 2026-09-26, in #1078.** `vcs.changed_path_args` now asks every read for `-z`, the one form in which git quotes no path and ends each with NUL, and drops the `core.quotePath=false` that `-z` makes moot. `vcs.listed_paths` is the one parse of a `--name-only` or `ls-files` listing and `vcs.untracked_path_args` builds the untracked read; the `--raw`, `--numstat` and `log` readers (`_landing_split`, `_superseded`, `claims.work_under_record` and the holdings log) read their own NUL records. `PL-NK1L`, `PL-PQ0R`, `PL-Y2L6` and `PL-0T5X` closed with it. The thread that built step 3 stopped there for length, not for the work.

**Step 4's first half built 2026-09-26, in #1081.** `vcs.only_on_a_branch` is the one answer to whether an item is only on a branch, asked by the digest, `flight` and `stranded` alike; `PL-LFNK` closed with it. **Next, in a fresh thread once #1081 has merged:** `PL-0JGZ`, whose answer is recorded in it. Move it to `ready` and build the two named predicates its done-when names. It closes this head too, when `verify:` passes and `generator:` can say spent. The thread that built `PL-LFNK` stopped there for length, not for the work.

**Step 4 finished 2026-09-26, in #1084.** `PL-0JGZ` closed with `arming.arms_on_green`, arming's named answer to what may merge unread, beside `claims.in_queue`'s answer to what owes a claim; each docstring names the other. It lives in `arming.py`, the module the gate holds, rather than in `claims.py` as `PL-0JGZ`'s done-when had it (project owner, 2026-09-26, ratified, over two predicates in `claims`, as `PL-F6MM` keeps `RECORDS`). `verify:` passes with it. The head stays open all the same: #1082 reopened step 2 for the one splitter the three Bash guard hooks import, which takes `PL-R5RF`, `PL-63TT` and `PL-39LD`, `PL-63TT`'s case first because it is a silent miss rather than a false refusal (project owner, 2026-09-26). **Next, in a fresh thread:** triage those three, then build that splitter. `generator:` stays live until it lands.

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** Each listed question has one implementation that every caller imports, with `tools/` importing `subprojects/docket/src` as `branch_id_check` already does; a test per question holds the disagreeing input.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
