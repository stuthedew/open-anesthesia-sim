---
id: PL-FX3N
title: make test runs the suite serially while make check runs it at -n auto, so the target a session uses while iterating is the slow one
status: untriaged
added: 2026-09-04
---

**Problem.** `PL-WCZV` put `-n auto` on `make check`'s `pytest` line and on the
CI step. `make test` - "pytest only, without the coverage gate", the target a
session runs while iterating - was left bare, so it still runs serially. On a
four-core box that is roughly 78 s against 27 s for the same tests.

**Why it matters.** The slow one is the one a session reaches for most, so the
saving is missed exactly where iteration cost is felt. It is also a third place
the flag has to agree with the other two, which is the invariant `PL-D3M2`
already says nothing holds.

**Why it was left rather than fixed.** `PL-KCQ7`'s session added it, then
dropped the edit when `PL-WCZV` turned out to have landed on `main` in parallel:
`make test` was outside what the owner approved, and quietly widening a branch
that had just collided was the wrong move twice over.

**Not automatic.** The `check`-target reasoning does not transfer unexamined -
`-n` interleaves output and defeats `-x` and `pdb`, which is part of what
`make test` is for. Consider whether the answer is `-n auto` on the target, a
`make test-fast`, or leaving it and saying why in the target's comment.

**Where.** `Makefile`'s `test` target; `README.md`'s target listing if the
answer changes what it does.

**Done when.** `make test` either runs across cores or carries a comment saying
why it deliberately does not.
