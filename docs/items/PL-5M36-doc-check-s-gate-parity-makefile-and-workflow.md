---
id: PL-5M36
title: doc_check's gate-parity, Makefile and workflow readers misread six forms beside where a statement ends - check_gate_parity reports a difference after declining a line, make_targets counts a tab-only recipe line and keeps an escape's backslash, _make_mentions reads a block-quoted fence with its markers, _run_script reads an invalid literal block's first lines silently, and a pyproject.toml that is not TOML aborts the run - and _git has no caller; latent
status: untriaged
added: 2026-10-10
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

**Generator check.** Not members of `PL-R417`: each reads its statement whole
and misjudges something else.

**Done when.** Each form is read as make, bash and YAML read it, or declined
by name; the TOML error is reported, not raised; `_git` is removed; a test
pins each form.
