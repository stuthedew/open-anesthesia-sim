---
id: PL-X43T
title: doc_check's _recipe_commands reads each recipe line as its own command where .ONESHELL hands the whole recipe to one shell, so a here-document body line in a recipe reads as a ruff run without --no-cache, and the coverage gate and the ruff cache check judge a command make never runs; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** doc_check's _recipe_commands reads each recipe line as its own command where .ONESHELL hands the whole recipe to one shell, so a here-document body line in a recipe reads as a ruff run without --no-cache, and the coverage gate and the ruff cache check judge a command make never runs; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
second half of `tools/doc_check.py`. `_recipe_commands` feeds
`check_ruff_cache` and `check_coverage_gate`, and reads each logical recipe
line as one shell invocation, which is what GNU make 4.3 does by default. Under
the special target `.ONESHELL` make hands the whole recipe to one shell (§ 5.3.1
of its manual), so a here-document body (POSIX § 2.7.4) continues across recipe
lines.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against GNU make 4.3 with a stub `ruff` on `PATH`. `TAB` marks a tab:

```text
.ONESHELL:
check:
TABcat <<'EOF' > notes.txt
TABruff check src
TABEOF
TABuv run ruff check --no-cache src
```

`_recipe_commands` read four commands, and `check_ruff_cache` reported line 4
running `ruff check src` without `--no-cache`, declining nothing. make ran only
`ruff check --no-cache src`, and `notes.txt` held the line `ruff check src`.
Latent: the repository's Makefile sets no `.ONESHELL`.

**Generator check.** A member of `PL-R417`: a reader takes each recipe line for
a statement where `.ONESHELL` makes the recipe one script. `PL-G2FY`, a member,
read recipe lines without `.ONESHELL`; `PL-GSJ6` (`.RECIPEPREFIX`) is a
construct of its own.

**Done when.** Under `.ONESHELL`, `_recipe_commands` reads the joined recipe
through `docket.shell.script_lines`, as `workflow_commands` reads a `run: |`
block, or declines the special target by name so each check says what it left
unread, pinned by a `recipe commands, ` case in `PL-R417`'s guard that fails on
today's reader.
