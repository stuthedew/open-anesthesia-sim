---
id: PL-5M36
title: doc_check's gate-parity, Makefile and workflow readers misread six forms beside where a statement ends - check_gate_parity reports a difference after declining a line, make_targets counts a tab-only recipe line and keeps an escape's backslash, _make_mentions reads a block-quoted fence with its markers, _run_script reads an invalid literal block's first lines silently, and a pyproject.toml that is not TOML aborts the run - and _git has no caller; latent
priority: P3
effort: M
status: done
classes: defect
milestone: v0.5.24
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1436
payoff: doc_check stops reporting a gate difference it could not read and stops aborting on a malformed pyproject.toml, so its Makefile, fence and workflow answers hold for the forms make, bash and YAML accept
verify: grep -q 'def test_gate_parity_reports_no_difference_once_a_make_check_line_is_declined' tests/unit/test_doc_check.py && grep -q 'def test_a_tab_only_line_under_a_rule_is_no_recipe' tests/unit/test_doc_check.py && grep -q 'def test_a_pyproject_that_is_not_toml_is_reported_not_raised' tests/unit/test_doc_check.py && ! grep -q 'def _git(' tools/doc_check.py
---

**Problem.** doc_check's gate-parity, Makefile and workflow readers misread six forms beside where a statement ends - check_gate_parity reports a difference after declining a line, make_targets counts a tab-only recipe line and keeps an escape's backslash, _make_mentions reads a block-quoted fence with its markers, _run_script reads an invalid literal block's first lines silently, and a pyproject.toml that is not TOML aborts the run - and _git has no caller; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`tools/doc_check.py`.

- `check_gate_parity` goes on after `_shell_reading` declines a line, since
  only declined steps go on `steps`, and reports that a workflow runs no
  equivalent of a Makefile gate it could not read - against its own comment
  that a difference would then not be a fact.
- `make_targets` counts a tab-only line as a recipe, where make 4.3 runs
  nothing (the target is up to date), and `_target_recipes` drops the same
  line; it also reads a target written with an escaped colon with both
  backslashes, where make's database shows one.
- `_make_mentions` reads a fence inside a block quote with its `>` markers,
  so a `make` target named in it is not found, and reports a `make` inside a
  multi-line `$( )` on the line the substitution opens.
- `_run_script` reads a literal block holding a line less indented than its
  content but deeper than its key as its first lines only, where PyYAML
  refuses the workflow.
- `_check_tag_version_files` reaches `version_in`, which raises an uncaught
  `TOMLDecodeError` when the working tree's `pyproject.toml` is not TOML.
- `_git` has no caller.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against GNU make 4.3, bash 5.2.21 and PyYAML 6.0.3. Latent: no
Makefile line, fence, workflow or `pyproject.toml` in the tree holds these
forms.

**Re-confirmed 2026-10-11** on main at `16a20a4f`, under python3 3.13.16 and
PyYAML in the project environment: a `check:` recipe whose second line holds
an unclosed quote is declined and the run still errors that the workflow runs
`tools/b.py` and `make check` does not; `check:` over a tab-only line gives
`make_targets` `check` with a recipe and `_target_recipes` none; `a\:b:` is
read as `a\:b`; a block-quoted fence yields no mention; a `make` on the third
line of a fence, inside a `$(` opened on the second, is reported at the second;
a literal block with a line one column short of its content reads only
`echo a` where PyYAML raises `ParserError`; a `pyproject.toml` of
`not = = toml` raises `TOMLDecodeError` out of `_check_tag_version_files`; and
`doc_check._git` has no caller in `tools/` or `tests/`.

**Why it matters.** Each is a check answering past what it read: gate parity
reports as a fact a difference its own comment says is not one, two Makefile
readers disagree about one tab-only line, a `make` command in a block quote
is never held to a target, and a malformed `pyproject.toml` takes down the
whole `doc_check` run instead of declining one check. Latent today, but each
is the floor's violation the day a file is written that way.

**Generator check.** Not members of `PL-R417`: each reads its statement whole
and misjudges something else.

**Generator check, added at triage 2026-10-11.** The first bullet, gate parity
reporting a difference it could not read, is an instance of `PL-0HPV`'s fact -
the checks the local gate and the merge gate each run, and where the two sets
differ - filed after that head closed (2026-09-22, `spent`), after `PL-RW3T`,
`PL-ZXM1` and `PL-HSB3`; the triage pass reported that count rather than
recording a head. The other five forms are one-offs.

**Done when.** Each form is read as make, bash and YAML read it, or declined
by name; the TOML error is reported, not raised; `_git` is removed; a test
pins each form.
