---
id: PL-5TN8
title: Two core-guard-coverage items will each add a ~50 s full-suite --cov command to every make check when triaged
status: untriaged
added: 2026-09-02
---

**Problem.** `PL-NC2P` and `PL-YMY7` are open, `ready`, in
`core-guard-coverage`, and carry no `verify:` command yet. Every coverage item
in that feature has taken the shape `uv run pytest --cov=<module>
--cov-fail-under=100`, which is a full-suite run measured at ~50 s. Giving
those two the same shape puts two ~50 s commands into the set `bin/docket
check` executes on every `make check`.

**Why it matters.** `PL-LXR3` made that set run concurrently, which took
`bin/docket check` from 34.9 s to 10.1 s. A pool cannot go faster than its
slowest member, so two ~50 s commands would take the figure to roughly 50 s -
better than the ~140 s it would have been serially, but still five times where
it stands, and arriving in a single triage pass rather than gradually. The
shape of the cost has changed with concurrency: it is now set by the slowest
command rather than by the number of them, so one heavy command is worth more
attention than twenty light ones.

Recorded while resolving `PL-LXR3`'s merge, where the risk was raised by a
parallel triage branch and only partly closed: concurrency reduced it, and
nothing prevents it.

**Where.** `docs/items/` - the two named items' `verify:` fields when they are
triaged; `subprojects/docket/src/docket/verify.py` if the answer turns out to
be a rule rather than a per-item choice.

**Worth deciding first.** Whether the answer is per-item or structural. A
coverage item's command is a full-suite run *by necessity* - coverage of a
module is the union of everything that exercises it, which is why
`.claude/skills/docket/SKILL.md` prescribes that shape and warns against
scoping it to one file. So narrowing these two the way ordinary commands are
narrowed is not available, and the options are different in kind: accept the
~50 s floor; exclude `--cov` commands from the landed check and record why;
or give the landed check a cheaper proxy for a coverage item. The last is the
one that would need designing.

**Done when.** Either the two items are triaged with commands whose cost is
known and accepted, or `bin/docket check` no longer pays full-suite coverage
runs for open coverage items, with the reasoning recorded either way.
