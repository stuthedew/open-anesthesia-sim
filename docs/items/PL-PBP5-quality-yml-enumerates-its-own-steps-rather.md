---
id: PL-PBP5
title: quality.yml enumerates its own steps rather than running make check, so dead_ends.py, ignore_check.py and possessive_section_check.py have no CI backstop and a branch pushed without a local make check lands green on a tree make check would refuse
priority: P2
effort: M
status: done
classes: defect, infra
touches: .github/workflows/quality.yml, Makefile, tools/doc_check.py, tests/unit/test_doc_check.py, docs/ARCHITECTURE.md, docs/items/
added: 2026-09-21
closed: 2026-09-21
pr: 882
payoff: a check wired into make check is enforced by CI too, so the convention it holds does not depend on a session remembering to run the local gate
verify: grep -q 'def check_gate_parity' tools/doc_check.py && grep -q 'tools/dead_ends.py check' .github/workflows/quality.yml
---

**Problem.** quality.yml enumerates its own steps rather than running make check, so dead_ends.py, ignore_check.py and possessive_section_check.py have no CI backstop and a branch pushed without a local make check lands green on a tree make check would refuse

**Found while closing `PL-316G`** (the possessive-to-section-mark conversion),
whose step 2 wires `tools/possessive_section_check.py` into `make check` so
"the convention holds for citations nobody has written yet". The wiring does
what the item asked. What it does not do is what the item's own reasoning
assumes: `.github/workflows/quality.yml` enumerates its own steps rather than
invoking `make check`, so three of that target's lines run nowhere else -
`tools/dead_ends.py check`, `tools/ignore_check.py` and now
`tools/possessive_section_check.py`. A branch pushed without a local
`make check` gets a green CI verdict on a tree `make check` would refuse.

**Why it matters.** The project's standing argument for a check is that a
convention nothing enforces decays. A check that runs only where a session
remembers to run it is enforced by the same memory the convention was, which
is the property the check was built to replace. `make check` is the required
pre-commit gate, so this is a second line of defence rather than the only one
- which is why it is filed rather than fixed inside `PL-316G`.

**Two of the three predate this.** `ignore_check.py` and `dead_ends.py` have
been `make check`-only for longer than `possessive_section_check.py` has
existed, and nobody has filed it, so *deliberate* is a live reading and has to
be ruled out before anything is added. `pr_title_check.py` is the worked
counter-example: it is `make check`-only in `quality.yml` and has a workflow of
its own in `.github/workflows/pr-title.yml`, so the project has already decided
this question once, in the direction of covering it.

**What the answer has to weigh.**

- Whether each of the three is cheap enough for the floor section, which runs
  before `astral-sh/setup-uv` and whose whole design is that no virtualenv
  exists yet. `dead_ends.py` and `possessive_section_check.py` are
  standard-library-only and read text, so both qualify; `ignore_check.py`
  shells out to mypy and does not, which is why it sits under `uv run` in the
  Makefile and is the one genuine split in the group.
- What the counterfactual is worth, per
  `.claude/rules/expert-review.md` § "Name the number that would change your
  mind, then go and count it": this is worth adding only if pushes that skip
  `make check` are a real rate rather than a hypothetical. Count them before
  deciding - a CI run whose tree fails one of the three is the observable, and
  `git log` plus the run history can say how often it has happened.
- Whether the answer is instead to make the two gates one, so the question
  cannot recur per tool. `PL-J3WK` is the same seam from the other side -
  `make check` runs `bin/docket check` without `--verify` where CI runs it with
  - and whichever way that one goes should decide this one too.

**Done when.** The three are either covered by CI or recorded as deliberately
local with the reason, and whatever decides it is written where the next tool
added to `make check` will meet the question rather than re-derive it.

## Answered 2026-09-21

**`PL-J3WK` decided it, as this brief said it should, and the answer is that
the two gates stay two.** That item took the *statically decidable* half of
`--verify` into the bare `bin/docket check` and left the replay where it was,
on the argument that the expensive tier has nothing to add to a question the
store already answers. The same argument rules out making CI run `make check`
here, and for a reason this brief did not have: `quality.yml`'s floor section
runs the standard-library tools under the 3.11 floor **before** `uv` exists,
which is what proves they need no virtualenv, and `make check` opens by
creating one. The local gate is also legitimately stricter in a place nobody
had noticed - `uv run ruff check --no-cache .` against CI's plain `ruff check`,
which `check_ruff_cache` already holds it to deliberately.

So the two lists are not merged. What changes is that **the difference stops
being invisible**: `check_gate_parity` in `tools/doc_check.py` reconciles the
set of this project's own scripts each gate runs, in both directions, and
refuses every asymmetry not recorded in `GATE_ONLY` with its reason. Scripts
rather than command strings, because how a script is invoked differs by
construction - `python3 tools/x.py` at the floor, `uv run python tools/x.py`
after the sync - so comparing strings would report every line as a drift. Only
workflows triggered by `pull_request` count as the merge gate, which is what
makes `tools/pr_title_check.py` the worked counter-example this brief named
rather than a fourth finding: it is `make check`-only within `quality.yml` and
has `pr-title.yml` of its own.

**The three, decided one at a time on what they cost.** All three are covered;
none is recorded as deliberately local.

| script | where | measured |
| --- | --- | --- |
| `tools/dead_ends.py check` | floor section | 0.07 s, standard library, reads two files |
| `tools/possessive_section_check.py` | floor section, beside `doc_check` | 1.6 s, standard library, reads Markdown |
| `tools/ignore_check.py` | after `uv run mypy` | 9.2 s there against 27.3 s cold |

`ignore_check.py` is the one genuine split this brief predicted: it shells out
to mypy, so it cannot go in the floor section. Placing it immediately after the
`uv run mypy` step is what makes it affordable - that run has already put
everything the excluded trees import into `.mypy_cache`, and the difference is
27.3 s against 9.2 s measured on this tree. `GATE_ONLY` ends up holding exactly
one entry, `tools/required_checks_check.py`, whose answer is not in the tree at
all.

**The count this brief asked for, and it came back a real rate.** Over the 100
most recent completed `pull_request` runs of `quality.yml` - 2026-09-21 01:06Z
to 20:57Z, 74 green, 15 cancelled by the workflow's own concurrency, 11 red -
**5 of the 11 failures were at a step `make check` also runs**, and 6 were the
`--verify` replay, which is `PL-J3WK`'s territory. Read strictly the figure is
4 rather than 5: one of the five is `doc_check.py` crashing on an absolute path
outside the repository, which is `PL-H0CF` rather than a tree the local gate
would have refused. Either way branches do reach CI carrying trees `make check`
would refuse, at roughly one pull-request run in twenty, so the backstop is
worth its 11 s. Not one of the five was `ruff`, `mypy` or `pytest`: the
code-quality half of the local gate caught everything before CI in that window
and the documentation and store half did not, which is the half the three
uncovered scripts belong to.

**Done when** is met: the three are covered, the one deliberate asymmetry is
recorded with its reason, and the decision is enforced by a check that fires
the moment a line is added to `check:` - with a note beside the target's first
`tools/` line saying so, for the session that has not run the gate yet.

