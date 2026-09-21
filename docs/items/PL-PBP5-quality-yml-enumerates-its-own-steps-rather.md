---
id: PL-PBP5
title: quality.yml enumerates its own steps rather than running make check, so dead_ends.py, ignore_check.py and possessive_section_check.py have no CI backstop and a branch pushed without a local make check lands green on a tree make check would refuse
priority: P3
effort: S
status: needs-decision
classes: infra
feature: check-parity
touches: .github/, Makefile, tools/, docs/items/
added: 2026-09-21
payoff: a check wired into make check is enforced by CI too, so the convention it holds does not depend on a session remembering to run the local gate
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

**Decision needed.** Whether the three `make check`-only tools get a CI
backstop, and whether that is settled per tool or by closing the seam so the
question cannot recur with the next tool added. `PL-J3WK` is the same seam from
the other side - `make check` runs `bin/docket check` without `--verify` where
CI runs it with - and should be answered in the same sitting.

**`PL-J3WK` has since gone one way, and it is a precedent rather than an
answer** (read 2026-09-21 from `origin/claude/trusting-hawking-wlh7vg`, where
it is closed `done` and its pull request not yet open; `origin/main` still
carries it `ready`). It closed the seam by moving the statically decidable half
of `--verify` - the no-op command and the command two items share - into bare
`bin/docket check`, so both gates run it. It touched neither `Makefile` nor
`.github/workflows/quality.yml`. So the project's answer to "make the two gates
one" was *no*: it moved the check to where both gates already look instead.
That is available here for `dead_ends.py` and `possessive_section_check.py`
only by the opposite move - putting them in CI as well - because unlike
`docket check` they are not invoked by CI at all. The precedent to take from it
is the shape: prefer a check that runs in both places over reconciling what
each gate enumerates.

**Recommended: count first, then take the cheap half.** Run the count the
section above asks for, because whether pushes that skip `make check` are a
real rate is what decides whether anything is worth adding at all. Whatever it
says, `dead_ends.py` and `possessive_section_check.py` are standard-library-only
and read text, so they belong in `quality.yml`'s floor section beside the checks
already there - a two-line change that keeps the floor's no-virtualenv
guarantee. `ignore_check.py` shells out to mypy and is the one genuine split:
leave it under `uv run` and record that as deliberate with the reason, rather
than bending the floor section to accommodate it. Recording the split is the
half that stops this recurring, so it is not optional even if the count says
add nothing.

**Done when.** The three are either covered by CI or recorded as deliberately
local with the reason, and whatever decides it is written where the next tool
added to `make check` will meet the question rather than re-derive it.
