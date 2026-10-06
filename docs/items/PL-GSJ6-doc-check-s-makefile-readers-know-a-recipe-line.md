---
id: PL-GSJ6
title: doc_check's Makefile readers know a recipe line only by its tab, where make 4.3 reads one by .RECIPEPREFIX once a Makefile sets it, so every recipe in such a Makefile reads as missing and a documented target as exiting 0 without running; latent
status: untriaged
touches: docs/items/PL-GZXY-doc-check-s-make-readers-read-only-the-first.md
added: 2026-10-06
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
