# Apparatus map

This document maps the workflow apparatus: the scripts, hooks and checks that
exist so agent sessions can be productive, rather than the simulator they
build. It is held to `.claude/rules/apparatus-standard.md`, not to the
specialist standard `CLAUDE.md` holds the simulator's documents to. The
simulator's own map - its layering, package map, data flow, and where new code
belongs - is [`docs/ARCHITECTURE.md`](ARCHITECTURE.md), and the queue's
commands and item format are in
[`subprojects/docket/README.md`](../subprojects/docket/README.md).

These three sections were `docs/ARCHITECTURE.md`'s until `PL-KRGY` moved them
here on 2026-10-11, so that the simulator's map stopped carrying the
apparatus's inventory, and the items that work on that inventory stopped
reading as both lanes' work.

## Developer tooling (`tools/`)

Outside the packaged application, and not imported by it:

```text
tools/
├── agent_identity_check.py  # refuses a control that carries the agent colour and can be rendered disabled, because a toolkit then paints its label in its own disabled-content grey, which is declared in no source file and so is unreachable by `contrast_check.py`; a control may be disabled only where the same expression also hides it - `disabled = E` with `visible = not E`, or `setDisabled(E)` with `setHidden(E)` in the Qt spelling since PL-25KS - and one given an agent colour anywhere outside the single writer `RunView._apply_agent_color_scheme` - where it is constructed, or by a `setStyleSheet` or `setItemData` call after - must be written by it; reads every module under `app/` and names none by path, and refuses a tree in which no `disabled` write can be read at all rather than passing over it
├── branch_id_check.py    # refuses a branch ahead of the default base that carries no item id in its name and leads no commit subject with one, because every in-flight guard matches an id and work carrying none is invisible to all of them - an id counting only where the base's or the branch's copy of the store holds it, since the grammar alone passes an English word such as `CTRL` (`PL-SN2T`); scoped to the `claude/*` namespace, since a contributor has no queue to be visible in. It also reads the claim record (`PL-J9S0`): it refuses a `claude/*` branch whose work outside the queue claims nothing, and a claim ordering behind another live claim; `--hint PATH` is the first-edit hook's half of the same question, and `--hint-changed` asks it of every file the checkout has changed, for the hook's run after a Bash call, which names no path (`PL-RXFK`)
├── branch_sweep.py       # archives, then deletes, every `claude/*` branch whose work is finished, because GitHub deletes a head branch only when its own pull request merges and a session cannot delete one at all (`PL-X8SV`); it adds no judgment of its own - a branch stays while a pull request is open from or onto it, `claims.unfinished_work` or a release cut holds it, `vcs.stranded` finds the only copy of an item or an edit to one still open on the base, `vcs.orphaned` or `left_behind_check.py` finds commits a merged pull request left behind, or its last commit is under 72 hours old; one atomic push, leased on the tip it judged, copies that tip to `refs/archive/<branch>/<tip>` and deletes the branch, so a wrong call costs a restore rather than work; any reading that fails pushes nothing and exits 1; `.github/workflows/branch-sweep.yml` runs it daily
├── dead_ends.py          # emits `docs/dead-ends.md`'s entry lines into session context at start, and holds that emitted half - never the file's preamble, which is instructions for adding an entry rather than for reading one - to 30 entries and 4,000 bytes, because a `SessionStart` hook's output is resent on every turn and an unbounded always-loaded store measurably degrades an agent rather than merely costing tokens; refuses an entry citing an id that resolves to nothing, since `bin/docket show <id>` is the entry's whole retrieval path
├── context_reading.py    # reports this session's own context size - `baseline` (its first request: system prompt, resident instructions, session-start digest, any skill the harness preloaded), `context` (its latest request) and the `spend` between them - by reading the transcript the harness appends to as each request happens, `$CLAUDE_CONFIG_DIR/projects/*/$CLAUDE_CODE_SESSION_ID.jsonl` - every such file, since a session whose working directory moved has one under each directory, with the requests put in time order and no spend printed where the first record read does not start the session or the latest request is smaller than the first (`PL-PLT9`) - summing `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` off each assistant record's `message.usage`; deduplicates the several records the harness writes per request, and skips `isSidechain` records because a subagent's context never entered this window. It exists because the instrument `CLAUDE.md` prescribes for the spend budget cannot answer the question it is asked: `get_session`'s `context_usage.used_tokens` is written at turn boundaries, so a session working a whole item inside one turn reads a value that never moves - 0 before its first boundary, measured across all six concurrently running sessions on 2026-09-21 while this read 112,857 from the same transcript. Prints three numbers and judges none of them; the budget is stated against `spend` (project owner, 2026-09-21, ratified, over the absolute reading), and `CLAUDE.md` § "Session and tool-use efficiency" is where that is decided
├── contrast_check.py     # computes every declared color requirement's WCAG 2.2 contrast ratio from the constants in `app/`, and holds each to its declared minimum, taking the better channel where an element's edge can be carried by either its fill or its border; and states in its report line how many control kinds declare no colour at all, which it structurally cannot measure and `tests/integration/test_simulation_view.py` names
├── core_vocabulary_check.py  # holds `core/`'s identifiers to the vocabulary `docs/MODEL.md` establishes, in the three ways that are decidable: every `ClassName.accessor` in the Symbols table's Code column resolves to a real attribute, property or field - an em dash being accepted only where the cell says what the code reads instead; none of the accessor names `PL-9SH6` retired comes back, matched whole rather than as substrings, so that an identifier merely containing a retired name is not accused of reviving it - a rule with no live counterexample in `core/` since `PL-6KNM` renamed `require_concentration_fraction` to `require_fraction`, and `PL-JW9J` is where tightening it is decided; and every `*partition_coefficient` identifier names both of its phases in the declared outward order, gas then blood then tissue, so a coefficient cannot be written as its own reciprocal in a literature that calls one quantity tissue-gas, tissue-blood and blood tissue in a single chapter. It runs under `uv run python`, not at the 3.11 floor, because it parses `core/` with `ast`; whether a name is the one a reader who knows the domain would guess stays a judgment and is deliberately not scripted
├── diff_mutation.py      # runs mutmut on the functions a branch changed in the mutated modules, against every unit test file that imports the simulator, and reports each function's mutants, the diff of each survivor, and the changed lines that mutmut cannot mutate. It reruns each mutant that mutmut calls a timeout, because mutmut reports any exception in its worker as a timeout. `make mutate` runs it, and `make mutate ARGS=--all` mutates the whole tree. `--verdict` prints the run as JSON for `bin/docket verify`, which refuses a branch while a mutant of a line it changed survives (`PL-CZXN`); otherwise it measures, as `PL-Y1PS` records. `docs/mutation-testing.md` has the recipe, the pitfalls and the baselines
├── doc_check.py          # validates this map and `docs/ARCHITECTURE.md`'s, MODEL.md's provenance table and its marked prose values, the data files' declared source tiers, citations - every path and section the documentation cites, the quoted sections in every live `docs/items/` brief and every source docstring, since those two are where this project writes most of them, and a live brief's path citations against the files git history shows the tree once held, since a brief also names files its work will create; a leading `/` is read from the repository root - markdown math syntax, that every sentence naming a host beside a refusal carries the date it was probed, ROADMAP.md's release train, with no "not yet" status written under it, its frozen-list counts and current baseline, the current gate's self-cleared group against its `Required scope`, and the current gate's membership against the queue - unconditionally for the queue's `safety`- and `science`-classed items, and as a recorded disposition, placed or deferred, for every other open debt item; that no milestone names one id under both its `Required scope` and its `Explicitly out of scope`, advising where the words introducing a scope entry's declaration carry exclusion language; that every `Required scope` entry declares its members in a `(queue item ...)` slot where the section's other entries declare, and that the queue holds every id so declared; that every test `MODEL.md` names resolves to one that exists; that every closed release tag's span is covered by notes naming each closing pull request inside it - the release's own cut excepted, being inside its own span by construction and stamped by the next release, and the newest span excepted, whose pointer would have to name a release nobody has cut; reports resident instruction size; and, beside the documentation it holds to the tree, the Makefile's own invocations held to CI's and to each other, such as `make check`'s coverage gate and the `--no-cache` on every `ruff check` recipe line
├── doc_quote_check.py   # reports each quotation of Claude Code's documentation that its page on code.claude.com no longer contains, or that its quoting file no longer contains, read from the record `doc_quotes.toml` beside it, because the pages change over weeks and `PL-124X` found 4 of 16 quoted strings gone; a page it cannot read is reported and fails the run, since an uncompared quotation has not been shown current; it reads the network, so `drift.yml`'s weekly `doc-quotes` job runs it rather than `make check`, and a session runs it by hand before relying on a quotation (`PL-S7LT`)
├── doc_quotes.toml       # the record `doc_quote_check.py` reads: for each quotation, the file that quotes it, the page it quotes and the quoted text
├── effort_trial.py       # the effort trial (`PL-HYRM`): run by the cloud environment's setup script, it draws `xhigh` for about one session in four and `high` otherwise, and from 2026-10-24 04:00 UTC writes the arm as `effortLevel` and `maxEffortLevel` in `.claude/settings.local.json`; its `digest` mode prints the arm in the session-start digest, which is the trial's record of it
├── fact_home_check.py    # refuses a second reader of a fact the apparatus already answers, outside the module that owns it - a `subprocess` call whose argv starts with `git` outside `docket.vcs` and the hooks' `_git`; a recursive walk of the tree outside `docket.vcs.tracked_files`, and `docket.grep`'s model of what `grep -r` reads, which is the disk; the GitHub API's host outside `open_pull_requests.py`; a `main` or `origin/main` literal outside `docket.vcs`; `shlex.split` or `shlex.shlex` outside `docket.shell` and the hooks' `shell_split.py` - an upper-case module-level name defined in two apparatus files, and a membership test of `OPEN_STATUSES` or `CLOSED_STATUSES` or an `isdigit`, `int` or pattern match of the `pr` field outside `docket.model` (`PL-N4FP`), against a baseline keyed by file, rule and scope that fails when it grows and when an entry goes stale, because three generator heads stating this principle closed on enumerated sweeps and re-entered while nothing refused the next copy (`PL-4S6C`)
├── fixture_id_check.py   # refuses a `PL-` literal outside `store.ID_ALPHABET` - Crockford base32 minus the vowels, four characters, or the three digits the historical ids use - because `read_items` takes the `id` field verbatim, so such a literal parses and behaves like any other fixture right up to the moment something applies `ID_PATTERN` to it and matches nothing at all, leaving every assertion resting on it green against a broken implementation (`test_roadmap.py` spent seventeen days that way, and `PL-GXPP` 261 substitutions removing the literal); it reads the grammar with `store.ID_RE` rather than restating it, walks every `*.py` in the repository for string *values* and for keyword-argument names translated `_` to `-` - the second because an id cannot be an identifier, so a helper keyed by one takes `PL_8888_open` and puts the hyphens back, a spelling in which no `PL-` token appears in the source at all and which is how the `doc_check` fixtures were written until `PL-L609`; scoped to `ast.keyword.arg` rather than to identifiers at large, which is the whole of what keeps `PL_PREFIX` out of it, measured 2026-09-21 as 21 of 8,098 keyword arguments carrying an uppercase letter and 17 of those Qt's `ignoreBounds`, `rateLimit` and `userData` - with docstrings dropped so that an id discussed in prose needs nothing, reporting a file's findings in line order across both passes, and line-scans every non-Python file under `.claude/`, a token joined where its format carries one across a line break - a shell script's or a Markdown shell fence's backslash-newline, as bash reads it (`PL-WG6S`), and a TOML multi-line string's line-ending backslash or an escaped line break in a front matter double-quoted scalar (`PL-HKR5`), and `.claude/settings.json` read through `json`, its escapes decoded and a hook's command joined as the shell joins it (`PL-YPLM`) - where the rule is exact without a parser - measured 2026-09-21, every failing token in that tree was a defect, 2 of 2 - while `docs/`, `ROADMAP.md` and the item store stay out because there prose about a malformed id is the norm and `PL-GXPP`'s brief alone names seventeen; a name that is deliberately not an id, a rejection fixture or a `glob("PL-K*.md")` pattern, says so with a `not-an-id` marker on any line it spans. In both halves a token is judged only where it is written the way an id is - `PL-` and one whole word of capitals and digits, the only characters an id holds - so prose naming the prefix, `PL-prefixed`, is not read as one, where the prefix alone once made it a finding (`PL-VH5V`). A second rule refuses a second *spelling* of the grammar rather than a bad literal: a `PL-` followed by a character class closed by a counted quantifier, which is a copy of `store.ID_LENGTH` with a copy of the alphabet in front of it, the prefix matched in either case because a branch-name pattern spells it `pl-` and `vcs.BRANCH_ID_RE` was such a copy the rule could not see (`PL-PB8V`), because five tools wrote their own and every one drifted - all of them admitting the vowels the store cannot mint, and the four written `{4}` blind to the 43 historical three-digit ids, which cost `generator_check.py` 219 citation edges and one wrong printed signal (`PL-KYW3`); the counted quantifier is what makes that rule exact enough to fail the build, since an open-ended `PL-[A-Za-z0-9]+` claims to know nothing about the grammar and is left alone - `CANDIDATE_RE` itself included - and it is scoped to what a module *runs* rather than to prose or to `.claude/`, a regex being read rather than copied, so that no exemption is needed anywhere in the tree as it stands. It runs under `uv run python` for the reason `workflow_paths_check.py` does, parsing `tests/` and `src/` where the source targets 3.14; the rule was `subprojects/docket/tests/test_store.py`'s until `PL-7922`, where it globbed that one directory and so reached neither `tests/unit/` nor the advisory `tools/generator_check.py` prints
├── generator_check.py    # surfaces the `touches` clusters worth a session's judgment about a root cause - three or more open items, plus at least one signal: three of them sharing a `feature`, one of them cited by three or more other open items, or a self-generation ratio of at least 1.0 over the path's closures - and claims none of them is a generator, because a generator is a recorded fact (`root-cause-of:` on the causing item) rather than anything a measurement can decide; the ratio counts only children landing back in the same cluster, since a session closing an item captures whatever else it noticed and those captures attribute to the item it was working, so counting all of them rates any heavily-worked file a generator - `vcs.py` reads 2.33 that way against 0.71 measured properly, and `core/` 5.08 against 0.17; spawn attribution is the commit that adds an item file leading its subject with the id of the item being worked, which is `PL-6ZQY`'s own method; declines the ratio rather than printing 0.00 where a path has no closures; advisory, and exits 0 whatever it finds
├── glyph_check.py        # refuses a non-ASCII character that nobody has confirmed the client can draw, from any string that can reach a reader - every string literal outside a docstring under `app/` and `core/`, and every string in the `data/` JSON - because `→` (U+2192) has no glyph in the Flutter client, drew as a replacement box in the control-change list, and no test in this repository could see it: every string assertion here compares text the same font-less Python process produced; the allowlist is per character rather than per Unicode block, and each entry records what was rendered and looked at
├── headless_worker.py    # runs one `claude -p` worker per delegable item on the owner's machine, on the monthly API credit: a clone and a `claude/<id>-worker` branch per run, the clone removed once everything in it is pushed and kept with its log otherwise (`PL-TX7K`), a per-run dollar cap, a batch that starts from the Console's credit-left figure and stops before a run it cannot cover (`PL-NQ0M`) or after any failed run (`PL-44SP`), a `caffeinate` hold on the Mac's idle sleep (`PL-BT70`), `--no-push` for a trial whose work must stay local (`PL-80R5`), and a record of each pushed run committed to its branch for review (`PL-87BR`)
├── import_boundary_check.py  # fails the build on any import its `BOUNDARIES` table confines elsewhere: `pydantic` anywhere under `src/anesthesia_sim/` other than `core/parameters.py`; `time`, `datetime`, `random`, `secrets` or `uuid` in any module under `core/`; `flet` and `flet_charts` anywhere under `src/anesthesia_sim/`, the port being complete; `PySide6`, `pyqtgraph` or `numpy` in any module under `core/`; and `anesthesia_sim.app` in any module under `core/`, matched against every dotted name an import makes available with relative imports resolved - so the payload/dataclass boundary, the never-wall-clock rule, the toolkit-independence rule and the layering's one direction are measured rather than asserted
├── ignore_check.py       # evaluates warn_unused_ignores over the two test trees `[tool.mypy] files` excludes, so an inert `type: ignore` fails the build
├── item_reads.py         # reports, from the local untracked `.docket-reads.log` that `.claude/hooks/item_read_log.py` writes, how many distinct items sessions actually open, what share of those are closed, and how many citation edges are traversed within a session - the read-side measurements every argument about the store's shape had been assuming; states the sample size first and chooses between none of the readings a low count admits
├── left_behind_check.py  # names the commits a branch carries past the head its newest merged pull request merged, because nothing merges a merged pull request a second time and a push made after the merge lands nowhere with no conflict, red check or advisory (`#284`); exact rather than a content comparison - the tip is compared by ancestry against the frozen `refs/pull/<n>/head`, read with one `ls-remote`, so a squash, a base that rewrote the file afterwards and identical lines from two sessions cannot confound it the way they have confounded `vcs.orphaned`, which stays beside it as the half that answers offline (`PL-VV4D`, `PL-BHVM`); the one case ancestry cannot see, a commit past the head whose change reached the base through another pull request, it puts to `vcs.change_landed`, the three-way replay `vcs.orphaned` reads too, and reports as landed there, naming the pull request (`PL-GHHW`, `PL-PXZ3`); git records no link from a branch to its pull request, so that mapping is GitHub's pull-request listing and needs a token; it declines, under its own prefix, on no network, no permission and a `refs/pull/<n>/head` GitHub has deleted (`PL-LF2C`), and never reads a missing answer as clear, because in the session-start digest that calls it silence is the all-clear; where it and `vcs.orphaned` disagree it prints the disagreement and wins
├── literal_home_check.py  # refuses a bare numeric literal anywhere under `src/anesthesia_sim/` outside the value of a module-level assignment - 0, 1 and 2 exempt, and never a `bool` - and a numeric constant defined in more than one module, so a number has one named home and a second copy cannot drift from the first; its `BASELINE` holds the literals the tree carried when it landed, keyed by file, scope and value rather than line, and may only shrink, and a finding names any constant of the same value without deciding that it is the same quantity (`PL-40SJ`)
├── main_ci_status.py     # reports the default branch's last quality verdict, and nothing at all when it was a success, because the whole-store `verify:` replay runs only on push to `main` and its failures therefore land on a run no pull request shows; a run newer than that verdict that was cancelled, or concluded `action_required`, gets a line of its own whatever the verdict, since its commit has no whole-store verdict and the one reported is an older commit's (`PL-JTHW`); its `FAILED` set is the one `update_armed.py` reads a check run's conclusion by (`PL-351H`); on a failure it makes a second request for the run's jobs and names the step that failed, because 93 of the 109 failures on record are the whole-store replay alone and a line naming no step cannot separate those from a broken tree (`PL-T83R`); it also prints a line when the median time of CI's pytest step over `main`'s five newest successful runs leaves the band of 0.5 to 1.3 times `PYTEST_BASELINE_S`, and says in that line when it could not read the time, so that its silence means the time was read and in the band (`PL-YY32`); it also prints a line naming each `drift.yml` job whose newest result on `main` is not a pass, judged by the job and not by its run, since that workflow reports and never gates and a red run nobody read went unmentioned for 17 days (`PL-JTWV`); the session-start hook calls it, it gates nothing, and it is not the only tool here that reads the network - `required_checks_check.py` does too and gates, and `pr_body_check.py` does in its `--record`, `--recover` and `--compare` modes
├── new_prose.py         # prints each docstring and comment of 30 words or more that a branch added or changed in `src/` or in a file under `tests/` that imports the simulator, with its rows and the code around it, so that the close-out's fresh reviewer reads no file. `.claude/skills/docket/modes/close-out.md` step 8 runs it, and `PL-PRCS` records why
├── open_pull_requests.py  # prints the branch name and number of every open pull request, one per line, so `bin/docket flight` can tell a branch waiting on review from one nobody opened - the half of "is anybody still on this branch" that git cannot answer, and the half that left `claude/hopeful-allen-tetrje` reported as live work for three hours with every item on it closed - and can say on every row which pull request is open, since a branch outlives its session and an age alone cannot say so in the first hour (`PL-7TVT`); the contract is the exit status, zero meaning it looked and non-zero with an empty stdout meaning it could not, because "could not look" read as "nothing is open" would announce that finished work has stalled on every branch under review; it lives here rather than in `subprojects/docket/` for the reason `main_ci_status.py` does - that package answers from a bare checkout with no network and knows nothing about GitHub - and `docket.toml`'s `open_pull_requests_command` is what points `flight` at it; `pr_title_check.py` shares the request rather than making its own, so the token, the timeout and the every-failure-is-a-skip rule have one spelling; `--newest BRANCH BASE` prints `NUMBER STATE HEAD` for the newest pull request from one branch, which `bin/docket branch` and `bin/docket arm` read through `newest_pull_request_command` as the merge evidence a squash leaves no commit of, so a branch whose pull request merged is told to restart rather than to merge the base in (`PL-8BR0`); `--auto-merge NUMBER` prints `on TIME` or `off TIME` for the latest switch of a pull request's auto-merge, which `bin/docket arm` reads through `auto_merge_command` so that a switch off no session recorded as its own holds the pull request (`PL-8TPV`); `left_behind_check.py` reads that newest pull request through `newest` and `update_armed.py` the open listing through `every_page`, which reads to a short page and declines where a page moved under the read, so the tools cannot disagree about either (`PL-351H`)
├── possessive_section_check.py  # reports a possessive citation whose quotation matches a heading in the file it names, and prints the `§` line it should become, because admitting the possessive to `CITATION_CONNECTIVE` (`PL-316G`) settled whether such a citation is *checked* and left what it tells a reader: `§` says the quotation is a section title and the possessive says nothing, this project writing it to quote a sentence as often as to cite a section. Only the direction that is a fact about the tree is reported - a quotation matching a heading is a section citation - while one matching no heading may be a faithful quotation of prose and is left alone, which is the judgment half `CLAUDE.md` refuses to script. A `**Bold.**` marker is in that half, being often a lead sentence as well as a title, so either form quotes one correctly (`PL-FKH6`). Closed briefs never reach it, `_quoting_sources` having exempted them since `PL-ZM8P`
├── pr_body_check.py      # reports a squash commit on `main` that landed with no body and no file under `docs/pr-bodies/`, because the squash commit's body is the record of a pull request's body and a merge client can still send an empty one (`PL-843V`; `PL-3PH2` retired the per-pull-request copy `PL-979D` kept in the tree); the default mode, run by hand at each release, prints a verdict either way, and `--recover` fetches each lost body from the public API into `docs/pr-bodies/<N>.md` under a header dating the fetch; `--anchors`, in `make check`, refuses a recovered file whose `commit:` is not a first-parent commit of the default branch, and says it checked nothing on a shallow clone; `--compare` is a hand-run measurement of how far squash bodies drift from their pull requests, a drift accepted rather than repaired; `--screen` reads a pull request call from stdin and refuses a title or body holding an email address other than `noreply@anthropic.com`, run before the call by `.claude/hooks/pr-body-email-guard.sh` because GitHub publishes a body at once (`PL-7K31`)
├── pr_record_check.py    # refuses a pull request until every item its branch closes records `pr:` equal to the pull request's own number, which the `pull_request` event is the one point in the workflow that knows (`PL-HMZZ`); the number is written on the closing branch by `bin/docket record N` before the merge, so which pull request closed an item is a recorded fact rather than one inferred afterwards from squash subjects and item-file history - the inference that ten items in three weeks were the shapes of history that misled, retired with the count that 1,143 of 1,143 done items carried the field once the last 43 were written by it; a sibling of `pr_title_check.py` that reads the same two trees through its helpers, runs as a step of the same required job, and under `--discover` lets `make check` ask the branch's own open pull request, skipping silently on every way that lookup can fail
├── pr_title_check.py     # refuses a pull request whose title does not lead with the ids its branch closes, because the squash-merge subject is taken from that title and is the one line of `main`'s history that says which items a change was about; it no longer stands for provenance, which `pr_record_check.py` beside it records before the merge (`PL-M7W1`, `PL-HMZZ`)
├── required_checks_check.py  # reconciles the jobs that report a status check on `pull_request`, parsed from `.github/workflows/`, against the status checks branch protection requires, read from the GitHub API - in both directions, because a required name nothing reports leaves every pull request pending forever on a check that cannot arrive (`PL-KPP1`, `#377`) and a reporting job nothing requires can go red without blocking a merge (`PL-H8YD`, `#654`); it needs no credential at all, since on a public repository `GET /repos/{owner}/{repo}/branches/{branch}` answers unauthenticated where the `.../protection` endpoint the question was first asked of needs an `administration` grant a workflow token can never hold; it reads both settings surfaces, classic branch protection and rulesets, and treats an empty union as a failure rather than as agreement, because a migration between them would otherwise leave it passing while requiring nothing; and it refuses rather than guesses a matrix job, a reusable workflow call or an unreachable API, a job silently dropped from the reporting set being indistinguishable from nothing to reconcile. It runs as a step inside `quality.yml`'s `checks-part-1` job rather than as a job of its own, so the check that guards the required list adds no entry to it; that job and `checks-part-2` report on a pull request without being required, each declaring `# not-required:` because the required `checks` job needs both and fails unless both succeeded (`PL-T9X9`), and it is one of several tools here that read the network, `main_ci_status.py`, `open_pull_requests.py`, `left_behind_check.py` and `pr_body_check.py`'s `--record`, `--recover` and `--compare` modes among them
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

`tools/doc_check.py` holds this document to the code. The package-map tree
above, and `docs/ARCHITECTURE.md`'s of `src/anesthesia_sim/`, are each checked
against the tree on disk in both directions, so a module added without a line
in its map, or a line left behind after a deletion, fails `make check`, and a
document whose map is gone fails rather than passing on the other's. That is
why the trees list every module individually: a
directory drawn with no children beneath it stands for its whole subtree and
is not expanded, and `__init__.py` is excluded throughout. Neither live tree
draws such a directory, so `tests/unit/test_doc_check.py` holds the rule in
both directions:
`test_childless_directory_covers_its_whole_subtree` and
`test_a_childless_directory_covers_nothing_outside_its_own_subtree`. The same tool checks `docs/MODEL.md`'s provenance table against
the data files and resolves every path and section heading the documentation
cites.

Its `check_source_tiers` holds the same data files to `docs/MODEL.md`
§ "Source hierarchy". Every `sources` entry declares a `tier` from the closed
vocabulary, an `adopted` flag, and an `authority_for` list that is non-empty
exactly when the entry is adopted and names only the file's own stored values,
none of them twice. A file with no entry that is both `primary` and `adopted`
records a `provenance_gap`. It decides only what a
file *declares*. Whether a citation labelled `primary` really is a primary
measurement of the quantity needs somebody who has read the paper, and a tool
guessing at that — by author, by journal, by a denylist on a product name —
would be authoritative and wrong. That is the same split the provenance table
check already runs on: it decides that a documented key exists and holds the
stated value, never that the value is right.

`tools/pr_title_check.py` and `tools/pr_record_check.py` are the two halves of
`PL-2XTF`'s lesson, re-divided by `PL-HMZZ`. A squash merge takes its subject
from the pull request title, so a title naming none of the items it closes
lands a subject that says nothing about them: that happened once, on a
UI-generated title that closed three items, and the title check stops it while
the title can still be edited. What the title does not carry is provenance.
Which pull request closed an item used to be recovered from that subject and
then from the item file's own history, and every new shape of history misled
the recovery until it got an exception of its own; the number is now written
onto the closure by the branch that closes it, and the record check refuses
the pull request until every closure carries it, at the one point in the
workflow that knows its own number.

It runs in `.github/workflows/pr-title.yml`, which takes the title from
`PR_TITLE`, and in `make check` and `make pr-title`, which pass `--discover`
and read it from the branch's own open pull request instead (`PL-J3BB`). It
was CI-only until then, which made it the one gate a session could not run
before pushing: the check compares the title against *what the branch closes*,
and a branch closes more items as it goes, so a correct title goes stale the
moment the next item closes on it. Every way the lookup can fail — no token, no
network, no pull request open yet — is a silent skip, so `make check` stays
green offline.

`tools/branch_id_check.py` is the same shape of guard aimed at the other end of
the same problem, and the two do not overlap: the title check asks whether a
pull request names the items it *closes*, and answers "no id is owed" for a
branch that closes none — which is exactly the unfiled repository housekeeping
`PL-CP74` found colliding. `docket flight`, `show`, `next`, `concurrent` and
the session-start digest all answer "is anybody already on this?" by matching a
`PL-` id in a branch name or at the front of a commit subject, so a branch
carrying none reads as nobody's work to every one of them, and goes on doing so
after both sessions have pushed.

That argument is about agent sessions, so the check binds only their branch
namespace — `claude/*` — and passes anything outside it. A contributor has no
queue and no id, and requiring one refused `#394`, the project owner's own
web-UI edit to the README, in the required job (`PL-8P6D`).
[`CONTRIBUTING.md`](../CONTRIBUTING.md) is the route that leaves open.

It imports `BRANCH_ID_RE` and `leading_ids` from `docket.vcs` rather than
matching ids its own way, because a check looser than the guard it protects
would certify a branch as visible that `docket flight` still cannot see — the
gate green while the guarantee is void. One commit carrying an id is enough,
which is what keeps the tool out of the judgment it must not make: how small a
piece of work is too small to file is decided in `.claude/skills/docket/modes/capture.md`
under "Mode: housekeeping nobody filed", and a fix riding inside a commit an id
already leads needs no item of its own. A release commit is exempt, exactly:
`make release` writes that subject, and it closes no item.

`tools/contrast_check.py` holds the interface to the accessibility target
`docs/MODEL.md` states — WCAG 2.2 Level AA. It reads the color constants with `ast`
rather than importing them, because the interface imports PySide6 and a
bare checkout or a hook has no PySide6 to import. It reads them from every module
under `app/` — the theme first, then the rest in path order — rather than from
two named paths (`PL-BXB2`). Since `PL-2CS8` every color is declared
in `app/theme.py`, and `check_colors_live_in_the_theme` fails the build on one
declared anywhere else, as a named constant or as a hex color written inline,
in a call or inside a longer string such as a stylesheet (`PL-PXT7`); every
module is still parsed for colors as well, so a
color put back outside the theme is measured rather than lost, which is the failure that
item was filed for. Its `REQUIREMENTS` table is the specification: each entry names
the colors that appear on screen together, the success criterion, the minimum,
and the reason, which cites the code they are drawn in by symbol. Most entries
are one foreground against one background; an element whose edge either of two
channels can carry — the agent badges, each a fill with a border in the agent's
own text color — declares both and is held to the better, because measuring
such an element one channel at a time reports a false shortfall whichever
channel is picked (`PL-GNN1`). The tool
evaluates that table and decides nothing else — which colors matter, which
channels an element really has, and whether
a non-color channel is genuinely redundant, are judgments, and
`.claude/rules/ui-color.md` carries them. The one thing it does decide about
the prose is the half a script can: a description may cite no line number, and
every symbol it names must exist in some module under `app/`. Those citations
were line numbers until `PL-GJDW`, and all fourteen had rotted into unrelated
code, which made the tool's own coverage unauditable while looking audited. Requirements that fall short
today are listed against the item that closes each, and a listed shortfall that
starts passing is an error, so a fix cannot leave its excuse behind.

It measures one thing beyond the `REQUIREMENTS` table, and that one is a hard
error rather than a listable shortfall. `TRACE_FLOOR` holds each of the six
chart traces to 3:1 against the panel under **four** vision models — as
displayed, and simulated for protanopia, deuteranopia and tritanopia by the
Brettel 1997 projection in `DICHROMACY_TRANSFORMS`. The fourth model is the
project's own bar rather than the criterion's, since SC 1.4.11 is defined on
the color a display emits; the reason it is worth the extra arithmetic is that
`MUSCLE_COLOR` measured 3.19:1 on screen and 2.98:1 for a deuteranope, which no
normal-vision check could see (`PL-GVXP`). `--matrix` prints the pairwise
separation across all four, which is the evidence that these six traces cannot
be separated by color at all and that the line style is doing the work;
`docs/MODEL.md` § "The six compartment traces" carries the tables and the
limits on how far a simulated ratio may be read.

`tools/agent_identity_check.py` closes the one gap that table structurally
cannot cover: a colour the project never declares. Flet/Material painted a
disabled control's label in the theme's disabled-content grey, and a Qt style
does the same from its palette's disabled role; neither appears in any module
`contrast_check.py` reads, so a requirement went on measuring
the enabled pair and reporting a pass while the agent's name sat grey on its
own ISO 5360 fill for the whole of every run (`PL-61WW`). The rule it enforces
is the project owner's, 2026-09-08: no control carrying agent identity may be
*rendered* disabled, so SC 1.4.3's exemption for an inactive component — which
settles a conformance claim, not whether a reader can identify the running
agent — is never claimed here. Rendered is the load-bearing word: a control may
be `disabled` where it is also `visible = not <the same expression>` — or,
in the Qt spelling the check reads since `PL-25KS`, `setDisabled(E)` where it
is also `setHidden(E)` — since it then draws nothing. The identity set is not
a second list to keep in step but
whatever `RunView._apply_agent_color_scheme` writes, that method already
being the single writer of agent colour; a control given an agent colour
anywhere outside that method — where it is constructed, in the Flet spelling,
or by a `setStyleSheet` or `setItemData` call after it, in Qt's — and never
written there is the check's other error, and is what keeps that coverage
claim true rather than asserted. It reads every
module under `app/` and names none by path (`PL-V53R`): the writer is found in
whichever module holds it, exactly once — none is an error, two is a second
writer of agent colour — rule 1 reads the pairing inside the writer's own
class, since `self.X` names that class's attribute, and rule 2 reads every
method of every class in every module except the writer, since the writer can
only write its own and its body is the set itself. A tree in
which no `disabled` write can be read at all is an error rather than a pass
(`PL-0PJG`), and the success line states how many such writes were read,
across how many modules and how many on identity controls, and how many
colourings rule 2 read in each spelling, so the sentence
cannot be printed from nothing. Like the two tools
above it decides nothing else — whether a control's identity is legible, and
whether a pairing is the right one for it, stay judgments.

**What a Qt port costs these two, measured rather than estimated (`PL-JRS3`).**
The dependency is split, and not the way the question assumed: one reads
*values* and survives, the other reads Flet's *control objects* and goes
silent. Measured 2026-09-14 by rewriting `app/theme.py` and
`app/simulation_view.py` on the AST — every Flet property assignment replaced
by the PySide6 setter call that supplants it — and running both against the
result.

`contrast_check.py` survives. Its colour input is module-level
`NAME = "#RRGGBB"` constants, which no toolkit owns, and every way of removing
a declared one is loud: renaming `FAT_COLOR` failed with the constant named,
and moving `SimulationView` to its own module — which `PL-B9PY` records the
port doing from the start — failed with 68 unresolved citations, from the
symbol rule `PL-J7C5` added for an unrelated reason. Its one hole was
**additive**, and `PL-BXB2` closed it before the port could open it: a colour
declared in a module that was neither of the two then read was measured by
nothing and missed by nothing, and a new chart-panel module holding a selection
colour at 1.07:1 on the panel passed with `0 errors`. The tool now reads every
module under `app/`, so that colour is measured and refused, an inline hex
literal outside the theme is refused with it, the moved-class probe resolves
its citations instead of failing, and the report's first line says how many
modules it read.

`agent_identity_check.py` did not survive, and its failure was worse than
silence. Rule 1 reads `self.X.disabled = EXPR` paired with
`self.X.visible = not EXPR`; PySide6 spells both as calls, so `property_writes`
returned nothing and the pairing loop ran zero times. On a tree where all six
identity controls are driven by `setEnabled()` with no paired hide it printed
"6 control(s) carry the agent colour, none of them rendered disabled" and
exited 0 — an affirmative claim about a tree it had not measured, which a
reader could not tell from the same sentence earned. `PL-0PJG` closed that
door ahead of the port: a tree in which no `disabled` write is read in any
class of any module is an error naming the spelling the check does not read,
so that probe fails on the first port commit rather than passing through it,
and the success line carries the count it rests on. Whether the older tool
went quiet turned on a choice the port makes incidentally: porting the colour
writes as well trips rule 2 and moving the class trips the empty-set guard, so
both of those are loud, but rule 2 then misdiagnoses, reporting that the
writer "never writes" controls it writes through `setStyleSheet`.

So the port's cost side gains one entry rather than two, and it is specific:
rule 1 of `agent_identity_check.py` is inside the port's scope — teaching it
the setter spelling, which the empty-measurement error now demands of the
first commit that changes it. Both tools' widening to every module under
`app/` landed ahead of the port (`PL-BXB2`, `PL-V53R`), so the decomposition
itself costs neither of them anything. `PL-25KS` paid that one entry: rule 1
reads `setDisabled`/`setEnabled` paired with `setHidden`/`setVisible` as well
as the property spelling, and the identity set counts every method the single
writer calls on a control, `setStyleSheet` included.

`tools/glyph_check.py` covers the half of presentation correctness that no
string assertion here can reach. Every such assertion compares text the same
font-less Python process produced, so the suite is blind to whether the client
can *draw* what it is given: `→` (U+2192) has no glyph in the Flutter client
and drew as a replacement box in the control-change list on 2026-09-04, in the
arrow of `5.60% -> 0.95%` — the direction of a setting change, which is the one
thing that line exists to state (`PL-8XPQ`). The rule is default-deny: every
non-ASCII character in a string that can reach a reader must appear in
`CONFIRMED`, whose entries each record what somebody rendered and saw. Per
character rather than per Unicode block, because Latin-1 Supplement admits `¤`,
`þ` and `ð` beside the `·`, `±` and `×` this interface has actually shown — a
block set would admit thousands on the evidence of three. It reads three trees,
not the one the item first named: `app/` draws the strings, `core/` raises the
text the view prints verbatim — `_apply_setting` renders `f"Setting refused —
{error}"` from a `SimulationConfigurationError` — and `data/` holds
`display_name`, which reaches the readouts and is the one place an edit lands
without touching Python. Documentation is exempt by a structural test, a string
that is a bare expression statement, which is what keeps `§` out of a list
meant to record what was rendered. Like the tools above it decides nothing
else: whether an unlisted character *would* render needs a real client, so it
refuses and never approves.

`tools/import_boundary_check.py` measures four claims the source makes about
itself. `_StrictPayload`'s docstring says that the `_...Payload`/public-
dataclass pairs exist so the rest of `core/` never imports Pydantic;
`docs/MODEL.md` "The reproducibility guarantee" says that a run is a function of
its inputs and of the number of steps taken and of nothing else — so the run
loop reads no clock; and `docs/ARCHITECTURE.md` § "Layering" keeps simulation
code independent of the UI toolkit (a `CLAUDE.md` bullet until `PL-ZYHX`
retired it to this tool on 2026-10-17), which `ROADMAP.md` § "Completed: v0.4.26 - the
interface moves to Qt" turned into a figure — exactly three modules imported
Flet — and reasoned from while the port ran; and `docs/ARCHITECTURE.md`
§ "Layering" says the
layers are enforced by import direction, which no boundary measured for `core/`
reaching into `app/` until one could name a module inside this package rather
than a root package, to which both layers are `anesthesia_sim` (`PL-YXFF`).
Nothing checked any of them, so a
leak into a compartment
would have left the paragraphs reading as verified while being false — worse than the
coupling itself; the Flet count was true and unenforced until `PL-9KDK`, and
`PySide6`, `pyqtgraph` and `numpy` are held out of `core/` from before the
first import of any of them exists, so the port's first commit is measured
rather than the rule written after it. Its `BOUNDARIES` table is the specification, and the tool
decides nothing beyond it: which packages ought to be confined, and where the
exception belongs, are judgments written there with the reason beside them.
Three further states are errors, each closing a way the check could pass while
meaning nothing — an allowance naming a file that no longer exists, an allowance
no longer used, and a declared tree matching no source files at all.

The boundaries cover different trees, and the asymmetry is deliberate. The
Pydantic boundary covers `app/` as well as `core/`, so the rule reads *exactly
one module in this package imports Pydantic*. The `time`, `datetime`,
`random`, `secrets` and `uuid` boundaries stop at `core/` and permit no module
at all, because the
guarantee they defend explicitly allows the interface its wall clock — what it
forbids is a tick's real duration reaching the run. A test pins that asymmetry
end-to-end, so widening the tree to the whole package would fail on an import
the design permits rather than passing quietly (`PL-J833`). The toolkit
boundaries follow the clock's shape — `app/` is where a widget belongs — except
Flet's two root packages, `flet` and `flet_charts`, which cover the whole
package and permit no module at all: the port is complete (`PL-25KS`) and
nothing under `src/` may import Flet again (`PL-7SVX`). While the port ran
they named the three modules the roadmap counted — two boundaries because the
Flet chart module imported `flet_charts` without `flet`, so one boundary on
`flet` alone counted two — and were its checklist through the tool's own
unused-entry error: each module the port freed of either package dropped its
entry in the same commit, and the last took the allowances with it.

`tools/main_ci_status.py` gates nothing, and it is not
the only one that reads the network: `required_checks_check.py` does too and
gates, and `pr_body_check.py`'s `--recover` and `--compare` modes do. (This said it was the only
one until `PL-T83R`'s docs sweep; the tree comment above it had named
`required_checks_check.py` alongside it since that tool landed. No count is
asserted here deliberately - the last two attempts at one both went stale.) `.github/workflows/quality.yml` runs the whole-store
`verify:` replay only on push to `main` — `PL-SDHR`'s decision, because a pull
request cannot have changed whether some *other* item's work merged, and
replaying the store on every branch costs more than it buys. A pull request
*can* stop another item's command discriminating, by editing a file that
command reads, so the scoped replay covers those items too and the sweep is
what is left over rather than what catches them (`PL-XMNC`). The consequence is
that when that replay fails it fails on a run no pull request shows, and `main`
was red across three consecutive merges with every session believing the tree
was clean (`PL-0ZGK`). So the loop is closed from the reading end rather than by
making every branch pay to prevent it: `.claude/hooks/docket-digest.sh` calls
this at session start, and it prints one line when `main`'s last verdict was not
a success, and one when a run newer than that verdict was cancelled (`PL-JTHW`).
It also prints one when CI's pytest step time has drifted from its recorded
baseline, or could not be read (`PL-YY32`). And it prints one naming each
`drift.yml` job whose newest result on `main` is not a pass, or saying that
those runs could not be read (`PL-JTWV`).

`tools/context_reading.py` is the other one that gates nothing, and for a
different reason. `main_ci_status.py` reports on the repository, so it *could*
have been a check and is deliberately not one; `context_reading.py` reports on
the session running it, which is not a property of the tree and so is not
something `make check` could ever have an opinion about. Wiring it in would fire
it on every commit to say something true of no commit, which is the shape
`CLAUDE.md` retires rather than builds. It is run when a session is deciding
whether to start an item, which is the only moment its answer changes anything.

**The line names the step that failed, which is what makes it actionable.** All
819 completed `main` push runs of `quality.yml` from 2026-08-22 to 2026-09-20
were attributed by failing step (`PL-T83R`): 93 of the 109 failures are the
whole-store replay, 14 the bare `bin/docket check`, one a pytest failure
asserting on `ROADMAP.md` and one a startup failure - **not one of them a defect
in `src/`**. In all 93 the bare `bin/docket check` step passed earlier in the
same job on the same tree, which isolates the cause to the one report `--verify`
adds: an open item whose own `verify:` command has flipped to passing. So where
the replay is the *only* failing step the line says the red is the queue rather
than the tree and hands over `bin/docket check --verify`; where anything else
failed it names the steps and interprets nothing, because the bare check passing
first is the whole of what makes that reading sound.

The failure *rate* was left alone in the same pass, and the reasoning is worth
keeping: over the narrower window `PL-T83R` was filed on - 2026-09-05 to
2026-09-16, holding 74 of those 109 failures - 32.7% of pushes reaching a
verdict failed, which reads like a check nobody could act on. But the 74
failures behind it are 8 episodes - merges keep arriving while `main` is red, so
the per-push rate counts one outage once per merge. Two episodes hold 87% of the
red time and each ended in one cheap commit. Suppressing the class would have
cost 93 findings, every one of them real.

Two properties are what make it safe to run unconditionally, and both are held
by tests. **It is silent unless there is something to act on** — a green `main`,
no network, a non-GitHub remote and a malformed response all print nothing and
exit 0, because a line that appears every session trains a reader to skim the
region a real advisory occupies. And **a `cancelled` run is not a verdict**: the
tool reports the newest run that actually reached a conclusion. That skip was
load-bearing until `PL-SMN4` — every push to `main` shared one concurrency
group, so a merge arriving while an earlier one was still pending evicted it,
and 31 of the 257 completed `main` push runs across the eleven days that block
stood ended `cancelled` having started no job at all. `quality.yml` now gives
each `main` push a group of its own, which ends the eviction; what reaches this
tool as `cancelled` is a hand cancellation or a lost runner, and the commit
behind one still has no whole-store verdict that anything reports
(`PL-JTHW`). It is unauthenticated — the repository is public,
so no token is read and none is needed, which keeps a credential off a
session-start path. The GitHub read deliberately does not live in `docket`,
whose rule is that a read must work from a bare offline tree.

`tools/ignore_check.py` covers what the type-check gate cannot. `[tool.mypy]
files` names `src`, `tools`, `.claude/hooks` and `subprojects/docket/src`, and every
`type: ignore` in the repository sits outside that set, so `strict = true`'s
`warn_unused_ignores` never read one. It runs mypy over `tests/` and
`subprojects/docket/tests/` separately and takes two things from the output: an
inert directive, and an unresolved import — which makes live directives look
inert, so it invalidates the answer rather than adding to it. The several dozen
type errors those trees report, which are why the gate excludes them, pass
unread. It is the guarantee `RUF100` gives for `noqa`, arriving through the
other tool.

It holds every markdown file in the checkout — not only the documentation
proper — to the math syntax GitHub renders. Two failures, both silent:
LaTeX's `\(...\)` and `\[...\]`, which CommonMark strips to bare
parentheses before any math parser sees them, and an expression split across a
source line break, which renders as literal text on both sides because inline
math is parsed within a line; the same rule reports one whose opening backtick
a code span opened before it has claimed, which leaves its tail as literal text
(`PL-9TZH`). `docs/MODEL.md` carried 97 of the first and
three of the second, its whole symbol table among them. Fences, indented code
blocks, code spans and well-formed expressions are blanked before either rule
runs, so writing *about* the broken syntax is not writing it; an indented block
is recognised by CommonMark's rule, four columns past a list item's content
where it sits in one, so an item's own prose indented four is still read. Every markdown file is read
because rendering is not a claim held to the tree: a queue item renders on
GitHub like anything else, and seven of them had copied the broken form out of
`docs/MODEL.md`.

It also holds `ROADMAP.md`'s release-train table to a row grammar: each step
is a milestone carrying a version, a patch track, a numbered gate, or an
unnumbered marker, and the versions, gates and step numbers must run in order.
That table is the project's only statement of which milestone is current and
which is next, so it has to be readable by a tool rather than only by a
person — a hyphen typed for its em dash would otherwise reclassify a release
as a marker, silently. What the rows *mean* is not checked and is not
checkable: whether the prose beside a step is still true stays with the
reader.

The grammar itself lives in `subprojects/docket/src/docket/roadmap.py` and is
imported here. `docket wave` reads the same table to report which beat of the
planning cadence is due, and a second copy of the rules would drift from the
first silently — in the one document that says which milestone is current.

One thing it reports rather than checks: how many lines of instruction every
session loads before it has read anything — `CLAUDE.md` plus the rule files
under `.claude/rules/` carrying no `paths:` frontmatter — and whether that
total has grown against the default branch. Growth is an advisory, never an
error. A threshold would be met by deleting a rule to reach a number, and no
number the tool could hold would know which rules a session must see before it
reads anything; where each rule belongs stays with the reader, the way
`docket stranded` leaves its own judgment.

It also holds every count a frozen list states about itself to the entries in
it. `ROADMAP.md` states a release's list size in its group headings and in the
two table rows naming the release, and the same number reached six places
once; admitting four entries on 2026-09-01 meant correcting nine numbers by
hand, then eight of them again an hour later. Counts written in prose are
deliberately not read, because a checker cannot tell a claim about today's
list from a dated fact about the day it was frozen — so the prose states no
count, and the number lives only where its meaning is fixed by where it sits.
A count can agree with the entries under a heading while the heading files
them under the wrong claim, so the current gate's "Cleared by vX.Y.Z itself"
group is held to the `Required scope` that states what a milestone clears
itself: v0.6.0's filed two entries under § "Cleared before" that its scope named
(`PL-J6HP`).

A frozen list can be internally consistent and still be missing entries, so
membership is read too, against the queue rather than against the file. The
gate rule makes one class of finding unconditional: an item classed `safety`
or `science`, or one at `P0`, re-enters the *current* gate however long after
the freeze it was noticed. Every other class turns on whether its problem
predates the freeze, which is a judgment. Only the unconditional half is
checked, and only in the direction that is decidable — an open item of that
class whose id the current milestone's section does not place, either on its
frozen list or under `Required scope`. What such an item should *become* is
left alone, so this reports as an advisory and names the three dispositions
rather than choosing one. It exists because the rule ran only when a session
thought of it: eleven qualifying items were filed in the two days after Gate
1 froze and none reached the list, while every count in the file agreed and
`docket wave` reported the written list correctly the whole time — 84 open of
121, holding no `P1` at all, since both classes are pinned to the top band
(`PL-KTKP`).

The same module reads `ROADMAP.md`'s *version* table, and `doc_check` holds
the three statements of the current version to each other: one row per
released version, exactly one marked the current baseline, a "Current
baseline:" heading naming that same version, and that version matching
`pyproject.toml`. A release bumps the version file and leaves the plan naming
its predecessor, which happened on two consecutive releases.

Tags *are* compared, in three directions: a completed release git holds no tag
for is an error, a release tag no version-table row names is an error, and the
roadmap's own count of deliberately untagged versions is held to git. A tag
that is present is also held to where it points: on the commit that added its
release's notes, which is that release's cut, or, for a release cut before
notes were written, on a tree declaring its version (`PL-YKSD`, `PL-QHCW`). What the
check will not do is speak when it cannot tell a missing tag from an unfetched
one — a check that fails on how somebody fetched the repository gets switched
off. So it says nothing when the checkout holds no tags at all, withholds the
findings a truncated clone could have invented, and says nothing about the
release being cut right now, whose tag goes on a merge commit that does not
exist yet (`PL-J295`, `PL-R7C0`). That last silence is safe because the version
stops being the baseline as soon as a newer one lands, and is an error from
then on — which is when an untagged release first costs anything. `docket
release` is the other half, refusing to cut a release while the previous one is
untagged, at the moment tags are certainly to hand.

`check_resident_instructions` measures the resident instruction set: the text
every session loads at launch, before it has read anything. That is
`CLAUDE.md`, the rules under `.claude/rules/` that carry no `paths:`, and what
the session-start digest adds. It prints the total on every run, with each
file's change against the tip of the default branch. It is an advisory and
never a gate. A limit would be met by deleting a rule to reach a number, and no
number could know which rules a session must see first. Two advisories can
follow the total, and both stay quiet below `MATERIAL_RESIDENT_DELTA`
characters. The first names growth. The session that added the text then
routes it to the cheapest thing that delivers it when it is needed (a check,
the `docket` skill or a path-scoped rule), or keeps it and says why a session
could break it before it would look anything up. The second names a change
that both grew and shrank the set, because text cut to pay for an addition
never shows as growth in the total. `CLAUDE.md` § "The queue, and how the
project owner works" states the routing rule, and
`docs/resident-instructions.md` records what each resident block was tested
against.

Everything here depends on nothing outside the standard library and parses
under whatever bare `python3` is on PATH: `make check` invokes the ones that
parse no repository source that way directly, CI's floor section runs `python3 tools/doc_check.py check`
before any virtualenv exists, and both have to work in a checkout with no
virtualenv. That is why the floor these tools are held to is
**Python 3.11** — not the version `pyproject.toml` requires. The floor is not a
number chosen here: `doc_check.py` imports `docket.roadmap` for the release
train and `docket.config`, `docket.model` and `docket.store` for the queue, so
it is whatever `subprojects/docket/pyproject.toml` declares in
`requires-python`.

`.claude/hooks/` is held to the same floor for the same reason, and its
`ruff.toml` inherits the pin from `tools/ruff.toml` rather than restating it.
Claude Code invokes a hook as bare `python3` too, so a hook moved out of
`tools/` would otherwise be formatted at the repository's 3.14 target and
become unparseable by the interpreter that runs it.
`tests/unit/test_tools_portability.py` covers both directories by path rather
than by filename, so the guard follows the next hook without being extended.

Nine of them are nonetheless *invoked* only under `uv run python`, and two
more both bare and under it (below), and the distinction is worth keeping
straight, because it is about what a tool reads
rather than what it needs. `ignore_check.py` is the odd one and the only one
of the nine with a reason of its own: it shells out to mypy, so it wants the
virtualenv that gate runs in.

The other eight are one reason repeated. `import_boundary_check.py`,
`contrast_check.py`, `agent_identity_check.py`, `workflow_paths_check.py`,
`core_vocabulary_check.py`, `glyph_check.py`, `fixture_id_check.py` and
`literal_home_check.py` each
parse repository source
with `ast`, and that
source targets 3.14: `app_metadata.py` writes `except OSError,
subprocess.SubprocessError:` without parentheses, a PEP 758 form added in 3.14
and so a `SyntaxError` to the 3.11 parser (as `app/bookmarks.py`'s PEP 695
type parameters are too), and
`ast.parse`'s `feature_version` only narrows the syntax it accepts rather
than extending it. A tool that parses repository source can only run under an
interpreter that understands that source. All of them still meet the promise
above — standard library only, parseable at the floor — which is what the
portability suite holds them to, and it is why they stay in scope for it while
being absent from the CI floor section.

`contrast_check.py` is why the group is worth naming rather than left to each
tool's own docstring. It ran bare until `PL-L17Q`, green only because the two
files it then read happened to carry no 3.12+ syntax, so one PEP 695 generic added
to either would have failed the floor section on a tool nobody had touched. The
rule the eight are an instance of is stated in
`tests/unit/test_tools_portability.py`'s module docstring, and a tool joining
them belongs on the `uv run python` lines in both `Makefile` and
`.github/workflows/quality.yml`, never in that workflow's floor section.

`doc_check.py` and `possessive_section_check.py` are the exception, run both
ways. They parse repository source as well - every module's docstrings, for
the citations in them - and the floor section runs them bare all the same,
where each names on a "Not checked" line the files the floor parser cannot read
and passes rather than failing on them. Both gates also run them through `uv
run python`, which is the run that checks those files. Until `PL-MB3F` the
floor skipped them without a word, `make check` ran both bare, and the
possessive check read neither `app/bookmarks.py` nor `app_metadata.py` in
either gate.

`tools/ruff.toml` is what keeps that true. The repository targets 3.14, where
PEP 758 makes the parentheses in `except (OSError, TimeoutError):` redundant,
so a 3.14-targeted `ruff format` removes them and 3.11 can no longer parse the
file — a break the test suite cannot see, because it runs under the project
virtualenv and only the bare-`python3` invocation fails. The file extends the
repository's rules and overrides `target-version` alone;
`tests/unit/test_tools_portability.py` holds it to the declared floor, holds
every file here to parsing at it, and holds every import here to the standard
library plus in-tree `docket` — the same failure one step earlier, since a
package resolvable only inside the project virtualenv is a `ModuleNotFoundError`
under bare `python3`. A tool added later inherits all three.
`subprojects/docket/` carries the same guards for the same reason.

All of those are approximations run under the project virtualenv — a syntax
gate rather than an older parser, and the wrong interpreter's
`sys.stdlib_module_names`. The floor section of
`.github/workflows/quality.yml`'s `checks-part-1` job performs the run they stand in
for: `actions/setup-python` at the declared floor, then <!-- floor-commands -->
`python3 tools/doc_check.py check`, `python3 tools/possessive_section_check.py`,
`python3 tools/branch_id_check.py`, `python3 tools/rules_paths_check.py`,
`python3 tools/worker_runs.py check`,
`python3 tools/pr_body_check.py --anchors`, `python3 tools/dead_ends.py check`,
`python3 tools/fact_home_check.py` and `bin/docket check` under it. On a pull
request, `bin/docket ci-scope` runs under it first, to decide whether the run
takes the item-only fast path (`PL-DXD4`). <!-- /floor-commands -->
`tools/doc_check.py`'s `check_floor_list` holds the commands between those
two markers to the steps the floor section runs (`PL-5N7T`). `dead_ends.py` and `bin/docket
check` joined the section under `PL-PBP5`, which found them enforced by `make
check` alone; `tools/doc_check.py`'s `check_gate_parity` now refuses that
asymmetry in both directions, so this list cannot fall behind the Makefile's
again without the gate saying so. It runs ahead of the uv install rather than in a
job of its own (`PL-D551`), which is what keeps the no-virtualenv claim true:
at that point none exists. `contrast_check.py` was there too until `PL-L17Q`
and is deliberately not now, for the input-versus-dependency reason above.
That decides syntax, imports and runtime behavior at once, with no list to keep
current. A fourth test holds that section's pinned version to `requires-python`, so
raising the floor cannot leave CI exercising an interpreter the project no
longer supports. The approximations stay because they name the offending file
and import, run before a push, and reach what those commands never do.

## Wired hooks (`.claude/hooks/`)

The twelve scripts `.claude/settings.json` wires as hooks live in
`.claude/hooks/`, not in `tools/`, and the reason is a guard rather than tidiness.
`.claude` is a *protected directory* in Claude Code's own list, so a write to
anything under it is never auto-approved: it prompts, or in auto mode routes to
the classifier ([protected
paths](https://code.claude.com/docs/en/permission-modes#protected-paths), read
2026-09-05). A `permissions.allow` entry cannot lift that — the safety check
runs before allow rules are evaluated — so the directory is the guard, and
putting a hook anywhere else silently leaves it out. `stop_hook_patch.py` sat
in `tools/` until `PL-W4H9`, which is exactly the gap that item names: a script
that rewrites another hook, editable without review. `docket-digest.sh`,
`docket-branch-guard.sh`, `item_read_log.py`, `no-prune-guard.sh`,
`floor-interpreter-guard.sh`, `gate-status-guard.sh`, `push-check-guard.sh`,
`direct-merge-guard.sh`, `pr-body-email-guard.sh`, `owner_ask_guard.py` and `webfetch-quote-note.sh` are documented where their
behavior is, in their own headers. `shell_split.py`
is the one file there that nothing wires: the four Bash guards import it for where one shell command
ends (`PL-PVW2`). The reading itself is docket's `subprojects/docket/src/docket/shell.py`,
which `shell_split.py` finds from its own place, the one lexer docket and the
guards share (`PL-JNYL`). Which word of a git call is its command is docket's
too: `no-prune-guard.sh` and `push-check-guard.sh` read
`subprojects/docket/src/docket/gitargv.py`, the table `docket.vcs` reads, and
the push guard reads the default base and git's answers through `docket.vcs`
once it has found a push (`PL-ZXCN`). So the code that decides what the guards refuse lies
outside the protected directory, and an edit to it is approved as any other
edit is. A pull request changing it arms on green, as one changing
`.claude/hooks/` does, since the owner's rule of 2026-10-12 that workflow
items need no merge confirmation (`PL-KPM2`).

`.claude/hooks/stop_hook_patch.py` is the one hook here that is not a check and
does not run under `make check`. It is wired as a SessionStart hook, and it
edits a file this repository does not own:
`~/.claude/stop-hook-git-check.sh`, which a cloud container writes at start and
runs at every `Stop`. That hook counts unpushed commits against
`origin/<branch>` whenever that ref *resolves locally*, so a merged branch's
surviving tracking ref makes it demand a push that would recreate a dead branch
identical to `main`. The correction counts commits held by no remote ref
instead. It is a hook rather than a patch the project owner applies because the
file is not theirs to change: a container rewrites it at every start,
user-level settings never reach a cloud session, and an environment setup
script runs before Claude Code launches and is skipped once the environment
cache exists. The script matches one whole line and rewrites nothing if it is
absent or doubled, so an upstream change is a clean miss that reports itself
rather than a partial edit to a script every stop executes. `PL-WW08` carries
the diagnosis and the measurements.

It does a second thing for the same reason, and the two are one job: counting
commits held by no remote ref only works if this checkout *has* such refs. The
harness provisions the clone by fetching the default branch alone at depth 50
(`PL-2H0K`), so `remote.origin.fetch` names the default branch alone and
`git push` never writes `refs/remotes/origin/<branch>` — every commit on a
pushed branch then reads as unpushed however many times it has been pushed. The hook widens that
refspec, which repairs the clone rather than the test and keeps the stop check
offline instead of trading it for a network call at every `Stop`. It only ever
widens, and it neither fetches nor prunes, so it cannot destroy a ref
`bin/docket stranded` needs. `PL-3SGR` and `PL-483K` are the two reproductions.

## Third-party text (`tests/unit/markdown-specs/`)

The CommonMark 0.31.2 specification and cmark-gfm's GitHub Flavored
Markdown 0.29 specification are vendored unmodified, each named for the
release tag it was fetched at, because
`tests/unit/test_inline_reference.py` reads their examples as the corpus
`tools/doc_check.py`'s inline Markdown is held to markdown-it-py over, and
holds each to the SHA-256 of what that tag published (`PL-R417`).
`subprojects/docket/tests/test_markdown_reference.py` holds
`docket.markdown.emphasis` and `docket.release.code_spans` to markdown-it-py
over the same examples (`PL-47NJ`, `PL-T3GW`). Both are licensed CC-BY-SA 4.0, as each file's front matter states with the licence's
address. The licence lets a copy be shared whole, unmodified, with its notices
kept (§ 2(a)(1), § 3(a)(1)), and attaches its ShareAlike condition only to an
adaptation (§ 3(b)), which these are not, so the repository's Apache-2.0 does
not reach them and they do not reach it
(https://creativecommons.org/licenses/by-sa/4.0/legalcode.en, read
2026-10-10).
