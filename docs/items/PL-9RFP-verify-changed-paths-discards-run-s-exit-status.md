---
id: PL-9RFP
title: verify.changed_paths discards _run's exit status and _run returns combined stdout+stderr, so any base that does not resolve makes git's three-line fatal message come back as three changed paths and the commission audit reports them as findings while missing the real ones
priority: P2
effort: S
status: done
classes: defect
feature: evidence-declines
milestone: v0.5.7
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/README.md, docs/items/PL-19T3-changed-items-answers-confidently-that-nothing.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-14QR's 2026-09-22 triage pass
added: 2026-09-22
closed: 2026-09-23
pr: 933
payoff: the commission audit says it could not read the diff when the base does not resolve, instead of auditing git's error text as three edits and missing the real ones
verify: grep -q 'def test_changed_paths_declines_an_unresolvable_base' subprojects/docket/tests/test_verify.py
root-cause-of: PL-19T3, PL-ZPDM, PL-73P0, PL-MM7F
generator: spent - both runners it named now raise rather than answer. verify's seven reads go through _git, verify_item reports anything they raise as the diff could not be read, and test_verify fails any _run status bound to _. doc_check's _git raises, and candidates says it swept nothing. PL-19T3 is left: _run_git has a channel and reads exit 1 outside a repository as an answer
misread: Whether a git read answered or failed
---

**Problem.** verify.changed_paths discards _run's exit status and _run returns combined stdout+stderr, so any base that does not resolve makes git's three-line fatal message come back as three changed paths and the commission audit reports them as findings while missing the real ones

**Reproduced 2026-09-22 (`PL-14QR`, triage).** `verify.changed_paths(<repo root>,
"no-such-base-ref")` returned three "paths":
`'git <command> [<revision>...] -- [<file>...]'`,
`Use '--' to separate paths from revisions, like this:` and
`fatal: ambiguous argument 'no-such-base-ref...HEAD': unknown revision or path not in the working tree.`
The call is `_, committed = _run(["git", "diff", "--name-only", f"{base}...HEAD"], root)`.
The status is bound to `_`, and `_run` returns stdout and stderr together.

**Why it matters.** `changed_paths` feeds the commission audit, which reports
changed paths that fall outside an item's declared `touches`. With the base
unresolved, the audit reports git's usage text as three out-of-scope edits,
which reads as the branch having done something it did not. It also reports
none of the branch's committed edits. So the check that exists to catch work
outside an item's scope passes a diff it never read. This is the same shape as
the rest of `evidence-declines`: a read that could not be taken has to say so,
not return its failure text as data.

**Done when.** `changed_paths` reads git's exit status on each call it makes.
When the base does not resolve it declines rather than answers, and the audit
then says the diff was unread. A test in `subprojects/docket/tests/test_verify.py`
holds it with a base that does not exist.

**Built 2026-09-23, and wider than "Done when" on purpose.** The reproduction
showed that `changed_paths` was the second read to fail, not the first.
Against a base that does not resolve, `item_commits` passed git's complaint on
as three commit hashes, and the commission check named `fatal: invalid object
name 'fatal'.` as an edit. Both integrity checks PASSed on a diff never read.
So `bin/docket verify PL-9RFP --base no-such-base-ref --self` would have
ACCEPTed once the item's own command passed. Fixing `changed_paths` alone
leaves all of that, and the `generator:` line named the mechanism rather than
the one read, so all seven reads that discarded a status moved:

- `verify._git` returns stdout only. On any non-zero exit it raises
  `GitUnanswered` carrying git's first stderr line. `item_commits`,
  `changed_paths`, `_diff_text` and `other_items_named` read through it. It
  raises rather than returning a result that carries `declined`, because none
  of the callers has another value to return. A raise nobody catches fails
  loudly, where a forgotten `declined` would be silent again.
- `verify_item` catches it in one place, around every check (`_check_item`).
  It appends `the diff could be read` as a blocking failure with git's reason,
  keeps the checks that ran, and stops early. Self-audit behaves the same.
- `cmd_check --verify-base` declines the replay when `changed_paths` declines,
  as it already did when `changed_items` did.
- `doc_check._git` raises instead of returning `[]`, and `candidates` prints
  that it swept nothing and exits 1.
  `test_candidates_mode_is_quiet_when_nothing_changed` had been passing on a
  directory with no repository in it, so it pinned the silent answer. It now
  builds a repository.
- `test_no_run_call_in_verify_discards_its_exit_status` scans `verify.py` for
  a `_run` status bound to `_`. On the pre-fix file it named exactly the
  seven.

Every new or changed test was run against the pre-fix source, and all seven
that should fail there did.
