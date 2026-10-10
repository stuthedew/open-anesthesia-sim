---
id: PL-X43T
title: doc_check's _recipe_commands reads each recipe line as its own command where .ONESHELL hands the whole recipe to one shell, so a here-document body line in a recipe reads as a ruff run without --no-cache, and the coverage gate and the ruff cache check judge a command make never runs; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1390
payoff: a Makefile setting .ONESHELL is declined by name rather than read a recipe line at a time, so the ruff cache and coverage checks never judge a here-document line as a command make runs
verify: grep -qF '"recipe commands, a .ONESHELL recipe is refused by name"' tests/unit/test_doc_check.py
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

**Reproduced 2026-10-10 at triage** on this branch at `b6b9c382`, whose readers are `main`'s at `fe2e5132`: `_recipe_commands` read the
brief's Makefile as four commands, `cat <<'EOF' > notes.txt`, `ruff check src`,
`EOF` and `uv run ruff check --no-cache src`.

**Why it matters.** `check_ruff_cache` and `check_coverage_gate` judge the
commands `_recipe_commands` hands them, so under `.ONESHELL` a here-document's
body line is judged as a command make runs: a `ruff check` written in one fails
the gate for a command make never runs, and a coverage line in one is compared
with CI's as if make ran it. The build declines the special target by name, the
cheaper of the two endings the Done-when allows while no Makefile here sets it,
and the answer `PL-R417` has given each form nobody writes.

**Generator check.** A member of `PL-R417`: a reader takes each recipe line for
a statement where `.ONESHELL` makes the recipe one script. `PL-G2FY`, a member,
read recipe lines without `.ONESHELL`; `PL-GSJ6` (`.RECIPEPREFIX`) is a
construct of its own.

**Done when.** Under `.ONESHELL`, `_recipe_commands` reads the joined recipe
through `docket.shell.script_lines`, as `workflow_commands` reads a `run: |`
block, or declines the special target by name so each check says what it left
unread, pinned by a `recipe commands, ` case in `PL-R417`'s guard that fails on
today's reader.

**Built 2026-10-10 (`#1390`).** The Done-when's second branch, as triage chose:
`_recipe_statements` raises `UnreadStatement` naming `.ONESHELL` before any
recipe is read, wherever in the Makefile the special target is named, since GNU
make 4.3 applies it named after the rule it changes or beside another target
(`.PHONY .ONESHELL: check`), so each check says what it left unread. Both
recipe readers take it: `_recipe_commands`, which the Done-when names, and
`_target_recipes`, which reads the same recipes for the targets' own checks and
would have judged the same body lines. The `recipe commands, a .ONESHELL recipe
is refused by name` case pins it, failing on `main`'s reader, which read the
brief's Makefile as four commands. No Makefile here names `.ONESHELL`.
