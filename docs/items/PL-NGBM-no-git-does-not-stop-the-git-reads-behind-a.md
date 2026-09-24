---
id: PL-NGBM
title: --no-git does not stop the git reads behind a printed count, so docket digest --no-git shells out to git despite the flag saying branch detection is off
priority: P3
effort: M
status: done
classes: defect
feature: count-input-addressing
milestone: v0.5.7
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-09-20
closed: 2026-09-23
pr: 930
payoff: --no-git either means what its help says or says what it means, so a session reading a digest count under the flag can tell which reads were skipped
verify: grep -q 'def test_no_git_stops_every_git_read' subprojects/docket/tests/test_cli.py && grep -q 'def test_every_git_read_in_the_cli_takes_the_invocations_runner' subprojects/docket/tests/test_cli.py
root-cause-of: PL-T441, PL-WF3X, PL-N0MH, PL-3T2Q, PL-M6FY, PL-P757
generator: spent - cli.py resolves one Invocation per command, the one place root, store, settings, the store's git prefix and the runner are derived; test_no_git_stops_every_git_read and test_every_git_read_in_the_cli_takes_the_invocations_runner fail any call site that goes round it
misread: Where the item store sits relative to the repository root, as the path prefix git prints for it
---

**Problem.** `_flight`, `_stranded` and `_orphaned` each return an empty
report under `--no-git`, so the flag holds for everything the digest used to
do. The inputs `cli._complete_report` gathers do not check it: `cmd_check`
never did, and `digest` and `next` inherited that when `PL-VKGJ` routed all
three through one gathering. So `bin/docket digest --no-git` now runs
`merged_pull_requests`, `closures_on_base`, `records_on_base`, `lost` and
`cut_window` - about 250 ms of git subprocesses - under a flag whose help
reads "skip branch detection".

**Why it matters.** Small in cost and a correctness question in kind: a flag
that turns some git reads off and not others cannot be reasoned about, and the
help text says the wrong thing either way. Honouring it in all three keeps
`PL-VKGJ`'s invariant intact, because all three would then skip the same
inputs and still print counts that agree.

**Done when.** `--no-git` either stops every git read behind a printed count,
in all three commands alike, or says in its help that it means branch
detection only - and a test pins whichever was chosen.

**Design, 2026-09-23 - the fix is the generator's, and this done-when is one
facet of it.** The session that claimed this measured `cli.py` at `c903f738`
and handed off for length before building. The `generator:` line is the
diagnosis and the census bears it out: `cli.py` makes 31 calls into `vcs`
(and 4 into `verify`, which take no runner), and every one decides for itself
whether `--no-git` applies and whether to share the invocation's runner.

- **`--no-git`** is honoured in `_flight`, `_stranded`, `_orphaned`, `_cuts`,
  `_filed`, `_inferred_paths`, `cmd_trend` and `cmd_release`, and ignored
  everywhere else: the five reads in `_complete_report` (this item),
  `cmd_check`'s `--verify-base` scope (`changed_items`, `changed_paths`),
  `digest --profile`, `cmd_flight` (never checks at all), `cmd_stranded`
  (fetches *before* `_stranded` returns `None`, so `stranded --no-git` goes to
  the network), `cmd_branch`, `cmd_verify` and `cmd_record`.
- **The runner** is passed at 8 `vcs` calls and omitted at 22, each omission
  building a second runner that loses the cat-file memo: `_complete_report`'s
  five, `cmd_check`'s `changed_items`, `cmd_flight`'s two (`PL-M6FY`),
  `cmd_show`'s `precedence`, `_print_observed`'s `files_in_flight`, the four
  in `cmd_release`, `_numbers_before_notes`, `cmd_record`, `_record_owed`,
  `cmd_trend`, `cmd_stranded`, `cmd_branch`'s two and `cmd_verify`'s
  `default_base`. `digest --profile`'s `ref_walk` is deliberately plain, and
  its comment says why.
- **The store prefix** is derived four times, with three different answers
  for a store outside the checkout: `_tracked` (the empty prefix), `_stranded`
  (`None`), `_numbers_before_notes` (skip) and `cmd_record` (refuse, exit 2).
  `_tracked` answers `.` for a store at the root itself (`PL-3T2Q`).
- **The settings** are loaded three times (`_load`, `_tracked`, `cmd_flight`),
  and `_settings_source` is reached only from `_complete_report` (`PL-N0MH`).

**The fix: one `Invocation`, resolved once per command.** A dataclass in
`cli.py` holding `root`, `directory` (the store), `config`, `tracked` (the
store as git spells it), `settings` and `git: GitRunner | None`, plus the
flight cache. Built by `_invocation(args)` and kept on the namespace - the
idiom `_runner` and `_flight` already use, for the lifetime reason their
comments give - so it absorbs `_RUNNER_ATTR` and `_FLIGHT_ATTR`, and `main`
closes `inv.git`. `_root`, `_tracked`, `_runner` and `_settings_source` stop
being per-call accessors and become the derivation of one field each, their
docstrings moving with them. `_load(args)` stays and reads the store fresh on
every call, because `set`, `new` and `withdraw` write between reads.

`--no-git` becomes `git` being `None`, and there is no other test for it:
every `getattr(args, "no_git", False)` and `args.no_git` goes. A read site
takes `git` and returns its declined or empty form when that is `None`. Per
command:

- `check`, `digest`, `next`: `_complete_report` passes `None` for `history`,
  `closures`, `records`, `lost` and `window`, which `analyze` reads as
  unasked, so all three skip the same inputs and `PL-VKGJ`'s agreement
  holds. `check --verify-base` declines its scope through
  `LandedReport(declined=...)`, naming the flag. A bare `--verify` still
  replays, because the commands it runs are the project's rather than
  docket's reads.
- `flight`, `stranded`, `branch`: print `stranded`'s existing line, "branch
  detection is off (`--no-git`), so nothing was read", before any fetch.
  `branch --brief` and `--if-stale` print nothing, as they do for an absent
  base.
- `verify`, `record`: refuse, each with its own refusal code (1 and 2),
  because a diff against a base is their whole answer.
- `concurrent`: the observed section says branch detection is off. Its
  "nothing - which means no branch has touched these files *yet*" is, under
  the flag, a claim about a read that was never made.
- `digest --profile`: nothing to profile, and it says so.
- The help text: "ask git nothing: no branch detection, and none of the
  history reads behind a count".

The prefix gets one derivation, with `.` normalised to the empty prefix, so
the root itself and a store outside the checkout take the same value - the
first branch of `PL-3T2Q`'s done-when. The three readers that answer an
empty prefix differently (`_stranded` and `_numbers_before_notes` skip,
`record` refuses) test `inv.tracked` rather than recomputing it.

**Two tests hold it, one for each facet a later call site could drop.**

- `test_no_git_stops_every_git_read`: in a real git repository, so that a
  read would succeed and be seen, wrap `subprocess.run` and
  `subprocess.Popen` to record any `git` argv (`vcs._run_git`, the cat-file
  batch and `verify._run` all go through those two), run every command under
  `--no-git`, and assert that none was spawned. It is behavioural, so it
  covers the `verify` reads that take no runner.
- `test_every_git_read_in_the_cli_takes_the_invocations_runner`: an AST walk
  over `cli.py` in the shape of
  `test_no_git_read_in_the_cli_takes_the_store_from_the_settings`. Every call
  to a name imported from `.vcs` whose `inspect.signature` has a `runner`
  parameter passes `runner=`, and `ref_walk` passes its plain runner
  explicitly. It covers a read added later without anybody listing it, and
  it fails on today's tree at the 22 sites above.

**Members.** `PL-M6FY` and `PL-3T2Q` close with this, by construction, each
proven by one of the tests. `PL-N0MH` stays open, reduced to the render
question it already asks, since the settings now reach every command. On
close, `generator:` becomes `spent`: the invocation is the one place any of
the five facets is derived, and each test fails a call site that goes round
it.

**Sequencing.** `origin/claude/clever-thompson-1sdll0` (`PL-7TVT`'s
liveness work, running on 2026-09-23) has changed `cli.py` and
`test_cli.py`, `cmd_flight` among them. If its pull request has merged,
bring the base in first. If not, proceed and expect to resolve against it.

**Built, 2026-09-23 - where the design and the code differed.** `PL-7TVT`
merged first (#924), and it added a third read to `cmd_flight`
(`open_pull_requests`), so 23 sites built their own runner rather than 22.
Five existing tests reached git through `_run`, which passes `--no-git`, and
passed only because the flag was ignored; they moved to `_run_with_git`, and
four `fetch_remote` stand-ins now take the `runner` keyword. Neither of the two
tests proves a member's own `verify:`, which names a test of its own: so
`test_flight_shares_the_invocations_git_runner` (`PL-M6FY`) and
`test_a_store_at_the_repository_root_is_the_empty_prefix` (`PL-3T2Q`) were
written to those names. The
behavioural test watches `Popen` alone, since `subprocess.run` constructs one.
The runner test also refuses a site that constructs a runner of its own, which
presence of `runner=` alone would have passed. `stranded` on a store git
cannot address used to blame `--no-git`, and now says the store is not below
the root.
