---
id: PL-PVW2
title: Predicates the apparatus asks repeatedly - which ids a subject leads with, which files a branch changed, the pull-request number, the origin slug, the default ref, captures-only, how a shell command splits - are spelled again wherever they are needed, and the spellings disagree
priority: P2
effort: L
status: done
classes: defect
feature: one-answer
milestone: v0.5.12
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests, tools/generator_check.py, tools/pr_body_check.py, tools/doc_check.py, tools/open_pull_requests.py, tools/main_ci_status.py, tools/required_checks_check.py, tools/pr_title_check.py, tools/left_behind_check.py, .claude/hooks/, tests/unit/test_generator_check.py, tests/unit/test_open_pull_requests.py, tests/unit/test_required_checks_check.py, tests/unit/test_pr_body_check.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_gate_status_guard.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head, triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
closed: 2026-09-26
pr: 1099
payoff: the next tool or hook imports the one answer to each question the apparatus keeps asking instead of copying a spelling that disagrees, the way PL-KR69's and PL-8HSX's did on the protected-path audit
verify: grep -q 'def test_creation_parents_reads_leading_ids_as_docket_does' tests/unit/test_generator_check.py && grep -q 'def test_a_non_ascii_protected_path_is_rejected' subprojects/docket/tests/test_verify.py && grep -q 'def test_repo_slug_reads_a_token_bearing_url' tests/unit/test_open_pull_requests.py && grep -q 'def test_default_branch_ref_follows_docket_on_a_master_only_clone' tests/unit/test_pr_body_check.py && grep -q 'def test_pull_request_number_reads_both_subject_shapes' subprojects/docket/tests/test_vcs.py && grep -q 'def test_an_unspaced_separator_still_ends_a_command' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_path_listing_is_read_one_way' subprojects/docket/tests/test_vcs.py && grep -q 'def test_digest_counts_this_branch_as_here' subprojects/docket/tests/test_cli.py && grep -q 'def test_a_roadmap_only_branch_is_queue_work_but_not_armable' subprojects/docket/tests/test_claims.py && grep -q 'def test_a_glued_punctuation_run_splits_into_bash_operators' tests/unit/test_gate_status_guard.py && grep -q 'def test_a_backslash_newline_continues_the_command' tests/unit/test_gate_status_guard.py && grep -q 'def test_only_a_heredoc_body_is_removed' tests/unit/test_gate_status_guard.py && grep -q 'def test_a_quoted_separator_starts_no_command' tests/unit/test_no_prune_guard.py && grep -q 'def test_a_verify_clause_is_read_one_way' subprojects/docket/tests/test_checks.py && grep -q 'def test_an_apostrophe_in_double_quotes_hides_no_command' subprojects/docket/tests/test_verify.py && grep -q 'def test_workflow_paths_reads_a_quoted_path_as_one_word' tests/unit/test_doc_check.py
root-cause-of: PL-KR69, PL-YYDT, PL-2TV9, PL-GNCB, PL-0JGZ, PL-BBV7, PL-6P0F, PL-8HSX, PL-GVFC, PL-GJPD, PL-LFNK, PL-0T5X, PL-NK1L, PL-Y2L6, PL-PQ0R, PL-R5RF, PL-63TT, PL-39LD, PL-WGFY, PL-B5VZ, PL-P7J7, PL-CWBJ
generator: spent - every listed question has one implementation its callers import, the last spelling of how a shell command splits (tools/doc_check.py, PL-CWBJ) now reads through docket's shell.py, and a sweep of tools/, .claude/hooks/ and docket found no other reader to hand it a member
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

**Step 4 finished 2026-09-26, in #1084.** `PL-0JGZ` closed with `arming.arms_on_green`, arming's named answer to what may merge unread, beside `claims.in_queue`'s answer to what owes a claim; each docstring names the other. It lives in `arming.py`, the module the gate holds, rather than in `claims.py` as `PL-0JGZ`'s done-when had it (project owner, 2026-09-26, ratified, over two predicates in `claims`, as `PL-F6MM` keeps `RECORDS`). `verify:` passes with it. The head stays open all the same: #1082 reopened step 2 for the one splitter the three Bash guard hooks import, which takes `PL-R5RF`, `PL-63TT` and `PL-39LD`, `PL-63TT`'s case first because it is a silent miss rather than a false refusal (project owner, 2026-09-26). **Next, in a fresh thread:** triage those three, then build that splitter. `verify:` passed with `PL-0JGZ`'s test while the head stood reopened, so it gains one test per member, each a prediction in `tests/unit/test_gate_status_guard.py`: `test_a_glued_punctuation_run_splits_into_bash_operators` for `PL-63TT`, `test_a_backslash_newline_continues_the_command` for `PL-R5RF` and `test_only_a_heredoc_body_is_removed` for `PL-39LD`. The thread that builds the splitter updates the line where it names or places them otherwise. `generator:` stays live until it lands.

**Step 2's splitter, triaged and designed 2026-09-26, and built the same day.** `PL-63TT` (P2), `PL-R5RF` (P3) and `PL-39LD` (P2) were triaged `ready`, each with its `verify:`, by a thread that stopped for length before building. The design below is what was built; what the build added to it follows the list.

- **Where.** One standard-library module, `.claude/hooks/shell_split.py`, which all three hooks import. Each passes its own directory to its inline `python3 -c` (`HOOKS="$(dirname "${BASH_SOURCE[0]}")"`) and puts it first on `sys.path`; a failed import exits non-zero, which each hook's `|| exit 0` already turns into failing open. `.claude/hooks/` is on pytest's `pythonpath` and mypy's `files` in `pyproject.toml`, and `tests/unit/test_tools_portability.py` parses it at the floor and admits a sibling import.
- **A small lexer, not `shlex`**, because each fix needs to know what is quoted: `shlex`'s punctuation runs are `PL-63TT`, the newline-to-` ; ` substitution that turns a backslash-newline into an escaped space and a `;` is `PL-R5RF`, and `split("<<", 1)` is not quote-aware (`PL-39LD`). Every rule is bash's (Bash Reference Manual §3.1.2 and §3.6.6; POSIX.1-2017 XCU §2.3 and §2.7.4):
  - operators by longest match over bash's own table, three characters first (`;;&`, `<<<`, `&>>`, and `<<-` as `<<` plus a `-`), then `&&`, `||`, `;;`, `;&`, `|&`, `<<`, `>>`, `<&`, `>&`, `<>`, `>|`, `&>`, then `&`, `|`, `;`, `(`, `)`, `<`, `>`. So `2>&1` is `2`, `>&`, `1`, and `>|` or `&>` never yields a separator;
  - `'...'` literal; `"..."` where a backslash escapes only `$`, a backtick, `"`, a backslash and a newline; `$'...'`, where a backslash-quote does not close it; a backslash outside single quotes followed by a newline is removed with it;
  - `#` opens a comment only where no word is in progress, and the comment ends before the newline. Under the substitution, `shlex`'s comment ran to the end of the input, hiding every later line;
  - an unquoted newline is a `;`, except straight after `|`, `|&`, `&&`, `||`, `(`, `;`, `&` or another newline, where bash reads a linebreak (so `make check &&` then a newline then `tail -5 log` keeps the status, which the substitution refuses today). A trailing `;` is dropped;
  - at each unquoted newline the pending heredocs' bodies are consumed in order. The delimiter is the word after `<<` or `<<-` with quotes removed; the body runs to a line equal to it, leading tabs stripped for `<<-`; an unterminated body runs to the end of the input, which is bash's reading and still fails open. `<<` with no word after it is unreadable;
  - `$` and the backtick stay word characters and `$(` yields `$` and `(`, exactly as `shlex` did, so the gate walker's subshell counting sees what it sees today.
- **API.** `words(command)`, or `None` where the command cannot be read (an unbalanced quote, a `<<` with no word); `segments(command)`, the words cut at each separator, with `|&` read as the pipe it is (a silent miss today, `make check |& tail`) and `;;`, `;&`, `;;&` as `;`; and `command_text(command)` for `no-prune-guard.sh`'s regexes - the text with continuations, comments and heredoc bodies removed. That one is never `None`: where the lexer stops, it keeps the unread remainder raw, so the prune guard never reads less than it does today.
- **The hooks.** The gate guard's per-character `PUNCTUATION` loop becomes a match on the whole `(` or `)` token, and its comments on glued runs and on `commenters` are rewritten; its `SEPARATORS` loop and the floor guard's are replaced by `segments`; the floor guard's comment deferring the continuation step to this head goes.
- **Tests,** each name already predicted in a `verify:`. In `tests/unit/test_gate_status_guard.py`: `test_a_glued_punctuation_run_splits_into_bash_operators` (`PL-63TT`'s commands and `(make check)|tail` refused; `make check |& tail` refused; `make check >| log; echo "exit=$?"` and `make check &> log; echo "exit=$?"` allowed), `test_a_backslash_newline_continues_the_command` (`PL-R5RF`'s command allowed; a continued gate piped without `pipefail` still refused), and `test_only_a_heredoc_body_is_removed` (`PL-39LD`'s command refused; `<<-` with tabs, a quoted delimiter, two heredocs on one line, `<<<`, a `<<` inside quotes, and an unterminated body allowed). `tests/unit/test_floor_interpreter_guard.py` takes the first and third names for its halves, and `tests/unit/test_no_prune_guard.py` the third, with a prune after the terminator refused and prose in the body still allowed. The existing tests hold as they are; the `ESCAPED` comment about a glued `;)` is rewritten.
- **Left out, filed.** `no-prune-guard.sh` finds a command position with its own regex rather than a split, so a `;` in a quoted argument reads as a separator (`PL-WGFY`, which refused the triaging session's own Bash call). Feeding it `command_text` is all `PL-39LD` asks.

**Step 2 built 2026-09-26, in #1087.** `.claude/hooks/shell_split.py` is the splitter, and the three hooks import it: the gate and floor guards read `segments`, the prune guard `command_text`. `PL-63TT`, `PL-39LD` and `PL-R5RF` closed with it, each reproduction pinned under the test name its `verify:` predicted; 22 of the new cases fail on the hooks as they stood, and every pinned shape was run through bash 5.2 first. What the build added to the design:

- **Operators are marked, as `Operator`, a `str` subclass.** As plain strings a quoted `;` or `(` cannot be told from the operator - `shlex` could not tell them apart either - so `make check && echo ";"` read as handing the status on. `segments` cuts only at an operator, and the gate guard counts only an operator `(` or `)`.
- **A `$( )` inside double quotes is read as the command it is.** The design did not cover it, and the commonest command a session runs needs it: `git commit -m "$(cat <<'EOF' ... EOF )"` otherwise ends its quoted word at the message's first `"`, and a message quoting `"make check | tail"` is read as commands and refused.
- **The heredoc test pins both directions.** The design listed `<<-`, a quoted delimiter and two heredocs on a line as allowed, and the allowed half passes on the old hooks too, which dropped everything after the first `<<`. So each shape is pinned twice - its body allowed, a check after its terminator refused - and `<<<` and a quoted `<<` are pinned refused, the direction that changed. A comment ending at its line and a newline after an operator reading as a linebreak are pinned as well.

[superseded 2026-09-26: `PL-WGFY` closed in #1088, and `PL-B5VZ` keeps the head live, as the paragraphs below say] **The head stays open, `generator:` live.** `verify:` passes and every member is terminal, but the question this step answers still has a second answer: `no-prune-guard.sh` finds a command position with its own regex (`PL-WGFY`, untriaged), so a quoted `;` still reads as a separator there. The sweep for other copies found docket's own readers of a `verify:` command, filed as `PL-B5VZ` for triage to place. **Next, in a fresh thread:** triage `PL-WGFY` as this head's member and move that guard's patterns onto `segments`; then `generator:` can say spent and the head closes. `verify:` passed once this step landed, so it gains that step's test, a prediction in `tests/unit/test_no_prune_guard.py`: `test_a_quoted_separator_starts_no_command`, with `PL-WGFY`'s quoted `;` allowed. The thread that builds it updates the line where it names or places the test otherwise.

**Step 2's last hook built 2026-09-26, in #1088.** `PL-WGFY` closed with it:
the prune guard reads `shell_split.commands`, every command a string runs,
those in a subshell or a `$( )` included, and `shell_split.command_words` is
now the one answer to where a command's words start, imported by all three
guards in place of the two copies the gate and floor guards held.

[superseded 2026-09-26: `PL-B5VZ` closed in #1095, and `PL-P7J7` keeps the head live, as the paragraphs below say] **The head stays open, `generator:` live, on `PL-B5VZ`.** The #1087 sweep
filed it for triage to place: docket's `checks.py` reads a `verify:` command
three ways beside its own quote-aware `_shell_words`, so `_redundant_pytest_clause`
and `_k_selector_clause` can read one clause two ways. That is this head's
`misread:` inside docket, and a second reader misreading a fact a head states
belongs to that head, so the head cannot say spent while it is open, and
`PL-B5VZ` is this head's to triage as a member. Its file is `checks.py`, which
the thread on `PL-GPJ7`'s step 3 (`PL-NQ3X`, `PL-6G8T`, `PL-FKH6`) holds.
**Next, in a fresh thread once that one has merged:** triage `PL-B5VZ` as this
head's member and read both clauses through `_shell_words`; then `generator:`
can say spent and the head closes. `verify:` passed once `PL-WGFY` landed, so it
gains that step's test, a prediction in `subprojects/docket/tests/test_checks.py`:
`test_a_verify_clause_is_read_one_way`. The thread that builds it updates the
line where it names or places the test otherwise.

**Docket's half of step 2 built 2026-09-26, in #1095.** `PL-B5VZ` closed with
it: `_shell_words` reads every operator rather than stopping at the first one
the admitted shapes refuse, records that refusal instead, and cuts the command
into its `&&` clauses, so `_redundant_pytest_clause` and `_k_selector_clause`
read their clauses from it and `checks.py` keeps no `shlex`. Over the store's
1,355 `verify:` commands the two rules answer exactly as before; two refusals
now name a whole operator (`||`, `>&`) where they named its first character.
Docket keeps a reading of its own rather than importing
`.claude/hooks/shell_split.py`: `bin/docket` puts its own package alone on the
path, and the hooks' words drop the quoting the admitted shapes read.

**The head stays open, `generator:` live, on `PL-P7J7`.** Asking where else
docket reads a `verify:` command found `verify.py`, which reads one with regexes
of its own (`_outside_quotes`, `_blanked`, `PIPELINE_END_RE`,
`TRAILING_COMMENT_RE`) and `shlex.split`, and misses a real `bin/docket verify`
behind an apostrophe inside double quotes. That is this head's fact again, in
the module `checks.py` imports, so the head cannot say spent while it stands.
[superseded 2026-09-26: `PL-P7J7` triaged, as the paragraph below says] **Next, in a fresh thread once #1095 has merged:** triage `PL-P7J7` as this
head's member, move `_shell_words` into a module both files import, and read
`verify.py`'s commands through it; then `generator:` can say spent. `verify:`
passed once `PL-B5VZ` landed, so it gains that step's test, a prediction in
`subprojects/docket/tests/test_verify.py`:
`test_an_apostrophe_in_double_quotes_hides_no_command`. The thread that builds
it updates the line where it names or places the test otherwise.

**`PL-P7J7` triaged 2026-09-26** as this head's member, with the build's design
in its brief; the thread that triaged it stopped for length before building.
[superseded 2026-09-26: `PL-P7J7` built in #1098, as the paragraph below says] **Next, in a fresh thread:** build `PL-P7J7` as its design says, with the test
named above; then `generator:` can say spent unless `PL-CWBJ` - `tools/doc_check.py`
splitting a CI step's `run:` with a pattern of its own, filed at that triage -
is triaged as this head's member, which keeps it live on that one.

**`PL-P7J7` built 2026-09-26, in #1098.** `subprojects/docket/src/docket/shell.py`
is docket's one reading of a `verify:` command: `checks.py`'s lexer moved there
and reads a `$( )` or backquote body as the command bash runs, and `verify.py`'s
five readers take it, with no quote regex or `shlex` left in either file.
`test_an_apostrophe_in_double_quotes_hides_no_command` is where this item's
`verify:` predicted it. `PL-P7J7`'s brief has the store's answers before and
after. [superseded 2026-09-26: `PL-CWBJ` built, and the head closed, as the paragraph below says] **The head stays open, `generator:` live, on `PL-CWBJ`:**
`tools/doc_check.py` still splits a CI step's `run:` with a quote-blind pattern
of its own, the one spelling of how a shell command splits left outside
docket's `shell.py` and the hooks' `shell_split.py`. It is untriaged and off
the Fix generators project's list, so whether it is this head's member was put
to the project owner; if it is not, `generator:` says spent and the head closes.
`verify:` passed once `PL-P7J7` landed, so it gains that step's test, a
prediction in `tests/unit/test_doc_check.py`:
`test_workflow_paths_reads_a_quoted_path_as_one_word`. The thread that builds
`PL-CWBJ` updates the line where it names or places the test otherwise; if
`PL-CWBJ` is not this head's member, the clause goes as the head closes.

**`PL-CWBJ` built 2026-09-26, and the head closes, `generator:` spent.**
`PL-CWBJ` was triaged as this head's member on the project owner's word that it
joins the Fix generators list, and recorded there. `tools/doc_check.py`'s two
readers of a shell line, `check_workflow_paths` and `check_gate_parity`, take
`docket.shell.shell_words`, and `COMMAND_SPLIT_RE` is gone;
`test_workflow_paths_reads_a_quoted_path_as_one_word` is where this item's
`verify:` predicted it. Swept again for another spelling of how a shell command
splits, across `tools/`, `.claude/hooks/` and docket's `src/`: none.
`cli.py`'s `shlex.split` turns a configured command into the argv it runs
without a shell, and `release.py`'s `shlex.join` builds one; neither reads what
a shell would run. Two readings remain, each for its own input, as #1095
recorded: docket's `shell.py` for one line, which `tools/` now imports, and the
hooks' `shell_split.py` for a whole Bash command. Every listed question has one
implementation its callers import.

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** Each listed question has one implementation that every caller imports, with `tools/` importing `subprojects/docket/src` as `branch_id_check` already does; a test per question holds the disagreeing input.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
