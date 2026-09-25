---
id: PL-J16N
title: No real-git test pins the editing mark for a round that retitles its item's file, and two test_vcs.py fakes list a rename's paths whatever the reader asks git
priority: P3
effort: S
status: done
classes: defect
feature: parallel-sessions
touches: subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, docs/items/PL-MB2W-who-holds-an-item-is-derived-by-every-reader.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
closed: 2026-09-25
payoff: a design round that retitles its item still warns the next session through show and triage, and each fake-backed rename test is built on the listing git gives its reader
verify: grep -q 'def test_show_names_a_round_that_retitled_the_item_file_as_editing_it' subprojects/docket/tests/test_cli.py
---

**Problem.** No real-git test pins the editing mark for a round that retitles its item's file, and two test_vcs.py fakes list a rename's paths whatever the reader asks git

**Re-scoped 2026-09-25, on the owner's answer.** Filed against
`vcs._modified_by`, which read a design round that renamed its item's file as a
capture, because `git log --name-only` prints a rename as its new name alone;
and against the fake behind `test_a_round_that_renames_the_item_file_still_claims_it`,
which listed both names and so could not fail on it. `PL-FX5Q` (#1016) deleted
`_modified_by`, `_own_edit_claims`, that test and the `_report` fake behind it,
so the claim half is moot: `claims.holdings` reads claims from trailers and
statuses by id, and no claim reader reads rename paths (`PL-MB2W` § "The
members against this design"). The re-scope recorded there: "the fake runner's
`--name-only` rename fidelity, with a real-git test, because `editing` still
reads diff paths."

**Answered 2026-09-25: re-scope it** (project owner, 2026-09-25, ratified, over
closing it as answered by `PL-FX5Q` and `--no-renames`, and over leaving the
re-scope to `PL-MB2W`'s close-out). Put to the owner by the project's
coordinator, after a read of `origin/main` at `46954a81` found the brief aimed
at deleted code.

**Where the re-scope lands, decided by the session working it.** The fake that
sentence names went with `PL-FX5Q`, and `editing` is now read by
`claims._editing`, whose tests in `test_claims.py` run real git. So the real-git
test drives `show`, which prints the mark (`flight` does not), and the fidelity
lands on the two `test_vcs.py` fakes that still hand a rename to a
`--name-only` read.

**What still reads diff paths.** `claims._history` lists each commit's paths
with `git log --no-renames --raw`, through `vcs.changed_path_args`. `_touched`
keeps, per item id, the last path listed by the newest commit touching it.
`_editing` looks the item's path at the branch tip up by id, falls back to that
listed path, and hands it to `vcs._superseded`, which reads `git diff --numstat
--no-renames <base> <tip>` for it and calls a path with removals only an edit
the base already holds.

**Measured 2026-09-25, git 2.43.0, in a scratch repository.** A branch renames
`items/PL-0001-on-main.md` to `items/PL-0001-a-narrower-title.md`, changes the
title line and appends a recommendation, and git scores it `R078`. `git diff
--name-only` prints the new name alone; with `--no-renames` it prints both, new
name first, so the path `_touched` keeps is the deleted one. `show PL-0001`
prints `Its file is already edited on <branch>`, because the tip lookup finds
the new name. With `_editing` handed the listed path instead (`paths =
dict(wanted)`), the mark vanishes and nothing says so: the deleted path reads
as removals only. All 1,855 docket tests pass on that change. Dropping
`--no-renames` from `changed_path_args` fails six, none of them on `editing`:
`verify`'s protected-path audit (two), `arm`, `files_in_flight`, and two
`test_vcs.py` fakes that read `diff --numstat`'s arguments by position.

**The fakes.** `test_vcs.py` asserts rules with git injected, and two of its
fakes hand a rename to a `--name-only` read. `_closed_by_runner`, behind
`test_a_closed_item_renamed_by_the_commit_was_not_closed_by_it`, lists both
names whatever it is asked. `_record_runner`, behind
`test_a_retitled_item_is_found_by_id_rather_than_by_path`, lists the new name
alone, where `records_on_base` asks with `--no-renames` and git lists both.
Both readers compare by id, so neither answer changes. What is wrong is the
listing the tests are built on, which is this item's original defect: a
fake-backed rename test built on output git does not give that reader.

**Why it matters.** When the mark is lost, `show` and `triage` tell a session
that nobody has touched a file a design round has already rewritten, and the
two collide at merge (`PL-N1JK`). A retitle is the normal shape of a round that
narrows its question. Ranked `P3`: the reader is correct today, and what is
missing is the test that would say so if it stopped being.

**Done when.**

- `test_show_names_a_round_that_retitled_the_item_file_as_editing_it` in
  `subprojects/docket/tests/test_cli.py` runs on a real checkout. The base
  holds an item at `needs-decision`. A branch's one commit is queue-only and
  retitles the item's file to a name sorting before the old one, with an edit
  light enough that git pairs the two. The test checks that pairing and the
  `--no-renames` listing order rather than assuming them, and `show` prints the
  editing mark. It fails with `paths = dict(wanted)` in `_editing`; a new name
  sorting after the old passes either way, which is why the order is chosen.
- `_closed_by_runner` and `_record_runner` take a rename as `(old, new)` and
  list it as git does for the argv they are sent: both names, sorted, under
  `--no-renames`, and the new name alone without it. One helper holds that
  rule and cites the measurement above, and the two rename tests pass their
  renames that way.
- The closing commit repairs `PL-MB2W` § "Build", which still names this
  re-scope as close-out work.

**Generator check.** A member of `PL-MB2W`, which answered its claim half and
re-scoped the rest. What is left is a test gap and two fakes, and no other open
item shares either. `PL-3LLZ` is about the fakes' duplication, a different
mechanism: the helper here holds one rule for two fakes and consolidates
nothing else.
