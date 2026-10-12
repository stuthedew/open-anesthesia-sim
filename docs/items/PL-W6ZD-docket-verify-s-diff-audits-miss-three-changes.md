---
id: PL-W6ZD
title: docket verify's diff audits miss three changes - a skip decorator moved from one test to another cancels in the per-file fold, a merge commit's combined diff is read as a two-way one, and an uncommitted edit beside a sanctioned queue write is never read - so a suppression, an added line or a status edit passes unseen; latent
priority: P3
effort: M
status: done
classes: defect
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/python.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_python.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1447
payoff: a skip moved onto another test, a suppression added in a merge commit, or an uncommitted status edit beside a record write can no longer pass verify unreported
verify: grep -q 'def test_a_skip_decorator_moved_to_another_test_is_an_added_suppression' subprojects/docket/tests/test_verify.py && grep -q 'def test_a_merge_commits_combined_diff_is_read_or_declined' subprojects/docket/tests/test_verify.py && grep -q 'def test_an_uncommitted_edit_beside_a_sanctioned_queue_write_is_not_sanctioned' subprojects/docket/tests/test_verify.py
reenters: PL-4W2L
---

**Problem.** docket verify's diff audits miss three changes - a skip decorator moved from one test to another cancels in the per-file fold, a merge commit's combined diff is read as a two-way one, and an uncommitted edit beside a sanctioned queue write is never read - so a suppression, an added line or a status edit passes unseen; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.verify`.

- `added_suppressions` cancels an added logical line against a removed one
  anywhere in the same file, so `@pytest.mark.skip(reason="needs bash")` moved
  from `test_a` to `test_b`, with nothing else changed, reports no suppression
  added, though it now disables a different test.
- `_net_line_changes` reads `git show --format=` output for a merge commit led
  by the item's id, which git writes as a combined diff headed `diff --cc`
  with two-column prefixes (`++`, ` +`, `- `). It skips a `++` line as a
  `+++` header and never resets the path on `diff --cc`, so
  `++xfail_strict = false` in a `pytest.ini` is dropped and the check passes.
  `PL-MR8Z` holds the two-way header misreads; this is the combined format.
- `sanctioned_queue_edit` and `_changes` read commits only, so an uncommitted
  `status: done` or `verify: true` edit on an item file whose committed change
  is a `pr` write still answers `pr`, while `changed_paths` lists the path.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, on scratch repositories. Latent: no commit on `main` moves a
decorator this way, merges carry no item's id, and the working-tree case needs
an uncommitted edit at verify time.

**Re-confirmed 2026-10-11** on main at `16a20a4f`, first form only:
`@pytest.mark.skip(reason="needs bash")` moved from `test_a` to `test_b` in a
scratch repository leaves no net line change, and `added_suppressions` reports
`found=()`.

**Generator check.** Not a member of `PL-R417`: each statement is read whole;
what is misread is its position, the diff's format, or which tree is read.
The first two forms are `PL-4W2L`'s fact, whether a branch's diff weakens its
tests, filed after that head closed on 2026-09-23; with `PL-MR8Z` that is two
real post-close instances (`PL-GXLX` was dropped as false, and `PL-PNZB` reads
the fact but `PL-R417` explains it), short of the three that make a generator.

**Why it matters.** `verify` is the audit a delegated branch's close-out rests
on, and each form lets a branch disable a test, add a configuration line or
edit an item's status while the report reads clean. Latent, since no commit on
`main` takes any of the three shapes, but the third needs nothing more unusual
than an uncommitted edit at verify time.

**Done when.** A suppression is compared with the definition it decorates, a
combined diff is read as one or declined by name, and an uncommitted change to
a path the audit judges is refused or named; a test pins each.

**Fixed 2026-10-12** in `#1447`, one reading for each form.

- `python.places` gives each logical line the definition it belongs to: a
  `def` or `class` itself, a decorator the definition it decorates, as `ast`
  holds it in that definition's node, and any other statement the definition
  holding it. `added_suppressions` counts each statement there, so a skip
  moved from `test_a` onto `test_b`, as a decorator or as a call to
  `pytest.skip` in the body, is a suppression added to `test_b`, while a test
  moved whole takes its marker with it and adds nothing. A test renamed takes
  its marker to a name that did not hold one, which reads as added, the side
  the check fails toward. `read_assertion_statements` takes its `where` from
  the same function rather than a scope walk of its own, which puts a
  decorator's assertion in the definition it decorates, as `read_assertions`
  already did.
- `_net_line_changes` reads a `diff --cc` section column by column and keeps
  each line's least count across the columns: added where no parent held it,
  removed where every parent did, which is `_file_steps`' reading of a merge.
  A quoted path is read as `""`, as an unread two-way header is, and a
  section is keyed as the file's two-way patches are so the fold runs across
  both. The two-way reader's own misreads stay `PL-MR8Z`'s.
- `sanctioned_queue_edit` answers no kind for a path with an uncommitted
  change, as an uncommitted capture or record already read, since every kind
  is read off a commit; the scope check names such a path as uncommitted.

`test_a_skip_decorator_moved_to_another_test_is_an_added_suppression` (both
shapes), `test_a_merge_commits_combined_diff_is_read_or_declined` and
`test_an_uncommitted_edit_beside_a_sanctioned_queue_write_is_not_sanctioned`
each fail on `main`'s code; `test_a_test_moved_whole_with_its_skip_adds_no_suppression`
and `test_a_statement_belongs_to_its_definition_and_a_decorator_to_the_one_it_decorates`
pin the other side.
