---
id: PL-1PBV
title: Three tools/ scripts still collapse a failed git call to empty output, the convention PL-9RFP removed from verify: pr_title_check passes a head it cannot read as closing no item, generator_check attributes no item when its log fails, and branch_id_check's walk keeps the route PL-73P0 patched only for an unresolved base
priority: P3
effort: S
status: done
classes: defect
feature: evidence-declines
touches: tools/pr_title_check.py, tools/generator_check.py, tools/branch_id_check.py, tests/unit/test_pr_title_check.py, tests/unit/test_generator_check.py, tests/unit/test_branch_id_check.py, .github/workflows/pr-title.yml, subprojects/docket/tests/test_cli.py
added: 2026-09-23
closed: 2026-09-23
payoff: the last three tools/ git readers say 'not checked' when git fails, instead of passing any pull request title, printing a spawn ratio of 0.00 nobody measured, or telling a branch it owes no id
verify: grep -q 'def test_a_head_git_cannot_read_is_not_a_branch_that_closes_nothing' tests/unit/test_pr_title_check.py && grep -q 'def test_a_history_git_cannot_read_leaves_the_ratio_unmeasured_rather_than_zero' tests/unit/test_generator_check.py && grep -q 'def test_a_walk_git_did_not_answer_declines_instead_of_owing_nothing' tests/unit/test_branch_id_check.py
---

**Problem.** Three tools/ scripts still collapse a failed git call to empty output, the convention PL-9RFP removed from verify: pr_title_check passes a head it cannot read as closing no item, generator_check attributes no item when its log fails, and branch_id_check's walk keeps the route PL-73P0 patched only for an unresolved base

**Found 2026-09-23, by asking where `PL-9RFP`'s extra findings came from.**
That item's brief named one read and its fix moved seven, plus
`doc_check._git`. It was the fourth fix in this feature in five days to find
more than its brief: `PL-Q9Z1`'s one-call-at-a-time sweep found nine reads in
breach where the design round had measured four, `PL-ZPDM`'s brief had the
release gate's direction backwards, and `PL-73P0`'s named the harmless of two
cases. Each fix swept the module in front of it, and nothing had swept across
modules. So this sweep read every place the tree shells out: 26 subprocess call
sites in 15 files. Three still carry the convention.

- **`tools/pr_title_check.py`.** `PR_TITLE="no id here" python3
  tools/pr_title_check.py --base a65b440c~1 --head a65b440c` fails and names
  `PL-9RFP`, which is the control. The same command with `--head no-such-head`
  prints `pr-title: this branch closes no item; no id is owed` and exits 0.
  `_git` returns `""` on any failure. Its docstring says the empty answer
  "still reads correctly at every call site: an unreadable tree closes
  nothing", which is the same claim `PL-9RFP` disproved for `verify`. An
  unreadable *base* fails loudly the other way, because every closed item then
  reads as this branch's. So the silent direction is an unreadable head, or
  both trees unreadable.
- **`tools/generator_check.py`.** `creation_parents` runs `git log` with no
  `check=` and never reads `returncode`. Against this repository it attributes
  1,561 items. Against a directory with no repository it attributes 0, and
  nothing is raised or printed. Every cluster's spawn column then reads zero,
  as if it had been measured.
- **`tools/branch_id_check.py`.** `_git` has the same convention. `main()`
  already refuses an unresolved base (`PL-73P0`), and its comment names the
  collapse. But a base that resolves, followed by a `log` walk that fails
  (the 30 s timeout, or a ref deleted between the two calls), still prints
  `nothing ahead of <base>; no id is owed` and exits 0. Found by reading the
  code, not reproduced.

**Reproduced again at triage, 2026-09-23.** The first two ran as written above.
The third can be reached by hand, not only through a race:
`python3 tools/branch_id_check.py --base no-such-ref` prints `branch-id: nothing
ahead of no-such-ref; no id is owed` and exits 0. `resolved` recognises a base
`default_base` guessed, and a base named on the command line is not a guess,
so it goes straight to the walk.

**Why it matters.** Each is a check or report that answers confidently on
evidence it never read, which is the shape of the whole `evidence-declines`
feature. All three triggers are narrow. CI checks out with `fetch-depth: 0`,
the title check reads `HEAD`, and `generator_check.py` runs only under `make
docket`, in a session's full clone. That last point is why this item is not
recorded as `impairs-generators:`, even though `tools/generator_check.py` is
on `generator_paths`: no run that happens today trips it. It would qualify the
moment the report runs anywhere git can fail, such as CI or a source tarball.
The value here is the feature's completeness. Once this item and `PL-19T3`
close, no git runner in the tree reads a failure as an answer.

**Out of scope on purpose, so the next sweep can skip them.**
`tools/pr_body_check.py` and `tools/main_ci_status.py` are advisories that
stay silent on failure by documented design. In `tools/open_pull_requests.py`,
`""` becomes `None` and every caller skips. These all carry a failure channel:
`tools/left_behind_check.py`, `tools/required_checks_check.py`,
`tools/ignore_check.py`, `.claude/hooks/stop_hook_patch.py`, the open-PR
lookup in `subprojects/docket/src/docket/cli.py`, and
`src/anesthesia_sim/app_metadata.py`. The last one documents its single
conflation, no git reading as the release build, as a decision. `vcs.py`
falls under `PL-Q9Z1`'s sweep except for `PL-19T3`. `verify.py` and
`doc_check.py` are `PL-9RFP`'s.

**Done when.** None of the three runners can mistake "git did not answer" for
an empty answer, and each script says it could not check instead of passing:
`pr_title_check` declines when either tree is unreadable, `generator_check`
says its spawn column went unmeasured, and `branch_id_check` says the walk was
not read. Each script gets a test that fails against the current source. A
tree-wide guard against the convention, extending `PL-9RFP`'s
`test_no_run_call_in_verify_discards_its_exit_status` past `verify.py`, would
be a new check. `CLAUDE.md` holds that back while any item carries
`generator: live`. The per-script tests are this fix's own regression tests,
not that guard.

**Generator check.** This is one instance of closed head `PL-9RFP`'s
mechanism: a git runner that answers a failed call with the empty string. It
was filed ten minutes after that head merged (`a65b440c` at 00:58 UTC, this
capture at 01:08). The head's `generator: spent` was true of the two runners it
named, `verify` and `doc_check`, and its fix did not reach these three. The
sweep that found them read all 26 subprocess call sites in the tree, so once
this item and `PL-19T3` close, no site is left to produce another.
