---
id: PL-3D2M
title: A pull request merged at a stale head silently drops later commits on the same branch, and nothing outside the item store notices
status: needs-decision
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py
added: 2026-09-04
priority: P2
effort: M
classes: defect, infra
---

**Problem.** A pull request can be merged at a head older than the branch's
current tip. GitHub squashes what it knew about, deletes nothing, and leaves the
branch ref pointing at the newer commit - so the branch looks merged, the pull
request reads merged, and the later commit is simply gone from `main` with
nothing saying so.

**Observed 2026-09-04.** #284 merged at `dc03044` while
`origin/claude/triage-n7hzpe` stood at `9fee36c`. The dropped commit carried a
`CLAUDE.md`-mandated behavior change - a rule the project owner had asked for in
that session - plus `PL-ZSV6` and a status correction to `PL-55JM`. It was found
only because the session happened to verify the merge against `origin/main`
file by file; the merge notification, the pull request's own state and the
branch ref all read as success. Recovered by restarting the branch on the merged
`main` and carrying the commit forward, as #286.

**Why it matters, and where the existing cover stops.** The item store is
already watched: `bin/docket stranded` and the session-start digest report an
item that exists only on a branch, so `PL-ZSV6` would have surfaced in the next
session. Nothing watches anything else. The `.claude/skills/docket/SKILL.md`
edit in that same commit - the actual behavior change - is invisible to every
check the project runs, and would have stayed lost until someone noticed
sessions still doing the corrected thing. The asymmetry is the finding: the
queue has a stranded-work detector and the tree does not.

It is also silent in the direction that costs most. A dropped commit leaves no
conflict, no red check and no advisory; the next session starts from a `main`
that is missing work everyone believes landed, and `CLAUDE.md`'s rule that a
behavior change takes effect in the session that asks for it is quietly void.

**Where.** Detection, not prevention - who clicks merge and when is outside this
repository. `subprojects/docket/src/docket/vcs.py` already holds the merged/
unmerged reasoning `stranded` and `branches_in_flight` are built on, and
`_work_already_on_base` already asks the content question a squash merge
requires, so the machinery exists.

**Decision needed.** Detect it in `stranded`/the digest by reusing the existing
merged-versus-unmerged walk, or check at merge time against the GitHub API?
The first is cheap and needs no new state; the second is more timely but makes
`docket` learn about this harness, which `PL-SK88` says it must not.

**Approach, not yet decided.** Cheapest first: have `stranded` (or the digest)
report a branch whose pull request is *merged* while the branch ref still holds
commits the base does not, rather than only reporting item files. That reuses
the existing walk and needs no new state. The alternative - checking at merge
time - needs a GitHub API round trip the tool deliberately does not make
(`PL-SK88` records why `docket` must not learn about this harness).

**Done when.** A commit left behind by a merge at a stale head is reported by
something the next session reads, whether or not it touched `docs/items/`.
