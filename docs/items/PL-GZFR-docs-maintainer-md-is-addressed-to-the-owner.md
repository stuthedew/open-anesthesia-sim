---
id: PL-GZFR
title: docs/maintainer.md is addressed to the owner but instructs sessions in about a dozen places (owner-ask records, the Auto-merge trailer, worker-run review, the effort-trial reply); check each also stands where sessions read it, then leave here only what it guarantees the owner (copy editor structure read, 2026-11-07)
priority: P2
effort: M
status: done
classes: defect, docs
feature: maintainer-guide-structure
touches: docs/maintainer.md, .claude/skills/pull-request/SKILL.md
added: 2026-11-07
closed: 2026-11-11
pr: 2104
payoff: every rule for sessions stands where sessions read it, and the owner's guide holds only what he does or is guaranteed
not-delegable: whether a sentence instructs a session or tells the owner is a judgment, and the rules may move into .claude/, so no command can prove the item done
---

**Problem.** docs/maintainer.md is addressed to the owner but instructs sessions in about a dozen places (owner-ask records, the Auto-merge trailer, worker-run review, the effort-trial reply); check each also stands where sessions read it, then leave here only what it guarantees the owner (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** `docs/maintainer.md` still opens "Everything here is addressed to the person running the sessions, not to the sessions themselves", and still tells sessions what to do. Examples: "The session records what to ask you as an `Owner-ask:` trailer on a commit" (§ "What comes to you before it merges"), the `Auto-merge: off - <why>` trailer (§ "Bring a stale base in when you merge, with Update branch"), the reviewing session's `tools/worker_runs.py review` step (§ "Spend the monthly API credit on delegable items"), and the effort trial's `move` command.

**Why it matters.** Sessions do not read this file unless something points them to it. A rule for sessions that stands only here is not followed, and one that stands here and in a skill is two copies that can drift apart. The owner, who does read it, has to skip passages that are not addressed to him.

**Done when.** Each instruction to a session in `docs/maintainer.md` is confirmed to stand where sessions read it (`CLAUDE.md`, a skill, a rule or `docs/worker.md`), and is moved there where it does not. What remains here tells the owner what to do, or what a session guarantees him, with a pointer to the rule.

**Generator check.** One-off: a finding from the `docs/maintainer.md` structure-read sweep. The fact is where a rule for sessions is kept. `PL-PDVF` (done) stated it for the Project's instructions; here the second holder is a document inside the repository, which that head's fix did not cover, and one item is not a cluster.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/maintainer.md` already opened "Everything here is addressed to the person running the sessions", and already told sessions to record an `Owner-ask:` trailer, to record an `Auto-merge: off - <why>` trailer, and to run `tools/worker_runs.py review` before opening a worker's pull request. So the item joins v0.7.0's frozen list.

**Done 2026-11-11.** A read-only search listed 25 places where `docs/maintainer.md` says what a session does, and looked for each in `CLAUDE.md`, the skills, the rules, `docs/worker.md` and the text the tools print. Each was then checked against the file it named.

- **Missing where sessions read, now moved.** The review of a headless worker's branch before its pull request opens, and carrying a sent-back branch's two record commits to their own branch, stood only here. Sessions met the first only as `make check`'s failure text, and the second nowhere. Both are now in `.claude/skills/pull-request/SKILL.md` § "Open the pull request with the work", and § "Spend the monthly API credit on delegable items" says what the reviewing session guarantees and points there.
- **Standing where sessions read, now named here.** The subagent model and effort rules and "a session does not argue for `high` on cost" stand in the dead-ends list that the session-start digest prints (`PL-2D28`), and the effort rule also in `.claude/rules/apparatus-standard.md`. The move to `xhigh` for a generator's cause stands in `triage.md`. The `/compact` reset stands in `start.md`. Re-running `tag-release.yml` stands in `release.md`. Each passage here now names that place.
- **The pull request sections.** The `Owner-read:`, `Owner-ask:` and `Auto-merge: off - <why>` trailers, the exception that leaves an owner's arm in place on a repair push, the direct squash merge and the deliberate lag behind `main` stand in `.claude/skills/pull-request/SKILL.md` and in the text `bin/docket arm` prints, which gives each trailer's form at the moment a session records it. The merge guard prints its own refusal. § "What comes to you before it merges" and § "Bring a stale base in when you merge, with Update branch" now open by naming those places, and the passages stay as the owner's account of what sessions guarantee.
- **Unchanged.** The routing of an owner's rule into the repository (`CLAUDE.md`, `coordinator.md`), the effort trial's first-reply line (printed by `tools/effort_trial.py`), the ledger's "a working session writes nothing about itself" (`model-review/SKILL.md`; a working session has no reason to write one), the model document review's findings (`PL-5S71`), and the setup-script check (`coordinator.md`) already name or sit beside their rule.
- The opening paragraph now says that a rule for sessions never lives only here, and that a passage saying what a session does states what it guarantees the owner and names where sessions read the rule.

