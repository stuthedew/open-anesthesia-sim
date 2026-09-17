---
id: PL-XMNC
title: The pull-request verify replay scopes to items whose item file the branch edited, so a branch that invalidates some other item's verify: command by editing the file that command reads replays nothing, and the break is reported only by the whole-store sweep after the merge
status: done
feature: verify-invalidation
added: 2026-09-17
closed: 2026-09-17
priority: P1
effort: M
classes: defect, infra
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .github/workflows/quality.yml, docs/ARCHITECTURE.md
verify: uv run pytest subprojects/docket/tests/test_verify.py subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_branch_editing_a_file_a_verify_command_reads_is_in_scope' subprojects/docket/tests/test_verify.py
---

**Problem.** The pull-request verify replay scopes to items whose item file the branch edited, so a branch that invalidates some other item's verify: command by editing the file that command reads replays nothing, and the break is reported only by the whole-store sweep after the merge

**Where it comes from.** `PL-879R` was filed to ask whether `docket check` could
advise on a `verify:` command's *shape*, so that a tautological command was
reported when written rather than when it started passing. It was dropped
2026-09-17 on a count: of the 168 open items carrying a command, the only
subset with a real population is the 36 with a negated discriminating half, and
all 31 of those whose negation is the sole assertion still discriminate on an
untouched tree. An advisory there would print 31 correct ids every run. But
`PL-879R`'s *goal* — report the break before it has already started passing —
is unmet, and the mechanism that meets it already exists. This item is that
mechanism. `PL-879R`'s brief carries the counts.

**The gap, exactly.** `.github/workflows/quality.yml` runs `bin/docket check
--verify --verify-base "$VERIFY_BASE"` on every `pull_request`, which is right,
and the whole-store `--verify` only on pushes to the default branch, which is
also right (`PL-SDHR`: the bill grows with the queue rather than with the
change). The scope comes from `vcs.changed_items()` — "the item ids this
checkout has changed against `base`", read from the `docs/items/` diff.

So a command is replayed on the pull request that **writes** it and never on
the pull request that **invalidates** it. Every recorded instance was the
second case: a branch edited a file some other item's command reads, without
touching that item's file.

| Item | Its command reads | Invalidated by | That branch touched it |
| --- | --- | --- | --- |
| `PL-XH1D` | `CONTRIBUTING.md` | `#487` (`4a4a483`) | created it |
| `PL-X9T3` | `docs/WORKING_NOTES.md` | `#490` (`f393e16`) | yes |
| `PL-MMWX` | `ROADMAP.md` | its own branch | already in scope |
| `PL-L9FC` | `README.md` | `#512` (`bc21c32`) | yes |
| `PL-D1RT` | `ROADMAP.md` | `#634` (`52205f6`) | yes |
| `PL-C4RS` | `ROADMAP.md` | `#640` (`e5ad821`) | yes |

**What to build.** Widen the pull-request replay's scope from *the items this
branch changed* to *the items this branch changed, plus the open items whose
`verify:` command reads a file this branch changed*. The second half is the new
part and it is decidable from the text: `verify.py` already has
`_outside_quotes`, which is the hard half of reading a shell line safely.

Two properties to preserve, both of which the existing code already models:

- **Only the discriminating clauses' paths count.** `tools/doc_check.py` appears
  in 54 of the 168 commands and is the health half in every one of them, so
  counting it would make any edit to that file drag 54 replays behind it. Split
  on `&&`, `||` and `;` outside quotes, as `reads_check_output` already does
  with `PIPELINE_END_RE`.
- **Decline rather than guess.** `changed_items` returns nothing where it cannot
  resolve a merge base, and `docket check`'s cost line says what a scoped run was
  scoped to. A path this reader cannot classify should widen the scope or be
  reported, never silently narrow it.

**What it costs, measured 2026-09-17.** 83 distinct files are read by some open
item's discriminating clause. Worst case is 10 extra replays
(`docs/WORKING_NOTES.md`), then 8 (`subprojects/docket/tests/test_checks.py`),
7 (`ROADMAP.md`), 6 (`subprojects/docket/tests/test_cli.py`), 6
(`docs/MODEL.md`). A branch touching none of the 83 adds nothing, which is most
branches. Against the 87 s the whole-store sweep cost on run 33998014593, this
is small.

**Why it beats the check it replaces.** It catches six of the six recorded
instances against the shape check's four, at the same moment; it needs no
judgment about whether a phrase is uniquely one item's work, because it runs
the command and reads the outcome, which `_check_landed` already knows how to
phrase; it fires on zero items for a branch that invalidates nothing; and it is
indifferent to the command's wording, so it covers shapes nobody has thought of
yet.

**Done when** a pull request that edits a file an open item's `verify:` command
reads replays that command and reports it if it now passes, with the scope
widening and its clause-splitting covered by tests, and with `docket check`'s
cost line saying what the widened scope was.

**Why it matters.** This is the gate every merge to `main` runs, and it is
blind in the one direction the failures actually come from. Six recorded
instances, three of them inside 2026-09-16, each the same shape: a branch edits
a file some other open item's `verify:` command reads, that command flips from
failing to passing with nobody having touched the item it guards, and `main`
goes red on the push-to-`main` sweep where no pull request could have shown it.
`PL-XF2Y` recorded two landing on one day, which is the rate rather than an
anecdote.

It meets `CLAUDE.md`'s compounding-friction tests on two counts. The check
**gives a wrong answer silently** - while an item's command already passes,
`docket verify` would `ACCEPT` a branch that did none of that item's work - and
it **sits upstream of everything**, in the gate the whole store runs through on
every merge. The cost of leaving it is paid twice: once by whoever finds `main`
red after the fact, and once by every session that reads the queue while a
guard that is supposed to prove doneness is proving nothing. `PL-879R` was the
other route to the same goal and was dropped on a count - a shape advisory
would have printed 31 correct ids on every run, forever, which is the check
`CLAUDE.md` says to retire rather than promote.

**Gate disposition, 2026-09-17** (project owner, ratified — chosen over
re-entering it into Gate 1's frozen list on the ground that the problem it
describes predates the 2026-09-06 freeze). Declined to Gate 2 under
`ROADMAP.md`'s standing refilling-queue ground: the capture postdates the
freeze, Gate 1 is already the largest gate this project has held, and this item
is being cleared immediately, so it holds nothing open either way. Recorded
because the presence rule forbids neither answer being written down, not
because the choice was close to consequential.

## Built 2026-09-17

`verify.command_paths` reads a `verify:` line for the paths it reads *as data*,
clause by clause on `&&`, `||` and `;` outside quotes; `verify.items_reading`
turns a set of changed paths into the open items those paths could have
invalidated; and `cmd_check` unions that with `vcs.changed_items` before
handing the pair to `already_passing`.

**The discriminating half is decided by what a clause runs, not by where the
clause sits.** A clause's program - its first word, plus the script an
interpreter executes - is not a file it reads, so `python3 tools/doc_check.py
check` and `bin/docket check` contribute nothing while `uv run pytest
tests/unit/test_x.py` contributes its argument. Position was the obvious rule
and is wrong: the health clause is last in real commands (`grep -rq …
src/anesthesia_sim/data/ && python3 tools/doc_check.py check`), and 13 of the
169 open commands are a single clause whose whole discrimination is a pytest
selector.

**Textual throughout, and it asks the filesystem nothing**, so a file the
branch is *creating* matches: `PL-XH1D`'s `test -f CONTRIBUTING.md` broke on a
branch that created the file, which existed nowhere in the tree the command was
written against. Where a token cannot be classified it widens - a quoted span
is scanned for paths, and a wrapped interpreter's script (`uv run python3
tools/x.py`) counts as read. A candidate is offered directory containment only
where it carries a `/`; a bare word must match a changed path exactly, so `grep
-q 'src' …` does not put its command behind every edit under `src/`.

**Measured on this store, 168 open items carrying a command.** Of the
repository's tracked files, 1,327 would put at least one item into scope. The
worst case is 17 (`subprojects/docket/tests/test_checks.py`), then 15
(`subprojects/docket/tests/test_cli.py`), 13 each for `test_release.py`,
`test_vcs.py` and `test_verify.py`, and 12 (`tests/unit/test_doc_check.py`).
Both ends are higher than the brief's estimate above, and for the same reason:
a command naming a *directory* covers every file under it — `uv run pytest
subprojects/docket/tests` is why the per-file worst case doubled, and the three
commands that recursively grep `docs/items/` are almost the whole of the 1,327,
one entry per item file. That is correct rather than spurious, and it is
bounded: **a branch that only files a capture adds 3 replays**, and this branch,
which edited `verify.py` and `cli.py`, added 3.

**`vcs.py` was not touched after all**, against the `touches` triage predicted:
`verify.changed_paths` already answers "every path the work has touched,
committed or not" for the commission check, against the same base and with the
same one-sided decline, so a second reader in `vcs.py` would have been
duplicated logic rather than a new capability.

**The cost line names both halves** - "12 item(s) in scope: 9 this branch
changed and 3 whose `verify:` command reads a file it changed against
origin/main" - because they want different reactions. An item this branch
edited and whose command now passes is probably finished work nobody closed;
one it merely invalidated is a command that has stopped discriminating.

