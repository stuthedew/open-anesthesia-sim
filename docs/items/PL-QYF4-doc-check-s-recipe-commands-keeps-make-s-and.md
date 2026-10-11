---
id: PL-QYF4
title: doc_check's _recipe_commands keeps make's @, - and + recipe prefixes on the command it hands back, so check_ruff_cache never holds an @-led ruff check to a cache-free run, and check_coverage_gate reads an @-led coverage run as differing from CI's identical one; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
payoff: an @, - or + on a recipe line no longer switches off the ruff-cache check or invents a Makefile-versus-CI coverage difference
verify: grep -q 'def test_a_recipe_prefix_is_stripped_before_the_command_is_read' tests/unit/test_doc_check.py
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, under python3 3.11:
`_recipe_commands` still yields `@ruff check src`, `-ruff check src` and
`+ruff check src` as written, and `check_ruff_cache` over a scratch Makefile
gives one error for the bare line and none for `@`, `-`, `+` or `@-`. The
tracked Makefile's only prefixed recipe lines are still the two `@echo` lines
under `release`.

**Why it matters.** Both checks exist to hold the tracked gate to a fact - a
cache-free `ruff check`, one coverage command shared by the Makefile and CI -
and a prefix silences the first and invents a difference in the second. The
first `@` added to quiet a ruff line would switch the ruff-cache guarantee off
with nothing failing.

**Generator check.** Not a member of `PL-R417`: each recipe line is read whole;
the fault is the prefix left on it. Read against `bin/docket generators
--misread` on 2026-10-11: the fact is which command make hands the shell from a
recipe line, a rule of make's that no head's `misread:` states; `PL-61FT`'s
nearest fact is about a shell command once it runs. No other reader here
strips the prefixes, so there is no second spelling to hold it to. A one-off.

**Done when.** `_recipe_commands` strips make's recipe prefixes, any mix of the
three, before yielding a command, pinned by a test for each prefix through
`check_ruff_cache` and one through `check_coverage_gate`.
