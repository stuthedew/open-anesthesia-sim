---
id: PL-GZFR
title: docs/maintainer.md is addressed to the owner but instructs sessions in about a dozen places (owner-ask records, the Auto-merge trailer, worker-run review, the effort-trial reply); check each also stands where sessions read it, then leave here only what it guarantees the owner (copy editor structure read, 2026-11-07)
priority: P2
effort: M
status: ready
classes: defect, docs
feature: maintainer-guide-structure
touches: docs/maintainer.md, .claude/skills, docs/worker.md, CLAUDE.md
added: 2026-11-07
payoff: every rule for sessions stands where sessions read it, and the owner's guide holds only what he does or is guaranteed
not-delegable: whether a sentence instructs a session or tells the owner is a judgment, and the rules may move into .claude/, so no command can prove the item done
---

**Problem.** docs/maintainer.md is addressed to the owner but instructs sessions in about a dozen places (owner-ask records, the Auto-merge trailer, worker-run review, the effort-trial reply); check each also stands where sessions read it, then leave here only what it guarantees the owner (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** `docs/maintainer.md` still opens "Everything here is addressed to the person running the sessions, not to the sessions themselves", and still tells sessions what to do. Examples: "The session records what to ask you as an `Owner-ask:` trailer on a commit" (§ "What comes to you before it merges"), the `Auto-merge: off - <why>` trailer (§ "Bring a stale base in when you merge, with Update branch"), the reviewing session's `tools/worker_runs.py review` step (§ "Spend the monthly API credit on delegable items"), and the effort trial's `move` command.

**Why it matters.** Sessions do not read this file unless something points them to it. A rule for sessions that stands only here is not followed, and one that stands here and in a skill is two copies that can drift apart. The owner, who does read it, has to skip passages that are not addressed to him.

**Done when.** Each instruction to a session in `docs/maintainer.md` is confirmed to stand where sessions read it (`CLAUDE.md`, a skill, a rule or `docs/worker.md`), and is moved there where it does not. What remains here tells the owner what to do, or what a session guarantees him, with a pointer to the rule.

**Generator check.** One-off: a finding from the `docs/maintainer.md` structure-read sweep. The fact is where a rule for sessions is kept. `PL-PDVF` (done) stated it for the Project's instructions; here the second holder is a document inside the repository, which that head's fix did not cover, and one item is not a cluster.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/maintainer.md` already opened "Everything here is addressed to the person running the sessions", and already told sessions to record an `Owner-ask:` trailer, to record an `Auto-merge: off - <why>` trailer, and to run `tools/worker_runs.py review` before opening a worker's pull request. So the item joins v0.7.0's frozen list.
