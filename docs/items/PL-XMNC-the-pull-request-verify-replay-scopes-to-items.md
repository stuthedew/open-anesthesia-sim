---
id: PL-XMNC
title: The pull-request verify replay scopes to items whose item file the branch edited, so a branch that invalidates some other item's verify: command by editing the file that command reads replays nothing, and the break is reported only by the whole-store sweep after the merge
priority: P2
effort: L
status: ready
classes: defect, infra
feature: verify-invalidation
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_checks.py
added: 2026-09-17
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_the_replay_scope_reaches_an_item_whose_command_reads_a_changed_file' subprojects/docket/tests/test_checks.py
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

**Why it matters.** A `verify:` command that has stopped discriminating is a gate
reporting success over a guarantee that is void - the first of `CLAUDE.md`'s
three compounding-friction tests - and it sits in the check every merge to `main`
runs. Today it is reported only by the whole-store sweep *after* the merge, so
`main` goes red on work no open pull request can see, which happened three times
before 2026-09-17 and twice in one day. The pull request that breaks it is the
one place the break is cheap to fix, and it is the one place nothing looks.

It also carries `PL-879R`'s goal, which was dropped on a count rather than
abandoned: report the break before it has started passing. Six of six recorded
instances are caught here against four of six for the shape check that was
refused, at a measured worst case of ten extra replays.

**Done when** a pull request that edits a file an open item's `verify:` command
reads replays that command and reports it if it now passes; the clause-splitting
that keeps the health half (`tools/doc_check.py` appears in 54 of 168 commands)
out of the scope is covered by tests; an unclassifiable path widens the scope or
is reported rather than silently narrowing it; and `docket check`'s cost line
says what the widened scope was.
