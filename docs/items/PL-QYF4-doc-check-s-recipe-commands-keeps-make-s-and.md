---
id: PL-QYF4
title: doc_check's _recipe_commands keeps make's @, - and + recipe prefixes on the command it hands back, so check_ruff_cache never holds an @-led ruff check to a cache-free run, and check_coverage_gate reads an @-led coverage run as differing from CI's identical one; latent
status: untriaged
added: 2026-10-06
---

**Problem.** doc_check's _recipe_commands keeps make's @, - and + recipe prefixes on the command it hands back, so check_ruff_cache never holds an @-led ruff check to a cache-free run, and check_coverage_gate reads an @-led coverage run as differing from CI's identical one; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`tools/doc_check.py`. `_recipe_commands` yields each recipe line stripped of
whitespace and nothing else. GNU make removes a leading `@` (manual § 5.2), `-`
(§ 5.5) or `+` (§ 9.3) before handing the line to the shell, so the command
that runs is the rest of the line. `check_ruff_cache` holds every `ruff check`
the Makefile runs to a cache-free invocation, and `check_coverage_gate` holds
the Makefile's coverage run and CI's to one command; both read
`_recipe_commands`.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against GNU make 4.3, with a scratch Makefile whose `check` recipe is one line:
`ruff check src` gave `check_ruff_cache` one error, and the same line led by
`@` or by `-` gave none, where `make -n` shows the same `ruff check src` for
all three. A copy of the tracked Makefile and workflows with the coverage run's
line led by `@` gave `check_coverage_gate` the error that the Makefile and CI
differ, where the unprefixed copy passes. Latent: the tracked Makefile prefixes
only two `echo` lines.

**Generator check.** Not a member of `PL-R417`: each recipe line is read whole;
the fault is the prefix left on it.

**Done when.** `_recipe_commands` strips make's recipe prefixes, any mix of the
three, before yielding a command, pinned by a test for each prefix through
`check_ruff_cache` and one through `check_coverage_gate`.
