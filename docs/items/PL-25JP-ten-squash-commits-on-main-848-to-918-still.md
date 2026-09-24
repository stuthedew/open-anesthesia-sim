---
id: PL-25JP
title: Ten squash commits on main, #848 to #918, still carry no body: tools/pr_body_check.py --recover restores them and the session-start digest names them every session, but no item owns running it
priority: P2
effort: S
status: done
classes: housekeeping
feature: pr-body-integrity
touches: docs/pr-bodies, docs/items
added: 2026-09-23
closed: 2026-09-24
payoff: the ten lost commit bodies are kept in the tree, and the digest stops printing a warning every session has learned to skip
verify: grep -q '^pr: 848' docs/pr-bodies/848.md && grep -q '^pr: 849' docs/pr-bodies/849.md && grep -q '^pr: 886' docs/pr-bodies/886.md && grep -q '^pr: 887' docs/pr-bodies/887.md && grep -q '^pr: 910' docs/pr-bodies/910.md && grep -q '^pr: 911' docs/pr-bodies/911.md && grep -q '^pr: 912' docs/pr-bodies/912.md && grep -q '^pr: 913' docs/pr-bodies/913.md && grep -q '^pr: 916' docs/pr-bodies/916.md && grep -q '^pr: 918' docs/pr-bodies/918.md
---

**Problem.** Ten squash commits on main, #848 to #918, still carry no body: tools/pr_body_check.py --recover restores them and the session-start digest names them every session, but no item owns running it

**What triage found, 2026-09-24.** `python3 tools/pr_body_check.py` still
reports ten: `#848`, `#849`, `#886`, `#887`, `#910` to `#913`, `#916` and
`#918`. All ten bodies can still be fetched from GitHub, and none was edited
after its merge. `--recover` sends one unauthenticated GET per pull request and
writes `docs/pr-bodies/N.md`, and does nothing else: no git command, no push,
and nothing sent to GitHub. It skips any number that already has a file, so a
rerun is safe, and deleting the files undoes it. It has no dry-run flag.

**Why it matters.** The session-start digest prints this line in every session,
and no item owned clearing it. So it has become a warning every session reads
past, which is `CLAUDE.md`'s second compounding test. Until the files are
recovered, the reasoning behind each of the ten commits lives only on GitHub.

**Generator check.** Bookkeeping, not a new instance. All ten merged before
`PL-WFFX` closed: `#848` on 2026-09-21 through `#918` at 23:19Z on 2026-09-22,
against the close at 23:33Z. It is the same recovery `PL-BXNH` and `PL-F8Q7`
ran for earlier ones.
