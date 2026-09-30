---
id: PL-2H0K
title: Measure how often a session's clone is shallow: since_filed and merged_pull_requests both decline there, vcs.py's merged_pull_requests docstring says agent containers normally are, yet PL-TQN2's web session on 2026-09-23 was a full clone of 1,301 commits, and create_session documents a default clone_depth of 50
priority: P3
effort: S
status: ready
classes: docs
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, .claude/hooks/stop_hook_patch.py, docs/ARCHITECTURE.md, tools/doc_check.py
added: 2026-09-23
payoff: a reader designing a git fallback is told which clone a session actually has
verify: ! grep -qF 'is normally shallow' subprojects/docket/src/docket/vcs.py
---

**Problem.** Measure how often a session's clone is shallow: since_filed and merged_pull_requests both decline there, vcs.py's merged_pull_requests docstring says agent containers normally are, yet PL-TQN2's web session on 2026-09-23 was a full clone of 1,301 commits, and create_session documents a default clone_depth of 50

**Measured at triage, 2026-09-24, in this session's container.** `git
rev-parse --is-shallow-repository` prints `false`, and `git rev-list --count
HEAD` prints 1,319. The `origin/main` reflog shows why:

1. `fetch --no-progress --depth 50 origin main`, when the container was
   provisioned.
2. `fetch --quiet --unshallow origin`, 14 seconds after the session started.

The second fetch comes from `.claude/hooks/docket-digest.sh`, which unshallows
a shallow clone at session start, is capped at 60 seconds, and fails silently.
So a container is provisioned shallow at depth 50, and everything a session
runs sees a full clone unless that fetch failed. `PL-TQN2`'s 1,301 commits were
the ordinary case, not an exception. One container is one data point, but what
the docstrings get wrong is the mechanism, not a rate. A second container, on
2026-09-30, belonged to a session spawned through `create_session`. It showed
the same two entries and 1,553 commits (`PL-KKX4`).

**Why it matters.** `merged_pull_requests`' docstring says a session's
container "is normally shallow, so that is the common case", and five more
sites in `vcs.py` and `checks.py` reason from it. Other places are wrong in the
same way:

- `.claude/hooks/stop_hook_patch.py` and `docs/ARCHITECTURE.md` say the
  harness clones with `git clone --depth 1`, where 50 was observed. `cli.py`
  said `--depth 1` too, until #1056 removed it on 2026-09-25.
- `tools/doc_check.py` says `actions/checkout` clones shallow, but every
  workflow here sets `fetch-depth: 0`.

A reader designing a fallback is told that the wrong case is the common one.

**Done when.** Those assertions say what was measured: the container is
provisioned at depth 50, the session-start hook unshallows it, and it stays
shallow only where that fetch failed. None of them says `--depth 1`, or that
the workflows' checkout is shallow.

**Generator check, revised 2026-09-30.** Triage judged this a one-off: a fact
about the environment written down without being measured. It is not one. The
`--depth 1` statements were written in #419 and #496, by sessions that had
started with no checkout and cloned by hand at depth 1 after `add_repo`
(`PL-KX9N`, `PL-3SGR`, `PL-483K`). That is `PL-KKX4`'s mechanism. `PL-KKX4`
now lists this item among its members, as a spent generator, because the
harness clones those sessions itself. `vcs.py`'s "normally shallow" is older
(2026-08-30), and nobody traced it to that mechanism.
