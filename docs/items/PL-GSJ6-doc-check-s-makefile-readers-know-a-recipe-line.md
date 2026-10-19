---
id: PL-GSJ6
title: doc_check's Makefile readers know a recipe line only by its tab, where make 4.3 reads one by .RECIPEPREFIX once a Makefile sets it, so every recipe in such a Makefile reads as missing and a documented target as exiting 0 without running; latent
priority: P3
effort: S
status: done
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py, tests/unit/test_makefile_reference.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
closed: 2026-10-19
pr: 1620
payoff: a Makefile that sets .RECIPEPREFIX stops reading as having no recipes, so a documented target is not reported as exiting 0 without running
verify: grep -q 'def test_a_makefile_that_sets_recipeprefix' tests/unit/test_doc_check.py
---

**Problem.** doc_check's Makefile readers know a recipe line only by its tab, where make 4.3 reads one by .RECIPEPREFIX once a Makefile sets it, so every recipe in such a Makefile reads as missing and a documented target as exiting 0 without running; latent

**Found 2026-10-06 building `PL-TDVJ` and `PL-BMZN`** (`#1384`), reading
`eval` in GNU make 4.3's `src/read.c`, which tests a line's first character
against `cmd_prefix`: a tab until a Makefile assigns `.RECIPEPREFIX`.
`_make_lines`, and every reader it serves, tests for a tab.

**Reproduced 2026-10-06** under python3 3.11.15: a Makefile of
`.RECIPEPREFIX = >`, `check:` and `>@echo ran` gives `make_targets` `check`
with no recipe and `_recipe_commands` no command, where GNU Make 4.3 runs
`make check` and prints `ran`.

**Re-confirmed 2026-10-11** on main at `16a20a4f`, under python3 3.13.16 and
GNU Make 4.3: the same Makefile gives `make_targets` `check` with no recipe
and `_recipe_commands` nothing, and `make -f` on it prints `ran` and exits 0.
`check_gate_parity` then reads an empty `check` recipe and returns without a
decline, so the parity check is silent rather than wrong there.

**Why it matters.** In a Makefile that sets the prefix every recipe reads as
missing, so `check_make_targets` tells a document naming any target that it
exits 0 without running, and the coverage gate and ruff cache checks compare
no command. Latent: the Makefile sets no prefix.

**Generator check.** A one-off: which character opens a recipe line, a fact no
other reader here holds. Not a member of `PL-R417`, since nothing here
continues across lines. `docket new` matched it to `PL-GZXY` by a shared path,
which is not the same fact, so that recurrence is withdrawn naming this brief.

**Done when.** The Makefile readers read a recipe line by the prefix make 4.3
uses at that line, `.RECIPEPREFIX` included, or decline by name a Makefile that
assigns it; a test pins whichever is built.

**Done 2026-10-19.** Declined by name rather than read by the prefix. A
recipe prefix changes which character opens a recipe line from the assignment
on, and porting that reading would change every reader of `_make_lines` for a
Makefile this repository does not have. `_make_lines` now refuses the line that
assigns `.RECIPEPREFIX`, after any of `export`, `override` and `private`, or a
`define` of it, through `MAKE_RECIPEPREFIX_RE`. Each Makefile check then
reports that line as unread instead of reading every recipe as missing. A
reference such as `$(.RECIPEPREFIX)` is still read. Regression:
`uv run pytest -q tests/unit/test_doc_check.py -k recipeprefix` against the
code before the fix fails 6 of 7, the first with
"assert [('.RECIPEPRE...echo ran', 3)] == (1, 'this lin...y by its tab')".
