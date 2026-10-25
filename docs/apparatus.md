# Apparatus map

This document maps the workflow apparatus. The apparatus is the scripts, hooks
and checks that exist so that agent sessions can be productive. It is not the
simulator that those sessions build. This document must meet the bar in
`.claude/rules/apparatus-standard.md`. It does not have to meet the specialist
standard that `CLAUDE.md` sets for the simulator's documents. The simulator's
own map is [`docs/ARCHITECTURE.md`](ARCHITECTURE.md). That map covers the
simulator's layering, its package map, its data flow, and where new code
belongs. The queue's commands and item format are in
[`subprojects/docket/README.md`](../subprojects/docket/README.md).

These three sections were part of `docs/ARCHITECTURE.md` until `PL-KRGY` moved
them here on 2026-10-11. The move was made so that the simulator's map would
stop carrying the apparatus's inventory, and so that the items that work on
that inventory would stop being treated as work for both lanes.

## Developer tooling (`tools/`)

These tools sit outside the packaged application, and the application does not
import them.

```text
tools/
├── agent_identity_check.py  # refuses a control that carries the agent colour and can be rendered disabled, because a toolkit then paints its label in its own disabled-content grey, which is declared in no source file and so is unreachable by `contrast_check.py`; a control may be disabled only where the same expression also hides it - `disabled = E` with `visible = not E`, or `setDisabled(E)` with `setHidden(E)` in the Qt spelling since PL-25KS - and one given an agent colour anywhere outside the single writer `RunView._apply_agent_color_scheme` - where it is constructed, or by a `setStyleSheet` or `setItemData` call after - must be written by it; reads every module under `app/` and names none by path, and refuses a tree in which no `disabled` write can be read at all rather than passing over it
├── ast_identity.py      # says whether each file's code is the same at two revisions once docstrings and comments are removed, a docstring being any string that stands as a statement of its own as `docket.python.docstrings` reads one (`PL-6GP9`), by comparing `ast.dump` of both parses, so a release cut whose simulator tree object moved can still prove that no executable statement did; a file that is not Python is compared as text, and whether a docstring-only change is safe stays the reader's call (`PL-VHHB`)
├── blind_review.py      # counts the blind generalist review passes a simulator branch owes, one or two by `docket.arming.blind_passes`, builds one directory per pass outside the repository holding only the committed tree and the diff, and prints the reviewer brief `PL-TCBJ` ran for each. `.claude/skills/docket/modes/close-out.md` step 9 runs it, and `PL-TDV9` records why. `--count` is `docket.toml`'s `blind_count_command`, which `bin/docket arm` runs to hold a simulator branch until a `Blind-review:` trailer records that many passes (`PL-HDRN`)
├── branch_id_check.py    # refuses a branch ahead of the default base that carries no item id in its name and leads no commit subject with one, because every in-flight guard matches an id and work carrying none is invisible to all of them - an id counting only where the base's or the branch's copy of the store holds it, since the grammar alone passes an English word such as `CTRL` (`PL-SN2T`); scoped to the `claude/*` namespace, since a contributor has no queue to be visible in. It also reads the claim record (`PL-J9S0`): it refuses a `claude/*` branch whose work outside the queue claims nothing, and a claim ordering behind another live claim; `--hint PATH` is the first-edit hook's half of the same question, and `--hint-changed` asks it of every file the checkout has changed, for the hook's run after a Bash call, which names no path (`PL-RXFK`)
├── branch_sweep.py       # archives, then deletes, every `claude/*` branch whose work is finished, because GitHub deletes a head branch only when its own pull request merges and a session cannot delete one at all (`PL-X8SV`); it adds no judgment of its own - a branch stays while a pull request is open from or onto it, `claims.unfinished_work` or a release cut holds it, `vcs.stranded` finds the only copy of an item or an edit to one still open on the base, `vcs.orphaned` or `left_behind_check.py` finds commits a merged pull request left behind, or its last commit is under 72 hours old; a worker branch whose latest run record is reviewed `sent-back` is kept only by an open pull request, the only copy of an item or the grace period (`PL-W5JR`); one atomic push, leased on the tip it judged, copies that tip to `refs/archive/<branch>/<tip>` and deletes the branch, so a wrong call costs a restore rather than work; any reading that fails pushes nothing and exits 1; `.github/workflows/branch-sweep.yml` runs it daily
├── dead_ends.py          # emits `docs/dead-ends.md`'s entry lines into session context at start, and holds that emitted half - never the file's preamble, which is instructions for adding an entry rather than for reading one - to 30 entries and 4,000 bytes, because a `SessionStart` hook's output is resent on every turn and an unbounded always-loaded store measurably degrades an agent rather than merely costing tokens; refuses an entry citing an id that resolves to nothing, since `bin/docket show <id>` is the entry's whole retrieval path
├── check_support.py     # what the source checks share, in one home: a scoped `ast` walk, a baseline by file that only shrinks with its overflow, stale-entry and report-line helpers, and the `--root` reading and report printing every check's `main` did by hand; pylint's duplicate-code check found the copies (`PL-VWXL`)
├── ci_runs.py            # keeps `docs/ci-runs.tsv`, one row per CI workflow run, by asking GitHub for each day since the newest row, because GitHub deletes a run 90 days after it ran and the model review scores an item partly by the red runs on its pull request; keeps a row GitHub no longer returns and a pull request link GitHub dropped, and refuses a day at the listing's 1,000-run cap rather than read it short (`PL-4SFQ`)
├── context_reading.py    # reports this session's own context size - `baseline` (its first request: system prompt, resident instructions, session-start digest, any skill the harness preloaded), `context` (its latest request) and the `spend` between them - by reading the transcript the harness appends to as each request happens, `$CLAUDE_CONFIG_DIR/projects/*/$CLAUDE_CODE_SESSION_ID.jsonl` - every such file, since a session whose working directory moved has one under each directory, with the requests put in time order and no spend printed where the first record read does not start the session or the latest request is smaller than the first (`PL-PLT9`) - summing `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` off each assistant record's `message.usage`; deduplicates the several records the harness writes per request, and skips `isSidechain` records because a subagent's context never entered this window. It exists because the instrument `CLAUDE.md` prescribes for the spend budget cannot answer the question it is asked: `get_session`'s `context_usage.used_tokens` is written at turn boundaries, so a session working a whole item inside one turn reads a value that never moves - 0 before its first boundary, measured across all six concurrently running sessions on 2026-09-21 while this read 112,857 from the same transcript. Prints three numbers and judges none of them; the budget is stated against `spend` (project owner, 2026-09-21, ratified, over the absolute reading), and `CLAUDE.md` § "Session and tool-use efficiency" is where that is decided
├── contrast_check.py     # computes every declared color requirement's WCAG 2.2 contrast ratio from the constants in `app/`, and holds each to its declared minimum, taking the better channel where an element's edge can be carried by either its fill or its border; and states in its report line how many control kinds declare no colour at all, which it structurally cannot measure and `tests/integration/test_simulation_view.py` names
├── config_home_check.py  # refuses a configuration fact whose copy differs from its home: the Python release in `.python-version`, ruff, mypy and the README; the `requires-python` range in `drift.yml`; the oldest uv; the mutmut pin; each workflow action's version; `libegl1`; the test trees; the clinical floor's paths; the simulator's and the apparatus's path lists; the `uv sync`, `ruff format`, `mypy` and whole-suite commands; the tools run under `uv run python`; two timeouts; and the effort in `.claude/settings.json` and the Explore subagent's model, against `docket.toml`'s `[models]` table (`PL-0XDM`). A copy it can no longer find fails too, so a reworded sentence cannot leave it checking nothing (`PL-SH0W`)
├── core_vocabulary_check.py  # holds `core/`'s identifiers to the vocabulary `docs/MODEL.md` establishes, in the three ways that are decidable: every `ClassName.accessor` in the Symbols table's Code column resolves to a real attribute, property or field - an em dash being accepted only where the cell says what the code reads instead; none of the accessor names `PL-9SH6` retired comes back, matched whole rather than as substrings, so that an identifier merely containing a retired name is not accused of reviving it - a rule with no live counterexample in `core/` since `PL-6KNM` renamed `require_concentration_fraction` to `require_fraction`, and `PL-JW9J` is where tightening it is decided; and every `*partition_coefficient` identifier names both of its phases in the declared outward order, gas then blood then tissue, so a coefficient cannot be written as its own reciprocal in a literature that calls one quantity tissue-gas, tissue-blood and blood tissue in a single chapter. It runs under `uv run python`, not at the 3.11 floor, because it parses `core/` with `ast`; whether a name is the one a reader who knows the domain would guess stays a judgment and is deliberately not scripted
├── diff_mutation.py      # runs mutmut on the functions a branch changed in the mutated modules, against every unit test file that imports the simulator, and reports each function's mutants, the diff of each survivor, and the changed lines that mutmut cannot mutate. It reruns each mutant that mutmut calls a timeout, because mutmut reports any exception in its worker as a timeout. `make mutate` runs it, and `make mutate ARGS=--all` mutates the whole tree. `--verdict` prints the run as JSON for `bin/docket verify`, which refuses a branch while a mutant of a line it changed survives (`PL-CZXN`); otherwise it measures, as `PL-Y1PS` records. `docs/mutation-testing.md` has the recipe, the pitfalls and the baselines
├── doc_check.py          # validates this map and `docs/ARCHITECTURE.md`'s, MODEL.md's provenance table and its marked prose values, the data files' declared source tiers, citations - every path and section the documentation cites, the quoted sections in every live `docs/items/` brief and every source docstring, since those two are where this project writes most of them, and a live brief's path citations against the files git history shows the tree once held, since a brief also names files its work will create; a leading `/` is read from the repository root - markdown math syntax, that every sentence naming a host beside a refusal carries the date it was probed, ROADMAP.md's release train, with no "not yet" status written under it, its frozen-list counts and current baseline, the current gate's self-cleared group against its `Required scope`, and the current gate's membership against the queue - unconditionally for the queue's `safety`- and `science`-classed items, and as a recorded disposition, placed or deferred, for every other open debt item; that no milestone names one id under both its `Required scope` and its `Explicitly out of scope`, advising where the words introducing a scope entry's declaration carry exclusion language; that every `Required scope` entry declares its members in a `(queue item ...)` slot where the section's other entries declare, and that the queue holds every id so declared; that every test `MODEL.md` names resolves to one that exists; that every closed release tag's span is covered by notes naming each closing pull request inside it - the release's own cut excepted, being inside its own span by construction and stamped by the next release, and the newest span excepted, whose pointer would have to name a release nobody has cut; reports resident instruction size; and, beside the documentation it holds to the tree, the Makefile's own invocations held to CI's and to each other, such as `make check`'s coverage gate and the `--no-cache` on every `ruff check` recipe line
├── doc_quote_check.py   # reports each quotation of Claude Code's documentation that its page on code.claude.com no longer contains, or that its quoting file no longer contains, read from the record `doc_quotes.toml` beside it, because the pages change over weeks and `PL-124X` found 4 of 16 quoted strings gone; a page it cannot read is reported and fails the run, since an uncompared quotation has not been shown current; it reads the network, so `drift.yml`'s weekly `doc-quotes` job runs it rather than `make check`, and a session runs it by hand before relying on a quotation (`PL-S7LT`)
├── doc_quotes.toml       # the record `doc_quote_check.py` reads: for each quotation, the file that quotes it, the page it quotes and the quoted text
├── duplicate_code_check.py  # runs pylint's duplicate-code check (`R0801`) alone over `src/`, `tools/` and docket, and refuses a pair of modules with more copied blocks than `ALLOWED_BLOCKS` allows, or fewer, so the baseline only shrinks; keyed by the pair rather than by line, so moving a block does not fail; under `uv run python`, because pylint is a `dev` dependency (`PL-VWXL`)
├── effort_trial.py       # the effort trial (`PL-HYRM`, `PL-8MZ9`): the session-start hook runs it in every cloud session. It takes the arm from a hash of the hook's session id, `xhigh` for about one session in two and `high` otherwise, writes it as `effortLevel` and `maxEffortLevel` in `.claude/settings.local.json`, and then prints the line naming it in the session-start digest, which is the trial's record of the arm
├── fact_home_check.py    # refuses a second reader of a fact the apparatus already answers, outside the module that owns it - a `subprocess` call whose argv starts with `git` outside `docket.vcs` and the hooks' `_git`; a recursive walk of the tree outside `docket.vcs.tracked_files`, and `docket.grep`'s model of what `grep -r` reads, which is the disk; the GitHub API's host outside `open_pull_requests.py`; a `main` or `origin/main` literal outside `docket.vcs`; `shlex.split` or `shlex.shlex` outside `docket.shell` and the hooks' `shell_split.py` - an upper-case module-level name defined in two apparatus files, or one call, one repository path or one plain string bound under two names, a string two facts share passing only while `DISTINCT_WORDS` lists every name that binds it (`PL-MM3Q`, `PL-S08Z`, `PL-3PKN`), and a membership test of `OPEN_STATUSES` or `CLOSED_STATUSES` or an `isdigit`, `int` or pattern match of the `pr` field outside `docket.model` (`PL-N4FP`), and any other `isdigit`, `isdecimal` or `isnumeric` call outside `docket.digits` (`PL-PNGQ`), against a baseline keyed by file, rule and scope that fails when it grows and when an entry goes stale, and that is empty since `PL-LGDV` drained it, because three generator heads stating this principle closed on enumerated sweeps and re-entered while nothing refused the next copy (`PL-4S6C`)
├── fixture_id_check.py   # refuses a `PL-` literal outside `store.ID_ALPHABET` - Crockford base32 minus the vowels, four characters, or the three digits the historical ids use - because `read_items` takes the `id` field verbatim, so such a literal parses and behaves like any other fixture right up to the moment something applies `ID_PATTERN` to it and matches nothing at all, leaving every assertion resting on it green against a broken implementation (`test_roadmap.py` spent seventeen days that way, and `PL-GXPP` 261 substitutions removing the literal); it reads the grammar with `store.ID_RE` rather than restating it, walks every `*.py` in the repository for string *values* and for keyword-argument names translated `_` to `-` - the second because an id cannot be an identifier, so a helper keyed by one takes `PL_8888_open` and puts the hyphens back, a spelling in which no `PL-` token appears in the source at all and which is how the `doc_check` fixtures were written until `PL-L609`; scoped to `ast.keyword.arg` rather than to identifiers at large, which is the whole of what keeps `PL_PREFIX` out of it, measured 2026-09-21 as 21 of 8,098 keyword arguments carrying an uppercase letter and 17 of those Qt's `ignoreBounds`, `rateLimit` and `userData` - with docstrings dropped so that an id discussed in prose needs nothing, reporting a file's findings in line order across both passes, and line-scans every non-Python file under `.claude/`, a token joined where its format carries one across a line break - a shell script's or a Markdown shell fence's backslash-newline, as bash reads it (`PL-WG6S`), and a TOML multi-line string's line-ending backslash or an escaped line break in a front matter double-quoted scalar (`PL-HKR5`), and `.claude/settings.json` read through `json`, its escapes decoded and a hook's command joined as the shell joins it (`PL-YPLM`) - where the rule is exact without a parser - measured 2026-09-21, every failing token in that tree was a defect, 2 of 2 - while `docs/`, `ROADMAP.md` and the item store stay out because there prose about a malformed id is the norm and `PL-GXPP`'s brief alone names seventeen; a name that is deliberately not an id, a rejection fixture or a `glob("PL-K*.md")` pattern, says so with a `not-an-id` marker on any line it spans. In both halves a token is judged only where it is written the way an id is - `PL-` and one whole word of capitals and digits, the only characters an id holds - so prose naming the prefix, `PL-prefixed`, is not read as one, where the prefix alone once made it a finding (`PL-VH5V`). A second rule refuses a second *spelling* of the grammar rather than a bad literal: a `PL-` followed by a character class closed by a counted quantifier, which is a copy of `store.ID_LENGTH` with a copy of the alphabet in front of it, the prefix matched in either case because a branch-name pattern spells it `pl-` and `vcs.BRANCH_ID_RE` was such a copy the rule could not see (`PL-PB8V`), because five tools wrote their own and every one drifted - all of them admitting the vowels the store cannot mint, and the four written `{4}` blind to the 43 historical three-digit ids, which cost `generator_check.py` 219 citation edges and one wrong printed signal (`PL-KYW3`); the counted quantifier is what makes that rule exact enough to fail the build, since an open-ended `PL-[A-Za-z0-9]+` claims to know nothing about the grammar and is left alone - `CANDIDATE_RE` itself included - and it is scoped to what a module *runs* rather than to prose or to `.claude/`, a regex being read rather than copied, so that no exemption is needed anywhere in the tree as it stands. It runs under `uv run python` for the reason `workflow_paths_check.py` does, parsing `tests/` and `src/` where the source targets 3.14; the rule was `subprojects/docket/tests/test_store.py`'s until `PL-7922`, where it globbed that one directory and so reached neither `tests/unit/` nor the advisory `tools/generator_check.py` prints
├── generator_check.py    # surfaces the `touches` clusters worth a session's judgment about a root cause - three or more open items, plus at least one signal: three of them sharing a `feature`, one of them cited by three or more other open items, or a self-generation ratio of at least 1.0 over the path's closures - and claims none of them is a generator, because a generator is a recorded fact (`root-cause-of:` on the causing item) rather than anything a measurement can decide; the ratio counts only children landing back in the same cluster, since a session closing an item captures whatever else it noticed and those captures attribute to the item it was working, so counting all of them rates any heavily-worked file a generator - `vcs.py` reads 2.33 that way against 0.71 measured properly, and `core/` 5.08 against 0.17; spawn attribution is the commit that adds an item file leading its subject with the id of the item being worked, which is `PL-6ZQY`'s own method; declines the ratio rather than printing 0.00 where a path has no closures; advisory, and exits 0 whatever it finds
├── glyph_check.py        # refuses a non-ASCII character that nobody has confirmed the client can draw, from any string that can reach a reader - every string literal outside a docstring under `app/` and `core/`, and every string in the `data/` JSON - because `→` (U+2192) has no glyph in the Flutter client, drew as a replacement box in the control-change list, and no test in this repository could see it: every string assertion here compares text the same font-less Python process produced; the allowlist is per character rather than per Unicode block, and each entry records what was rendered and looked at
├── headless_worker.py    # runs one `claude -p` worker per delegable item on the owner's machine, on the monthly API credit: a clone and a `claude/<id>-worker` branch per run, the clone removed once everything in it is pushed and kept with its log otherwise (`PL-TX7K`), a per-run dollar cap, a batch that starts from the Console's credit-left figure and stops before a run it cannot cover (`PL-NQ0M`) or after any failed run (`PL-44SP`), a `caffeinate` hold on the Mac's idle sleep (`PL-BT70`), a refusal before any spend when the bash or make on `PATH` is older than `make check` needs (`PL-44R1`), the model and effort `docket.toml`'s `[models]` table chooses for each item as the role `worker`, with `--model` as an override (`PL-0XDM`), `--no-push` for a trial whose work must stay local (`PL-80R5`), and a record of each pushed run committed to its branch for review (`PL-87BR`)
├── hook_blocks.py      # copies the guards' local refusal log into `docs/hook-blocks/`, one file per recording branch so two branches never write one file, when `bin/docket record` runs it as `record_command`; `count` prints each guard's refusals and sessions from those files (`PL-SG93`)
├── import_boundary_check.py  # fails the build on any import its `BOUNDARIES` table confines elsewhere: `pydantic` anywhere under `src/anesthesia_sim/` other than `core/parameters.py`; `time`, `datetime`, `random`, `secrets` or `uuid` in any module under `core/`; `flet` and `flet_charts` anywhere under `src/anesthesia_sim/`, the port being complete; `PySide6`, `pyqtgraph` or `numpy` in any module under `core/`; and `anesthesia_sim.app` in any module under `core/`, matched against every dotted name an import makes available with relative imports resolved - so the payload/dataclass boundary, the never-wall-clock rule, the toolkit-independence rule and the layering's one direction are measured rather than asserted
├── ignore_check.py       # evaluates warn_unused_ignores over the two test trees `[tool.mypy] files` excludes, so an inert `type: ignore` fails the build
├── item_reads.py         # reports, from the local untracked `.docket-reads.log` that `.claude/hooks/item_read_log.py` writes, how many distinct items sessions actually open, what share of those are closed, and how many citation edges are traversed within a session - the read-side measurements every argument about the store's shape had been assuming; states the sample size first and chooses between none of the readings a low count admits
├── left_behind_check.py  # names the commits a branch carries past the head its newest merged pull request merged, because nothing merges a merged pull request a second time and a push made after the merge lands nowhere with no conflict, red check or advisory (`#284`); exact rather than a content comparison - the tip is compared by ancestry against the frozen `refs/pull/<n>/head`, read with one `ls-remote`, so a squash, a base that rewrote the file afterwards and identical lines from two sessions cannot confound it the way they have confounded `vcs.orphaned`, which stays beside it as the half that answers offline (`PL-VV4D`, `PL-BHVM`); the one case ancestry cannot see, a commit past the head whose change reached the base through another pull request, it puts to `vcs.change_landed`, the three-way replay `vcs.orphaned` reads too, and reports as landed there, naming the pull request (`PL-GHHW`, `PL-PXZ3`); git records no link from a branch to its pull request, so that mapping is GitHub's pull-request listing and needs a token; it declines, under its own prefix, on no network, no permission and a `refs/pull/<n>/head` GitHub has deleted (`PL-LF2C`), and never reads a missing answer as clear, because in the session-start digest that calls it silence is the all-clear; where it and `vcs.orphaned` disagree it prints the disagreement and wins
├── literal_home_check.py  # refuses a bare numeric literal anywhere under `src/anesthesia_sim/` outside the value of a module-level assignment - 0, 1 and 2 exempt, and never a `bool` - and a numeric constant defined in more than one module, so a number has one named home and a second copy cannot drift from the first; its `BASELINE` holds the literals the tree carried when it landed, keyed by file, scope and value rather than line, and may only shrink, and a finding names any constant of the same value without deciding that it is the same quantity (`PL-40SJ`)
├── main_ci_status.py     # reports the default branch's last quality verdict, and nothing at all when it was a success, because the whole-store `verify:` replay runs only on push to `main` and its failures therefore land on a run no pull request shows; a run newer than that verdict that was cancelled, or concluded `action_required`, gets a line of its own whatever the verdict, since its commit has no whole-store verdict and the one reported is an older commit's (`PL-JTHW`); its `FAILED` set is the one `update_armed.py` reads a check run's conclusion by (`PL-351H`); on a failure it makes a second request for the run's jobs and names the step that failed, because 93 of the 109 failures on record are the whole-store replay alone and a line naming no step cannot separate those from a broken tree (`PL-T83R`); it also prints a line when the median time of CI's pytest step over `main`'s five newest successful runs leaves the band of 0.5 to 1.3 times `PYTEST_BASELINE_S`, and says in that line when it could not read the time, so that its silence means the time was read and in the band (`PL-YY32`); it also prints a line naming each `drift.yml` job whose newest result on `main` is not a pass, judged by the job and not by its run, since that workflow reports and never gates and a red run nobody read went unmentioned for 17 days (`PL-JTWV`); the session-start hook calls it, it gates nothing, and it is not the only tool here that reads the network - `required_checks_check.py` does too and gates, and `pr_body_check.py` does in its `--record`, `--recover` and `--compare` modes
├── model_doc_review.py  # has the model `docket.toml`'s `[models]` table chooses for the role `review` read `docs/MODEL.md` against `src/anesthesia_sim/data/` once, on the owner's API credit, through the Message Batches API: one request per `##` section, each carrying the whole document and every data file behind one cache marker so that a contradiction between sections is found; `estimate` prints the cost bound, `submit` refuses a bound above the credit left, and `fetch` writes one findings file for a session to check and file (`PL-5S71`). Its model, effort and price come from the table, and a model the table has no price for is refused (`PL-0XDM`)
├── model_home_check.py  # refuses a Claude model id written outside `docket.toml`'s `[models]` table, the records (the session ledger, worker runs, closed items), the tests and the copies registered in its `COPIES` with a reason; an open item is held to it too, because a stale model reached a session through one (`PL-0XDM`, `PL-J9VC`)
├── new_prose.py         # prints each docstring and comment of 30 words or more that a branch added or changed in `src/` or in a file under `tests/` that imports the simulator, with its rows and the code around it, so that the close-out's fresh reviewer reads no file. `.claude/skills/docket/modes/close-out.md` step 8 runs it, and `PL-PRCS` records why
├── open_pull_requests.py  # prints the branch name and number of every open pull request, one per line, so `bin/docket flight` can tell a branch waiting on review from one nobody opened - the half of "is anybody still on this branch" that git cannot answer, and the half that left `claude/hopeful-allen-tetrje` reported as live work for three hours with every item on it closed - and can say on every row which pull request is open, since a branch outlives its session and an age alone cannot say so in the first hour (`PL-7TVT`); the contract is the exit status, zero meaning it looked and non-zero with an empty stdout meaning it could not, because "could not look" read as "nothing is open" would announce that finished work has stalled on every branch under review; it lives here rather than in `subprojects/docket/` for the reason `main_ci_status.py` does - that package answers from a bare checkout with no network and knows nothing about GitHub - and `docket.toml`'s `open_pull_requests_command` is what points `flight` at it; `pr_title_check.py` shares the request rather than making its own, so the token, the timeout and the every-failure-is-a-skip rule have one spelling; every tool that asks the API builds its request with `api_request` and reads `GITHUB_API`, and reads which repository `origin` is through `repo_slug`, so the host, the version, the headers and the slug have one spelling too (`PL-LGDV`); `--newest BRANCH BASE` prints `NUMBER STATE HEAD` for the newest pull request from one branch, which `bin/docket branch` and `bin/docket arm` read through `newest_pull_request_command` as the merge evidence a squash leaves no commit of, so a branch whose pull request merged is told to restart rather than to merge the base in (`PL-8BR0`); `--auto-merge NUMBER` prints `on TIME` or `off TIME` for the latest switch of a pull request's auto-merge, which `bin/docket arm` reads through `auto_merge_command` so that a switch off no session recorded as its own holds the pull request (`PL-8TPV`); `left_behind_check.py` reads that newest pull request through `newest` and `update_armed.py` the open listing through `every_page`, which reads to a short page and declines where a page moved under the read, so the tools cannot disagree about either (`PL-351H`)
├── possessive_section_check.py  # reports a possessive citation whose quotation matches a heading in the file it names, and prints the `§` line it should become, because admitting the possessive to `CITATION_CONNECTIVE` (`PL-316G`) settled whether such a citation is *checked* and left what it tells a reader: `§` says the quotation is a section title and the possessive says nothing, this project writing it to quote a sentence as often as to cite a section. Only the direction that is a fact about the tree is reported - a quotation matching a heading is a section citation - while one matching no heading may be a faithful quotation of prose and is left alone, which is the judgment half `CLAUDE.md` refuses to script. A `**Bold.**` marker is in that half, being often a lead sentence as well as a title, so either form quotes one correctly (`PL-FKH6`). Closed briefs never reach it, `_quoting_sources` having exempted them since `PL-ZM8P`
├── pr_body_check.py      # reports a squash commit on `main` that landed with no body and no file under `docs/pr-bodies/`, because the squash commit's body is the record of a pull request's body and a merge client can still send an empty one (`PL-843V`; `PL-3PH2` retired the per-pull-request copy `PL-979D` kept in the tree); the default mode, run by hand at each release, prints a verdict either way, and `--recover` fetches each lost body from the public API into `docs/pr-bodies/<N>.md` under a header dating the fetch; `--anchors`, in `make check`, refuses a recovered file whose `commit:` is not a first-parent commit of the default branch, and says it checked nothing on a shallow clone; `--compare` is a hand-run measurement of how far squash bodies drift from their pull requests, a drift accepted rather than repaired; `--screen` reads a pull request call from stdin and refuses a title or body holding an email address other than `noreply@anthropic.com`, run before the call by `.claude/hooks/pr-body-email-guard.sh` because GitHub publishes a body at once (`PL-7K31`)
├── product_paths.py      # where the simulator's package lives - `src/anesthesia_sim` and its `core`, `app`, `data` and `layout` trees - which five tools spelt for themselves until `PL-H5T9`; every tool under `tools/` that reads the package imports it, and `docket` keeps its own spelling because it cannot import `tools/`
├── pr_record_check.py    # refuses a pull request until every item its branch closes records `pr:` equal to the pull request's own number, which the `pull_request` event is the one point in the workflow that knows (`PL-HMZZ`); the number is written on the closing branch by `bin/docket record N` before the merge, so which pull request closed an item is a recorded fact rather than one inferred afterwards from squash subjects and item-file history - the inference that ten items in three weeks were the shapes of history that misled, retired with the count that 1,143 of 1,143 done items carried the field once the last 43 were written by it; a sibling of `pr_title_check.py` that reads the same two trees through its helpers, runs as a step of the same required job, and under `--discover` lets `make check` ask the branch's own open pull request, skipping silently on every way that lookup can fail
├── pr_title_check.py     # refuses a pull request whose title does not lead with the ids its branch closes, because the squash-merge subject is taken from that title and is the one line of `main`'s history that says which items a change was about; it no longer stands for provenance, which `pr_record_check.py` beside it records before the merge (`PL-M7W1`, `PL-HMZZ`)
├── required_checks_check.py  # reconciles the jobs that report a status check on `pull_request`, parsed from `.github/workflows/`, against the status checks branch protection requires, read from the GitHub API - in both directions, because a required name nothing reports leaves every pull request pending forever on a check that cannot arrive (`PL-KPP1`, `#377`) and a reporting job nothing requires can go red without blocking a merge (`PL-H8YD`, `#654`); it needs no credential at all, since on a public repository `GET /repos/{owner}/{repo}/branches/{branch}` answers unauthenticated where the `.../protection` endpoint the question was first asked of needs an `administration` grant a workflow token can never hold; it reads both settings surfaces, classic branch protection and rulesets, and treats an empty union as a failure rather than as agreement, because a migration between them would otherwise leave it passing while requiring nothing; and it refuses rather than guesses a matrix job, a reusable workflow call or an unreachable API, a job silently dropped from the reporting set being indistinguishable from nothing to reconcile. It runs as a step inside `quality.yml`'s `checks-part-1` job rather than as a job of its own, so the check that guards the required list adds no entry to it; that job and `checks-part-2` report on a pull request without being required, each declaring `# not-required:` because the required `checks` job needs both and fails unless both succeeded (`PL-T9X9`), and it is one of several tools here that read the network, `main_ci_status.py`, `open_pull_requests.py`, `left_behind_check.py` and `pr_body_check.py`'s `--record`, `--recover` and `--compare` modes among them
├── restated_constants.py  # names each test under `tests/` that copies the value of a numeric constant in `core/supported_ranges.py` instead of importing its name: it runs the suite once per constant with the constant widened to a wrong value through the one environment variable `tests/conftest.py` reads, and reports each failing test whose file does not import the name and that passes without the perturbation; a floor at zero is left alone, and a failure in a file that imports `subprocess` is listed as not judged; a run it could not judge fails; one suite per constant is too slow for a gate, so `drift.yml`'s monthly `restated-constants` job runs it (`PL-0Z0F`)
├── rules_paths_check.py  # refuses a `paths:` entry in any rule file under `.claude/rules/`, nested ones included since Claude Code discovers them recursively, that does not begin with `/`, or whose literal prefix resolves to nothing, because an unanchored glob also matches its name at any depth while `./` and a typo'd prefix match nothing at all — so a rule's real scope can differ silently from the one it declares, in either direction. It also holds the apparatus set's three copies (in `CLAUDE.md`, `expert-review.md` and `apparatus-standard.md`'s `paths:`) to each other and to `workflow_paths`, so a path added to the lane must be placed in the set or in its `LANE_ONLY` list
├── skill_start_eval.py   # measures whether a skill starts on the requests it should (`PL-SN2Z`): runs each prompt in `skill_start_prompts.json` as a fresh headless `claude -p` session in a scratch clone, once with the skill on and, for a prompt that should start it, once with it turned off through `skillOverrides`, and counts a start only from a `Skill` tool call naming the skill. Each session runs in `dontAsk` mode, so it can read but not act. A run it cannot read is reported apart and left out of every rate. Every run is billed to the account the clone's `claude` signs in with, so it runs by hand and never in CI
├── skill_start_prompts.json  # the prompts `skill_start_eval.py` runs, in two groups: requests that should start the `docket` skill, several of which never say queue, item or docket, and ordinary requests that should not
├── source_tier_counts.py  # prints the source and tier behind every stored value in the data files, per file and in total, read from each `sources` entry's `authority_for`. These are the counts `docs/MODEL.md` § "Source hierarchy" states in prose. It prints no count at all while `check_source_tiers` reports an error, since a plausible count from malformed data is worse than none. It gates nothing, by the project owner's decision recorded on `PL-9LXK`: it prints the counts and never checks or rewrites the sentence that states them
├── tag_release.py        # tags the release `main` declares on its cut, the commit that added its notes, because that squash merge exists only once the release pull request merges and a session cannot push a tag ref (`PL-2FY6`, `PL-N936`); it reads everything from `origin/main` after fetching, changes nothing where `main` adds no notes for the version or `origin` already holds the tag on the cut, clears a withdrawn tag held here only once `origin` has answered it lacks it (`PL-PNW6`), reads the tag back from `origin` before reporting a push as landed because a session's tag push exits clean and lands nothing (`PL-N936`), and declines, exiting 1, where git will not answer, the clone is shallow, the notes were added more than once or the tag names another commit; `.github/workflows/tag-release.yml` runs it with `--apply` on each push to `main` that changes a release's notes
├── update_armed.py       # brings `main` into every armed pull request it has moved past, because `main` merges only an up-to-date branch and auto-merge never updates one, so an armed pull request whose session has ended waited at "behind" for somebody to click Update branch (`PL-S5MF`); it passes over a draft, a fork, one level with `main` and one whose required check already failed on its head, updates the rest on the head it read, and lists what it read; it writes only with `UPDATE_BRANCH_TOKEN`, lists what it would have updated without it, and exits 1 when a reading fails or GitHub refuses the token; `.github/workflows/update-armed.yml` runs it on each push to `main`
├── workflow_paths_check.py  # holds `docket.toml`'s hand-maintained lists to the tree: `workflow_paths` to what each test file under `tests/` imports — apparatus when it does not import `anesthesia_sim`, the simulator's when it does — because the apparatus tests living in the simulator's test tree were listed by hand and drifted, and an item declaring one alongside the script it tests is set aside from both lanes as reaching both halves, offered only by a `docket next` run without a lane, while a support module pytest does not collect, such as `tests/conftest.py`, imports what it needs rather than what it serves and is held only to the second half, its side otherwise being the list's to declare (`PL-12P8`); every tracked path outside `tests/` to `workflow_paths` or `product_paths`, refusing one under neither and naming both lines that would place it, because a path nobody listed was the simulator's by default and one such file had set 22 items aside from both lanes (`PL-8ZGY`); and `gate_paths` to every `ruff.toml` in the tree, because an uncovered linter config is one `docket verify`'s "the checks themselves are unedited" audit will not defend
├── worker_runs.py       # owns the record of each headless worker run in `docs/worker-runs/`: `headless_worker.py` writes one per pushed run and commits it to the worker's branch, `review` adds the reviewing session's outcome, and `check`, in `make check` and CI, refuses a record with no review or a malformed field, so headless and chat work can be compared (`PL-87BR`)
└── ruff.toml             # pins the formatter to the oldest interpreter these tools have to parse under
```

`tools/doc_check.py` checks this document against the code. It compares the
package-map tree above with the tree on disk, in both directions. It does the
same for the map of `src/anesthesia_sim/` in `docs/ARCHITECTURE.md`. So
`make check` fails when a module is added without a line in its map, or when a
line is left behind after a deletion. It also fails when a document's map is
gone, rather than passing on the strength of the other document's map. That is
why the trees list every module individually. A directory drawn with no
children beneath it stands for its whole subtree and is not expanded.
`__init__.py` is excluded throughout. Neither live tree draws such a
directory, so `tests/unit/test_doc_check.py` tests the rule in both
directions, in `test_childless_directory_covers_its_whole_subtree` and
`test_a_childless_directory_covers_nothing_outside_its_own_subtree`. The same
tool checks the provenance table in `docs/MODEL.md` against the data files. It
also resolves every path and section heading that the documentation cites.

Its `check_source_tiers` check compares the same data files with
`docs/MODEL.md` § "Source hierarchy". Every `sources` entry declares three
things: a `tier` from the closed vocabulary, an `adopted` flag, and an
`authority_for` list. The list must be non-empty exactly when the entry is
adopted. It must name only the file's own stored values, and none of them
twice. A file with no entry that is both `primary` and `adopted` records a
`provenance_gap`. The check decides only what a file *declares*. Deciding
whether a citation labelled `primary` really is a primary measurement of the
quantity needs somebody who has read the paper. A tool that guessed at that,
by author, by journal or by a denylist on a product name, would be
authoritative and wrong. The provenance table check already works on the same
split. It decides that a documented key exists and has the stated value. It
never decides that the value is right.

`tools/pr_title_check.py` and `tools/pr_record_check.py` are the two halves of
the lesson from `PL-2XTF`, as `PL-HMZZ` divided it again. A squash merge takes
its subject from the pull request title. So a title that names none of the
items it closes lands a subject that says nothing about them. That happened
once, on a title generated by a user interface, which closed three items. The
title check stops it while the title can still be edited. The title does not
carry provenance. Which pull request closed an item used to be recovered from
that subject, and then from the item file's own history. Every new shape of
history misled the recovery until the recovery got an exception of its own. Now
the branch that closes an item writes the pull request number onto the closure.
The record check refuses the pull request until every closure carries that
number. It does this at the one point in the workflow that knows the pull
request's own number.

The title check runs in `.github/workflows/pr-title.yml`, which takes the
title from `PR_TITLE`. It also runs in `make check` and `make pr-title`, which
pass `--discover` and read the title from the branch's own open pull request
instead (`PL-J3BB`). Until then it ran only in CI. That made it the one gate
that a session could not run before pushing. The check compares the title
against *what the branch closes*. A branch closes more items as it goes, so a
correct title goes stale the moment the next item closes on it. Every way the
lookup can fail is a silent skip: no token, no network, or no pull request
open yet. So `make check` stays green offline.

`tools/branch_id_check.py` is the same kind of guard, aimed at the other end
of the same problem. The two checks do not overlap. The title check asks
whether a pull request names the items it *closes*. For a branch that closes
none, it returns "no id is owed". That case is exactly the unfiled repository
housekeeping that `PL-CP74` found colliding. `docket flight`, `show`, `next`,
`concurrent` and the session-start digest all check the same question:
"is anybody already on this?" They check it by matching a `PL-` id in a branch
name or at the front of a commit subject. So every one of them treats a
branch that carries no id as nobody's work. They go on doing so even after
both sessions have pushed.

That argument is about agent sessions. So the check applies only to their
branch namespace, `claude/*`, and passes any branch outside it. A contributor
has no queue and no id. Requiring an id once refused `#394`, the project
owner's own web-UI edit to the README, in the required job (`PL-8P6D`).
[`CONTRIBUTING.md`](../CONTRIBUTING.md) is the route that this leaves open to
contributors.

The branch check imports `BRANCH_ID_RE` and `leading_ids` from `docket.vcs`
rather than matching ids its own way. A check looser than the guard it
protects would certify a branch as visible while `docket flight` still cannot
see it. The gate would be green while the guarantee is void. One commit
carrying an id is enough. That keeps the tool out of a judgment it must not
make: how small a piece of work is too small to file. That judgment is made in
`.claude/skills/docket/modes/capture.md`, under
"Mode: housekeeping nobody filed". A fix riding inside a commit that an id
already leads needs no item of its own. A release commit is exempt, exactly.
`make release` writes that subject, and a release commit closes no item.

`tools/contrast_check.py` checks the interface against the accessibility target
that `docs/MODEL.md` states, WCAG 2.2 Level AA. It reads the color constants
with `ast` rather than importing them, because the interface imports PySide6,
and a bare checkout or a hook has no PySide6 to import. It reads the constants
from every module under `app/`, the theme first and then the rest in path
order, rather than from two named paths (`PL-BXB2`). Since `PL-2CS8`, every
color is declared in `app/theme.py`. `check_colors_live_in_the_theme` fails the
build on a color declared anywhere else. That covers a named constant, and also
a hex color written inline, whether in a call or inside a longer string such as
a stylesheet (`PL-PXT7`). Every module is still parsed for colors as well. So a
color put back outside the theme is measured rather than lost, which is the
failure that `PL-2CS8` was filed for. Its `REQUIREMENTS` table is the
specification. Each entry names the colors that appear on screen together, the
success criterion, the minimum, and the reason. The reason cites, by symbol,
the code that draws those colors. Most entries are one foreground against one
background. Some elements have an edge that either of two channels can carry.
The agent badges are an example: each is a fill with a border in the agent's
own text color. Such an entry declares both channels and is judged by the
better one. The reason is that measuring such an element one channel at a time
reports a false shortfall, whichever channel is picked (`PL-GNN1`). The tool
evaluates that table and decides nothing else. Which colors matter, which
channels an element really has, and whether a non-color channel is genuinely
redundant are judgments. `.claude/rules/ui-color.md` carries those judgments.
The tool does decide one thing about the prose, which is the half that a script
can decide. A description may cite no line number, and every symbol it names
must exist in some module under `app/`. Those citations were line numbers until
`PL-GJDW`. All fourteen had rotted into unrelated code, so the tool's own
coverage could not be audited while it looked audited. Requirements that fall
short today are listed against the item that closes each one. A listed
shortfall that starts passing is an error, so a fix cannot leave its excuse
behind.

The tool measures one thing beyond the `REQUIREMENTS` table, and that one is a
hard error rather than a shortfall that can be listed. `TRACE_FLOOR` requires
each of the six chart traces to reach 3:1 against the panel under **four**
vision models. The first is the color as displayed. The other three simulate
protanopia, deuteranopia and tritanopia with the Brettel 1997 projection in
`DICHROMACY_TRANSFORMS`. The fourth model is the project's own bar rather than
the criterion's, because SC 1.4.11 is defined on the color that a display
emits. It is worth the extra arithmetic because `MUSCLE_COLOR` measured 3.19:1
on screen and 2.98:1 for a deuteranope. No normal-vision check could see that
difference (`PL-GVXP`). `--matrix` prints the pairwise separation across all
four models. That output is the evidence that these six traces cannot be
separated by color at all, and that the line style is doing the work.
`docs/MODEL.md` § "The six compartment traces" carries the tables, and the
limits on how far a simulated ratio may be relied on.

`tools/agent_identity_check.py` closes the one gap that the table structurally
cannot cover: a colour that the project never declares. Flet/Material painted a
disabled control's label in the theme's disabled-content grey. A Qt style does
the same from its palette's disabled role. Neither grey appears in any module
that `contrast_check.py` reads. So a requirement went on measuring the enabled
pair and reporting a pass. Meanwhile the agent's name sat grey on its own ISO
5360 fill for the whole of every run (`PL-61WW`). The rule this tool enforces
is the project owner's, from 2026-09-08. No control that carries agent identity
may be *rendered* disabled. So this project never claims the exemption that SC
1.4.3 gives an inactive component. That exemption settles a conformance claim.
It does not settle whether a reader can identify the running agent. The word
*rendered* is the one the rule depends on. A control may be `disabled` where it
is also `visible = not <the same expression>`. In the Qt spelling, which the
check reads since `PL-25KS`, a control may be `setDisabled(E)` where it is also
`setHidden(E)`. Either way, the control then draws nothing. The identity set is
not a second list to keep in step. It is whatever
`RunView._apply_agent_color_scheme` writes, because that method is already the
single writer of agent colour. A control can be given an agent colour outside
that method. In the Flet spelling, that happens where the control is
constructed. In Qt's, it happens through a `setStyleSheet` or `setItemData`
call afterwards. A control coloured that way and never written by the method is
the check's other error. That error is what keeps the coverage claim true
rather than merely asserted. The check reads every module under `app/` and
names none by path (`PL-V53R`). It finds the writer in whichever module holds
it, and requires exactly one. None is an error, and two means a second writer
of agent colour. Rule 1 reads the pairing inside the writer's own class, since
`self.X` names an attribute of that class. Rule 2 reads every method of every
class in every module except the writer. It skips the writer because the writer
can only write its own controls, and its body is the identity set itself. A
tree in which no `disabled` write can be read at all is an error rather than a
pass (`PL-0PJG`). The success line states how many such writes were read,
across how many modules, and how many were on identity controls. It also states
how many colourings rule 2 read in each spelling. So the success sentence
cannot be printed from nothing. Like the two tools above, this check decides
nothing else. Whether a control's identity is legible, and whether a pairing is
the right one for it, remain judgments.

**What a Qt port costs these two, measured rather than estimated (`PL-JRS3`).**
The dependency is split, and not in the way the question assumed. One tool
reads *values* and survives. The other reads Flet's *control objects* and goes
silent. This was measured on 2026-09-14. The measurement rewrote
`app/theme.py` and `app/simulation_view.py` on the AST, replacing every Flet
property assignment with the PySide6 setter call that supplants it. It then
ran both tools against the result.

`contrast_check.py` survives. Its colour input is module-level
`NAME = "#RRGGBB"` constants, which no toolkit owns. Every way of removing a
declared constant is loud. Renaming `FAT_COLOR` failed with the constant
named. Moving `SimulationView` to its own module failed with 68 unresolved
citations, from the symbol rule that `PL-J7C5` added for an unrelated reason.
`PL-B9PY` records that the port makes that move from the start. The tool's one
hole was **additive**, and `PL-BXB2` closed it before the port could open it.
A colour declared in a module other than the two that the tool then read was
measured by nothing and missed by nothing. A new chart-panel module holding a
selection colour at 1.07:1 on the panel passed with `0 errors`. The tool now
reads every module under `app/`. So that colour is measured and refused, and
an inline hex literal outside the theme is refused with it. The moved-class
probe resolves its citations instead of failing. The report's first line says
how many modules the tool read.

`agent_identity_check.py` did not survive, and its failure was worse than
silence. Rule 1 reads `self.X.disabled = EXPR` paired with
`self.X.visible = not EXPR`. PySide6 spells both as calls, so
`property_writes` returned nothing and the pairing loop ran zero times. On a
tree where all six identity controls are driven by `setEnabled()`, with no
paired hide, the check printed this line and exited 0:
"6 control(s) carry the agent colour, none of them rendered disabled". That
was an affirmative claim about a tree it had not measured. A reader could not
tell it apart from the same sentence when earned. `PL-0PJG` closed that gap
ahead of the port. Now a tree in which no `disabled` write is
read, in any class of any module, is an error. The error names the spelling
that the check does not read. So that probe fails on the first port commit
rather than passing through it, and the success line carries the count it rests
on. Whether the older tool went quiet depended on a choice that the port makes
incidentally. Porting the colour writes as well trips rule 2, and moving the
class trips the empty-set guard. Both of those failures are loud. But rule 2
then misdiagnoses: it reports that the writer "never writes" controls that it
does write, through `setStyleSheet`.

So the port's cost side gains one entry rather than two, and that entry is
specific. Rule 1 of `agent_identity_check.py` is inside the port's scope: it
must be taught the setter spelling. The empty-measurement error now demands
that teaching in the first commit that changes the spelling. Both tools were
widened to every module under `app/` ahead of the port (`PL-BXB2`, `PL-V53R`).
So the decomposition itself costs neither tool anything. `PL-25KS` paid that
one entry. Rule 1 now reads `setDisabled`/`setEnabled` paired with
`setHidden`/`setVisible`, as well as the property spelling. The identity set
counts every method that the single writer calls on a control, `setStyleSheet`
included.

`tools/glyph_check.py` covers the half of presentation correctness that no
string assertion here can check. Every such assertion compares text that the
same font-less Python process produced. So the suite is blind to whether the
client can *draw* what it is given. `→` (U+2192) has no glyph in the Flutter
client. On 2026-09-04 it drew as a replacement box in the control-change list,
in the arrow of `5.60% -> 0.95%` (`PL-8XPQ`). That arrow shows the direction of
a setting change, which is the one thing that line exists to state. The rule
is default-deny. Every non-ASCII character in a string that can reach a reader
must appear in `CONFIRMED`. Each entry there records what somebody rendered
and saw. The list is per character rather than per Unicode block, because
Latin-1 Supplement admits `¤`, `þ` and `ð` beside the `·`, `±` and `×` that this
interface has actually shown. A block set would admit thousands of characters
on the evidence of three. The tool reads three trees, not the one the item
first named. `app/` draws the strings. `core/` raises text that the view
prints verbatim: `_apply_setting` renders `f"Setting refused —
{error}"` from a `SimulationConfigurationError`. `data/` holds
`display_name`, which reaches the readouts and is the one place an edit lands
without touching Python. Documentation is exempt by a structural test: a string
that is a bare expression statement. That test is what keeps `§` out of a list
meant to record what was rendered. Like the tools above, this tool decides
nothing else. Whether an unlisted character *would* render needs a real client,
so the tool refuses and never approves.

`tools/import_boundary_check.py` measures four claims that the source makes
about itself. First, `_StrictPayload`'s docstring says that the
`_...Payload`/public-dataclass pairs exist so that the rest of `core/` never
imports Pydantic. Second, `docs/MODEL.md` "The reproducibility guarantee" says
that a run is a function of its inputs and of the number of steps taken, and of
nothing else. So the run loop reads no clock. Third, `docs/ARCHITECTURE.md`
§ "Layering" keeps simulation code independent of the UI toolkit. That rule was
a `CLAUDE.md` bullet until `PL-ZYHX` retired it to this tool on 2026-10-17.
`ROADMAP.md` § "Completed: v0.4.26 - the interface moves to Qt" turned the rule
into a figure, that exactly three modules imported Flet. That roadmap section
reasoned from the figure while the port ran. Fourth, `docs/ARCHITECTURE.md`
§ "Layering" says that the layers are enforced by import direction. No boundary
measured that for `core/` reaching into `app/` until a boundary could name a
module inside this package (`PL-YXFF`). Before that, a boundary named a root
package, and both layers are in the same root package, `anesthesia_sim`.
Nothing checked any of these claims. So a leak into a compartment would have
left the paragraphs looking verified while they were false, which is worse than
the coupling itself. The Flet count was true and unenforced until `PL-9KDK`.
`PySide6`, `pyqtgraph` and `numpy` are kept out of `core/` from before the
first import of any of them exists. So the port's first commit is measured,
rather than the rule being written after it. Its `BOUNDARIES` table is the
specification, and the tool decides nothing beyond it. Which packages ought to
be confined, and where an exception belongs, are judgments. They are written in
the table with the reason beside them. Three further states are errors. Each
closes a way the check could pass while meaning nothing: an allowance naming a
file that no longer exists, an allowance no longer used, and a declared tree
matching no source files at all.

The boundaries cover different trees, and the asymmetry is deliberate. The
Pydantic boundary covers `app/` as well as `core/`, so the rule says *exactly
one module in this package imports Pydantic*. The `time`, `datetime`, `random`,
`secrets` and `uuid` boundaries stop at `core/`, and they permit no module at
all there. They stop at `core/` because the guarantee they defend explicitly
allows the interface its wall clock. What the guarantee forbids is a tick's
real duration reaching the run. A test pins that asymmetry end-to-end. So
widening the tree to the whole package would fail on an import the design
permits, rather than passing quietly (`PL-J833`). The toolkit boundaries follow
the clock's shape, because `app/` is where a widget belongs. The exception is
Flet's two root packages, `flet` and `flet_charts`. Their boundaries cover the
whole package and permit no module at all, because the port is complete
(`PL-25KS`) and nothing under `src/` may import Flet again (`PL-7SVX`). While
the port ran, those boundaries named the three modules that the roadmap
counted. There were two boundaries because the Flet chart module imported
`flet_charts` without `flet`. So one boundary on `flet` alone would have
counted only two of the modules. The boundaries were the port's checklist,
through the tool's own unused-entry error. Each module that the port freed of
either package dropped its entry in the same commit, and the last module took
the allowances with it.

`tools/main_ci_status.py` gates nothing: no check fails because of what it
prints. It is also not the only tool here that reads the network.
`required_checks_check.py` reads the network too, and it is a gate. So do the
`--recover` and `--compare` modes of `pr_body_check.py`. (This document said
`main_ci_status.py` was the only one until the docs sweep in `PL-T83R`. The
comment above it in the tree had named `required_checks_check.py` beside it
ever since that tool landed. This document deliberately states no count,
because the last two attempts at one both went stale.)
`.github/workflows/quality.yml` runs the whole-store `verify:` replay only on
push to `main`. That was the decision in `PL-SDHR`, for two reasons. A pull
request cannot have changed whether some *other* item's work merged. And
replaying the store on every branch costs more than it buys. A pull request
*can* stop another item's command from discriminating, by editing a file that
the command reads. So the scoped replay covers those items too. The sweep on
`main` only picks up what is left over. It is not what catches those items
(`PL-XMNC`). The consequence is that when the replay on `main` fails, it fails
on a run that no pull request shows. `main` was red across three consecutive
merges while every session believed the tree was clean (`PL-0ZGK`). So the
loop is closed from the reading end, rather than by making every branch pay to
prevent the failure. `.claude/hooks/docket-digest.sh` calls
`main_ci_status.py` at session start. The tool prints one line when the last
verdict on `main` was not a success. It prints another when a run newer than
that verdict was cancelled (`PL-JTHW`). It prints one when the time of CI's
pytest step has drifted from its recorded baseline, or could not be read
(`PL-YY32`). And it prints one naming each `drift.yml` job whose newest result
on `main` is not a pass, or saying that those runs could not be read
(`PL-JTWV`).

`tools/context_reading.py` is the other tool that gates nothing, for a
different reason. `main_ci_status.py` reports on the repository. So it *could*
have been a check, and it is deliberately not one. `context_reading.py`
reports on the session that runs it. That is not a property of the tree, so
`make check` could never have an opinion about it. Wiring it into `make check`
would fire it on every commit to say something that is true of no commit.
`CLAUDE.md` retires checks of that shape rather than building them. A session
runs it when deciding whether to start an item, because that is the only
moment its result changes anything.

**The line names the step that failed, which is what makes it actionable.**
`PL-T83R` sorted all 819 completed push runs of `quality.yml` on `main`, from
2026-08-22 to 2026-09-20, by the step that failed. Of the 109 failures, 93
were the whole-store replay and 14 were the bare `bin/docket check`. One was a
pytest failure that asserted on `ROADMAP.md`, and one was a startup failure.
**Not one of them was a defect in `src/`.** In all 93 replay failures, the
bare `bin/docket check` step had passed earlier in the same job on the same
tree. That isolates the cause to the one report that `--verify` adds: an open
item whose own `verify:` command has flipped to passing. So when the replay is
the *only* failing step, the line says that the red comes from the queue
rather than the tree, and it hands over `bin/docket check --verify`. When
anything else failed, the line names the failing steps and interprets
nothing. It does so because the queue reading is sound only when the bare
check passed first, and that fact is the whole basis for the reading.

The failure *rate* was left alone in the same pass, and the reasoning is worth
keeping. `PL-T83R` was filed on a narrower window, 2026-09-05 to 2026-09-16,
which holds 74 of those 109 failures. Over that window, 32.7% of the pushes
that reached a verdict failed. That looks like a check nobody could act on.
But the 74 failures behind that rate are 8 episodes. Merges keep arriving
while `main` is red, so the per-push rate counts one outage once for each
merge. Two episodes hold 87% of the red time, and each ended with one cheap
commit. Suppressing the class of failure would have cost 93 findings, and
every one of them was real.

Two properties make it safe to run the tool unconditionally, and tests enforce
both. **It is silent unless there is something to act on.** The tool prints
nothing and exits 0 in four cases: a green `main`, no network, a non-GitHub
remote, or a malformed response. Silence matters because a line that appears
in every session trains a reader to skim the part of the output where a real
advisory appears. And **a `cancelled` run is not a
verdict**. The tool reports the newest run that actually reached a
conclusion. That skip mattered until `PL-SMN4`. Before then, every push to
`main` shared one concurrency group. So a merge that arrived while an earlier
one was still pending evicted it. Across the eleven days that arrangement
lasted, 31 of the 257 completed push runs on `main` ended `cancelled` without
starting any job. `quality.yml` now gives each push to `main` a group of its
own, which ends the eviction. A run that reaches this tool as `cancelled` is
now a hand cancellation or a lost runner. The commit behind such a run still
has no whole-store verdict that anything reports (`PL-JTHW`). The tool is
unauthenticated. The repository is public, so the tool reads no token and
needs none, which keeps a credential off a path that runs at session start.
The GitHub read deliberately does not live in `docket`, whose rule is that
every read must work from a bare offline tree.

`tools/ignore_check.py` covers what the type-check gate cannot.
`[tool.mypy] files` names `src`, `tools`, `.claude/hooks` and
`subprojects/docket/src`. Every `type: ignore` in the repository sits outside
that set. So the `warn_unused_ignores` that `strict = true` turns on never
read a single one. `ignore_check.py` runs mypy separately over `tests/` and
`subprojects/docket/tests/`, and takes two things from the output. The first
is an inert directive. The second is an unresolved import, which makes live
directives look inert. So an unresolved import invalidates the result rather
than adding to it. Those trees report several dozen type errors, which are why
the gate excludes them, and the tool passes them without reading them. It
gives `type: ignore` the guarantee that `RUF100` gives for `noqa`, delivered
through the other tool.

`tools/doc_check.py` checks every markdown file in the checkout, not only the
documentation proper, against the math syntax that GitHub renders. It catches
two failures, and both are silent. The first is LaTeX's `\(...\)` and
`\[...\]`. CommonMark strips these to bare parentheses before any math parser
sees them. The second is an expression split across a source line break. It
renders as literal text on both sides, because inline math is parsed within a
single line. The same rule also reports an expression whose opening backtick
has been claimed by a code span that opened before it. That leaves the
expression's tail as literal text (`PL-9TZH`). `docs/MODEL.md` carried 97
cases of the first failure and three of the second, including its whole symbol
table. Before either rule runs, the tool blanks fences, indented code blocks,
code spans and well-formed expressions. So writing *about* the broken syntax
is not the same as writing it. The tool recognises an indented block by
CommonMark's rule. Inside a list item, that means four columns past the item's
content, so an item's own prose indented by four columns is still read. The
tool reads every markdown file, because rendering is not a claim that is
checked against the tree, so it matters in every file. A queue item renders
on GitHub like anything else, and seven queue items had copied the broken form
out of `docs/MODEL.md`.

`doc_check.py` also checks the release-train table in `ROADMAP.md` against a
row grammar. Each step is one of four kinds: a milestone carrying a version, a
patch track, a numbered gate, or an unnumbered marker. The versions, gates and
step numbers must run in order. That table is the project's only statement of
which milestone is current and which is next. So a tool must be able to read
it, not only a person. Otherwise a hyphen typed in place of its em dash would
silently reclassify a release as a marker. The check does not cover what the
rows *mean*, and it cannot. Whether the prose beside a step is still true is
left to the reader.

The grammar itself lives in `subprojects/docket/src/docket/roadmap.py`, and
`doc_check.py` imports it. `docket wave` reads the same table to report which
beat of the planning cadence is due. A second copy of the rules would silently
drift from the first, in the one document that says which milestone is
current.

One thing `doc_check.py` reports rather than checks is the number of lines of
instruction that every session loads before it has read anything. Those lines
are `CLAUDE.md` plus the rule files under `.claude/rules/` that carry no
`paths:` frontmatter. The tool also reports whether that total has grown
against the default branch. Growth is an advisory, never an error. A threshold
would be met by deleting a rule to reach a number. And no number the tool
could hold would know which rules a session must see before it reads
anything. Where each rule belongs is left to the reader, the same way
`docket stranded` leaves its own judgment to the reader.

`doc_check.py` also checks every count that a frozen list states about itself
against the entries in the list. `ROADMAP.md` states a release's list size in
its group headings and in the two table rows that name the release. The same
number once appeared in six places. Admitting four entries on 2026-09-01 meant
correcting nine numbers by hand, and then eight of them again an hour later.
The check deliberately does not read counts written in prose. A checker cannot
tell a claim about today's list from a dated fact about the day the list was
frozen. So the prose states no count, and the number appears only where its
position fixes its meaning. A count can agree with the entries under a heading
while the heading files them under the wrong claim. So the current gate's
"Cleared by vX.Y.Z itself" group is checked against the `Required scope` that
states what a milestone clears by itself. In v0.6.0, two entries that its
scope named had been filed under § "Cleared before" (`PL-J6HP`).

A frozen list can be internally consistent and still be missing entries. So
the check also reads membership, against the queue rather than against the
file. The gate rule makes one class of finding unconditional. An item classed
`safety` or `science`, or one at `P0`, re-enters the *current* gate however
long after the freeze it was noticed. Every other class depends on whether its
problem predates the freeze, which is a judgment. Only the unconditional half
is checked, and only in the direction that can be decided. The check reports
an open item of that class whose id the current milestone's section does not
place, either on its frozen list or under `Required scope`. The check does
not decide what such an item should *become*. So the finding is an advisory,
and it names the three dispositions rather than choosing one. The check
exists because the rule used to run only when a session thought of it. Eleven
qualifying items were filed in the two days after Gate 1 froze, and none of
them reached the list. Meanwhile every count in the file agreed, and
`docket wave` reported the written list correctly the whole time: 84 open of
121, with no `P1` at all, because both classes are pinned to the top band
(`PL-KTKP`).

The same module reads the *version* table in `ROADMAP.md`. `doc_check` checks
the three statements of the current version against each other. There must be
one row per released version, and exactly one row marked as the current
baseline. A "Current baseline:" heading must name that same version, and that
version must match `pyproject.toml`. This exists because a release can bump
the version file and leave the plan naming its predecessor. That happened on
two consecutive releases.

Tags *are* compared, in three directions. A completed release for which git
holds no tag is an error. A release tag that no row of the version table names
is an error. And the roadmap's own count of deliberately untagged versions is
checked against git. A tag that is present is also checked for where it
points. It must be on the commit that added its release's notes, which is that
release's cut. For a release cut before notes were written, it must be on a
tree that declares its version (`PL-YKSD`, `PL-QHCW`). The check will not
speak when it cannot tell a missing tag from an unfetched one, because a check
that fails on how somebody fetched the repository gets switched off. So it
says nothing when the checkout holds no tags at all. It withholds the findings
that a truncated clone could have invented. And it says nothing about the
release being cut right now, whose tag goes on a merge commit that does not
exist yet (`PL-J295`, `PL-R7C0`). That last silence is safe for a reason. The
version stops being the baseline as soon as a newer one lands, and from then
on a missing tag is an error. That is when an untagged release first costs
anything. `docket release` is the other half. It refuses to cut a release
while the previous one is untagged, at a moment when tags are certainly
available.

`check_resident_instructions` measures the resident instruction set: the text
every session loads at launch, before it has read anything. That is
`CLAUDE.md`, the rules under `.claude/rules/` that carry no `paths:`, and what
the session-start digest adds. It prints the total on every run, with each
file's change against the tip of the default branch. It is an advisory and
never a gate. A limit would be met by deleting a rule to reach a number, and no
number could know which rules a session must see first. Two advisories can
follow the total, and both stay quiet while the change is less than
`MATERIAL_RESIDENT_DELTA` characters. The first names growth. The session that
added the text then routes it to the cheapest thing that delivers it when it
is needed (a check, the `docket` skill or a path-scoped rule). Or the session
keeps it and says why a session could break it before it would look anything
up. The second names a change that both grew and shrank the set, because text
cut to pay for an addition never shows as growth in the total.
`CLAUDE.md` § "The queue, and how the
project owner works" states the routing rule, and
`docs/resident-instructions.md` records what each resident block was tested
against.

Every tool here depends on nothing outside the standard library, and parses
under whatever bare `python3` is on PATH. `make check` runs the tools that
parse no repository source directly in that way. CI's floor section runs
`python3 tools/doc_check.py check` before any virtualenv exists. Both have to
work in a checkout with no virtualenv. That is why these tools are held to a
floor, the oldest Python they must run under, of **Python 3.11**. It is not the
version that `pyproject.toml` requires. The floor is not a number chosen here.
`doc_check.py` imports `docket.roadmap` for the release train, and
`docket.config`, `docket.model` and `docket.store` for the queue. So the floor
is whatever `subprojects/docket/pyproject.toml` declares in `requires-python`.

`.claude/hooks/` is held to the same floor for the same reason. Its
`ruff.toml` inherits the pin from `tools/ruff.toml` rather than restating it.
Claude Code also invokes a hook as bare `python3`. So a hook moved out of
`tools/` would otherwise be formatted for the repository's 3.14 target, and
the interpreter that runs it could no longer parse it.
`tests/unit/test_tools_portability.py` covers both directories by path rather
than by filename, so the guard covers the next hook without being extended.

Ten of them are nonetheless *invoked* only under `uv run python`, and three
more are invoked both bare and under it (see below). The distinction is worth
keeping straight, because it is about what a tool reads rather than what it
needs. `ignore_check.py` and `duplicate_code_check.py` are the odd ones out,
each for a reason of its own. The first shells out to mypy and the second runs
pylint, so each needs the virtualenv that its tool runs in.

The other eight share one reason. `import_boundary_check.py`,
`contrast_check.py`, `agent_identity_check.py`, `workflow_paths_check.py`,
`core_vocabulary_check.py`, `glyph_check.py`, `fixture_id_check.py` and
`literal_home_check.py` each parse repository source with `ast`, and that
source targets 3.14. For example, `app_metadata.py` writes
`except OSError, subprocess.SubprocessError:` without parentheses. That form
comes from PEP 758, added in 3.14, so it is a `SyntaxError` to the 3.11
parser. The PEP 695 type parameters in `app/bookmarks.py` are a `SyntaxError`
there too. And the `feature_version` argument of `ast.parse` only narrows the
syntax it accepts. It cannot extend it. A tool that parses repository source
can only run under an interpreter that understands that source. All of them
still meet the promise above: standard library only, and parseable at the
floor. The portability suite enforces that promise, which is why they stay in
its scope while being absent from the CI floor section.

`contrast_check.py` is the reason the group is worth naming, rather than
leaving each tool's own docstring to explain it. It ran bare until `PL-L17Q`.
It was green only because the two files it then read happened to carry no
3.12+ syntax. One PEP 695 generic added to either file would have failed the
floor section on a tool nobody had touched. The module docstring of
`tests/unit/test_tools_portability.py` states the rule that the eight are an
instance of. A tool that joins them belongs on the `uv run python` lines in
both `Makefile` and `.github/workflows/quality.yml`, never in that workflow's
floor section.

`doc_check.py` and `possessive_section_check.py` are the exception, run both
ways. `branch_id_check.py` also runs both ways in `quality.yml`. But it
reads only `git log` and the branch name, so the 3.11 parser has nothing it
cannot read. The comment above its `uv run` step says why (`PL-CP74`). The
other two do parse repository source: they read every module's docstrings for
the citations in them. The floor section runs them bare all the same. There,
each one names the files that the floor parser cannot read on a "Not checked"
line, and passes rather than failing on them. Both gates also run them through
`uv run python`, and that run is the one that checks those files. Until
`PL-MB3F`, the floor skipped those files without a word. `make check` ran both
tools bare, and the possessive check read neither `app/bookmarks.py` nor
`app_metadata.py` in either gate.

`tools/ruff.toml` is what keeps these tools parseable at the floor. The
repository targets 3.14, where PEP 758 makes the parentheses in
`except (OSError, TimeoutError):` redundant. So a `ruff format` that targets
3.14 removes them, and 3.11 can no longer parse the file. The test suite
cannot see that break, because it runs under the project virtualenv, and only
the bare-`python3` invocation fails. `tools/ruff.toml` extends the
repository's rules and overrides only `target-version`.
`tests/unit/test_tools_portability.py` enforces three things. It checks the
file's pinned version against the declared floor. It checks that every file
here parses at the floor. And it checks that every import here comes from the
standard library or the in-tree `docket`. The import check catches the same
failure one step earlier, since a package that resolves only inside the
project virtualenv is a `ModuleNotFoundError` under bare `python3`. A tool
added later inherits all three checks. `subprojects/docket/` carries the same
guards for the same reason.

All of those checks are approximations that run under the project virtualenv.
They use a syntax gate rather than an older parser, and they use the wrong
interpreter's `sys.stdlib_module_names`. The floor section of the
`checks-part-1` job in `.github/workflows/quality.yml` performs the real run
they stand in for. It runs `actions/setup-python` at the declared floor,
then <!-- floor-commands -->
`python3 tools/doc_check.py check`, `python3 tools/possessive_section_check.py`,
`python3 tools/branch_id_check.py`, `python3 tools/rules_paths_check.py`,
`python3 tools/worker_runs.py check`,
`python3 tools/pr_body_check.py --anchors`, `python3 tools/dead_ends.py check`,
`python3 tools/fact_home_check.py`, `python3 tools/config_home_check.py`,
`python3 tools/model_home_check.py` and `bin/docket check` under it. On a pull request, `bin/docket ci-scope` runs
under it first. It decides whether the run takes the item-only fast path
(`PL-DXD4`) or skips the costly tests (`PL-STM6`). <!-- /floor-commands -->
`check_floor_list` in `tools/doc_check.py` checks the commands between those
two markers against the steps that the floor section runs (`PL-5N7T`).
`dead_ends.py` and `bin/docket check` joined the section under `PL-PBP5`. That
item found them enforced by `make check` alone. `check_gate_parity` in
`tools/doc_check.py` now refuses that asymmetry in both directions. So this
list cannot fall behind the Makefile's again without the gate saying so. The
floor section runs ahead of the uv install rather than in a job of its own
(`PL-D551`). That is what keeps the no-virtualenv claim true, because at that
point no virtualenv exists. `contrast_check.py` was in the section too until
`PL-L17Q`, and it is deliberately not there now, for the input-versus-dependency
reason given above. Running at the floor decides syntax, imports and runtime
behavior at once, with no list to keep current. A fourth test checks that
section's pinned version against `requires-python`. So raising the floor cannot
leave CI exercising an interpreter that the project no longer supports. The
approximations stay because they name the offending file and import, they run
before a push, and they cover what those commands never do.

## Wired hooks (`.claude/hooks/`)

`.claude/settings.json` wires twelve scripts as hooks. They live in
`.claude/hooks/`, not in `tools/`, and the reason is a guard rather than
tidiness. `.claude` is a *protected directory* in Claude Code's own list, so a
write to anything under it is never approved automatically. The write prompts
for approval, or in auto mode it goes to the classifier ([protected
paths](https://code.claude.com/docs/en/permission-modes#protected-paths), read
2026-09-05). A `permissions.allow` entry cannot lift that requirement, because
the safety check runs before allow rules are evaluated. So the directory is the
guard, and a hook put anywhere else is silently left outside it.
`stop_hook_patch.py` sat in `tools/` until `PL-W4H9`. That is exactly the gap
the item names: a script that rewrites another hook, editable without review.
`docket-digest.sh`, `docket-branch-guard.sh`, `item_read_log.py`,
`no-prune-guard.sh`, `floor-interpreter-guard.sh`, `gate-status-guard.sh`,
`push-check-guard.sh`, `direct-merge-guard.sh`, `pr-body-email-guard.sh`,
`owner_ask_guard.py` and `webfetch-quote-note.sh` are documented where their
behavior is, in their own headers. `shell_split.py` is the one file in the
directory that nothing wires as a hook. The four Bash guards import it to find
where one shell command ends (`PL-PVW2`). The parsing itself is done by
docket's `subprojects/docket/src/docket/shell.py`, which `shell_split.py` finds
from its own location. It is the one lexer that docket and the guards share
(`PL-JNYL`). Docket also decides which word of a git call is its command.
`no-prune-guard.sh` and `push-check-guard.sh` read
`subprojects/docket/src/docket/gitargv.py`, the same table that `docket.vcs`
reads. Once the push guard has found a push, it reads the default base and
git's results through `docket.vcs` (`PL-ZXCN`). So the code that decides what
the guards refuse lies outside the protected directory, and an edit to it is
approved like any other edit. A pull request that changes this code is armed
to merge on green, as one that changes `.claude/hooks/` is. Both follow the
owner's rule of 2026-10-12 that workflow items need no merge confirmation
(`PL-KPM2`).

Every Python-backed guard refuses through `hook_input.deny`, in
`.claude/hooks/hook_input.py`, which also appends one line to a log on the
machine: the time, the session id, the guard's name and the rule that refused,
never the command (`PL-SG93`). `pr-body-email-guard.sh` refuses through
`tools/pr_body_check.py --screen`, whose `screen` calls `deny` too, and
`tests/unit/test_hook_blocks.py` fails any other Python file that builds a
refusal of its own (`PL-HHKC`). `bin/docket record` runs `tools/hook_blocks.py copy` as
`docket.toml`'s `record_command`, which copies the lines the repository lacks
into `docs/hook-blocks/<branch>.tsv`. `python3 tools/hook_blocks.py count`
prints each guard's refusals from those files, which is what a keep, simplify
or retire verdict on a guard is read from.

`.claude/hooks/stop_hook_patch.py` is the one hook here that is not a check and
does not run under `make check`. It is wired as a SessionStart hook. It edits a
file that this repository does not own: `~/.claude/stop-hook-git-check.sh`. A
cloud container writes that file at start and runs it at every `Stop`. That
Stop hook counts unpushed commits against `origin/<branch>` whenever that ref
*resolves locally*. So after a branch is merged, its surviving tracking ref
makes the Stop hook demand a push. That push would recreate a dead branch
identical to `main`. The corrected check counts the commits that no remote ref
holds instead. The correction is a hook rather than a patch the project owner
applies, because the file is not theirs to change. A container rewrites the
file at every start. User-level settings never apply to a cloud session. An
environment setup script runs before Claude Code launches, and it is skipped
once the environment cache exists. The patch script matches one whole line,
and it rewrites nothing if that line is absent or appears twice. So an
upstream change produces a clean miss that reports itself, rather than a
partial edit to a script that every stop executes. `PL-WW08` carries the
diagnosis and the measurements.

The SessionStart hook does a second thing for the same reason, and the two are
one job. Counting the commits that no remote ref holds only works if this
checkout *has* such refs. The harness provisions the clone by fetching only the
default branch, at depth 50 (`PL-2H0K`). So `remote.origin.fetch` names only
the default branch, and `git push` never writes
`refs/remotes/origin/<branch>`. Every commit on a pushed branch then appears
unpushed, however many times it has been pushed. The hook widens that refspec.
This repairs the clone rather than the test. It also keeps the stop check
offline, instead of trading it for a network call at every `Stop`. The hook
only ever widens the refspec, and it neither fetches nor prunes. So it cannot
destroy a ref that `bin/docket stranded` needs. `PL-3SGR` and `PL-483K` are
the two reproductions.

## Third-party text (`tests/unit/markdown-specs/`)

The CommonMark 0.31.2 specification and cmark-gfm's GitHub Flavored Markdown
0.29 specification are vendored unmodified. Each file is named for the release
tag it was fetched at. They are here because
`tests/unit/test_inline_reference.py` uses their examples as a corpus. The test
checks that the inline Markdown parsing in `tools/doc_check.py` agrees with
markdown-it-py on every example in that corpus. It also checks each file against the SHA-256
of what that tag published (`PL-R417`).
`subprojects/docket/tests/test_markdown_reference.py` checks that
`docket.markdown.emphasis` and `docket.release.code_spans` agree with
markdown-it-py on the same examples (`PL-47NJ`, `PL-T3GW`). Both specifications are
licensed CC-BY-SA 4.0. Each file's front matter states this, with the
licence's address. The licence lets a copy be shared whole, unmodified, with
its notices kept (§ 2(a)(1), § 3(a)(1)). It attaches its ShareAlike condition
only to an adaptation (§ 3(b)), and these copies are not adaptations. So the
repository's Apache-2.0 licence does not apply to them, and their licence does
not apply to the repository
(https://creativecommons.org/licenses/by-sa/4.0/legalcode.en, read
2026-10-10).

