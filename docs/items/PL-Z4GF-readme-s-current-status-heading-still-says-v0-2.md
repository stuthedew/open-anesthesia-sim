---
id: PL-Z4GF
title: README's Current status heading still says v0.2.3 while the shipped version is v0.2.4
priority: P3
effort: S
status: done
classes: docs
milestone: v0.2.5
touches: README.md
added: 2026-08-25
closed: 2026-08-25
commit: d40ff83
pr: 47
---

**Problem.** README's Current status heading still says v0.2.3 while the shipped version is v0.2.4

**Why it matters.** The README is the first thing a reader meets, and a stated
version that disagrees with `pyproject.toml` is the kind of small wrongness
that makes a reader distrust the rest. It will recur at every release unless
the heading stops naming a version, so prefer removing the number over
correcting it - `ROADMAP.md` already carries version history.

**Where.** `README.md`'s "Current status" heading.

**Done when.** The README no longer states a version that can go stale.

**Where.**

**Done when.**
