---
id: PL-TN18
title: Split the effort trial 50/50 between high and xhigh instead of 1 in 4 xhigh, so it reaches the same statistical power with about a quarter fewer sessions
status: done
feature: model-evidence
touches: tools/effort_trial.py, tests/unit/test_effort_trial.py, docs/maintainer.md, docs/apparatus.md, docs/items/PL-63CB-add-a-model-review-skill-that-on-a-cadence-and.md
added: 2026-10-24
closed: 2026-10-24
pr: 1756
payoff: the effort trial answers whether high causes more rework than xhigh after about a quarter fewer sessions
verify: grep -q '% 2 == 0' tools/effort_trial.py
---

**Problem.** The effort trial puts about one cloud session in four in the
`xhigh` arm and the rest in `high` (`PL-HYRM`). For a fixed number of
sessions, an unequal split detects a difference less reliably than an equal
one. With a ratio of r to 1, the number of sessions needed for the same power
grows by a factor of (r+1)²/4r. At r = 3 that factor is 16/12, so the 3:1
split needs about 33% more sessions than a 50/50 split. Put the other way, a
50/50 split needs about a quarter fewer.

**What prompted it.** The owner noticed on 2026-10-24 that new sessions kept
reporting the `high` arm. That was chance under the 1-in-4 design: on 100,000
random ids the hash gave `xhigh` 25.1% of the time, and four `high` sessions
in a row happen 32% of the time.

**Decision (project owner, 2026-10-24, ratified, over keeping 1 in 4 to spend
less of the usage allowance on `xhigh`).** Split the trial 50/50. A session is
in the `xhigh` arm when the SHA-256 digest of its session id, read as a whole
number, is even.

**What happens to sessions already in the trial.** A digest divisible by 4 is
also even, so every session already in the `xhigh` arm stays there. A digest
that leaves 2 when divided by 4 was `high` and becomes `xhigh`. Such a session
prints the new arm only if it resumes or compacts on a checkout with this
change. `PL-63CB` already takes each session's first arm line and counts the
sessions whose later lines differ, so the analysis handles them. Because the
allocation probability changed partway through, the analysis also treats the
period before and after this change as a stratum.

**Done when** `tools/effort_trial.py` assigns `xhigh` to an even digest, its
test checks that about half of a fixed set of ids is `xhigh`, and
`docs/maintainer.md`, `docs/apparatus.md` and `PL-63CB` state the 50/50 split
and when it began.

**Generator check.** Not a generator. The owner changed one parameter of an
existing mechanism, and nothing in the change causes further items.
