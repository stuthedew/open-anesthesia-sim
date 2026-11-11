---
id: PL-M8Z7
title: docs/maintainer.md describes hooks acting in every session (effort trial, owner-ask guard, merge guard, stop hook patch), but its setup-script section says a Projects thread runs none of them until that script is added; say whether they act in a Projects thread today (copy editor structure read, 2026-11-07)
priority: P2
effort: S
status: done
classes: defect, docs
feature: maintainer-guide-structure
touches: docs/maintainer.md
added: 2026-11-07
closed: 2026-11-11
pr: 2097
payoff: the owner knows whether the guard hooks protect a Projects thread today, and which hooks reach one
verify: grep -qF '2026-11-03' docs/maintainer.md
---

**Problem.** docs/maintainer.md describes hooks acting in every session (effort trial, owner-ask guard, merge guard, stop hook patch), but its setup-script section says a Projects thread runs none of them until that script is added; say whether they act in a Projects thread today (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** § "Give Projects threads the repository's hooks with one setup script" in `docs/maintainer.md` still opens "A Claude Projects thread does not load `.claude/settings.json`, so none of the repository's hooks run in it", and still reads as setup that is yet to be done. `PL-CR81` (done) records that on 2026-11-03 a thread in the project did run the hooks: `gate-status-guard.sh` refused a test command, and the docket digest printed at session start, through the setup script and `.claude/hooks/thread_hooks.py`.
<!-- absent: gate-status-guard.sh -->

**Why it matters.** The owner reads this file to know whether the guards protect a thread. As written he cannot tell whether the setup is done, and the passages that describe a hook acting in every session (the effort trial, the owner-ask guard, the merge guard, the stop hook patch) do not say whether a thread is one of them.

**Done when.** The setup-script section says, with the date and `PL-CR81`, that a thread ran the hooks once the setup script was in place. Each passage that describes a hook acting in every session says whether that includes a Projects thread.

**Generator check.** One-off for now. The fact is whether the repository's hooks run in a Projects thread, which `PL-CR81` measured on 2026-11-03. `PL-DH17` also rests on the older answer, and `CLAUDE.md`'s bullet on waiting through the harness (`PL-D1FD`) states it. No head states the fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/maintainer.md` already said that `.claude/hooks/owner_ask_guard.py` "refuses a thread's reply", while Projects threads ran none of the repository's hooks; `PL-CR81` found that on 2026-10-25. The setup-script section came later, in 50939e38 (`PL-X6VN`), but the mismatch between what the file says hooks do in a thread and what they did was already there. So the item joins v0.7.0's frozen list.

**Done 2026-11-11.** § "Give Projects threads the repository's hooks with one setup script" now opens with the result: the project's threads run the repository's hooks through the setup script, as `PL-CR81` found on 2026-11-03. The paragraph that says why the script is needed follows it. The passages on the effort trial, the owner-ask guard, the merge guard and the stop hook patch each say that a Projects thread is included, through that script.

**Measured again 2026-11-11, about 00:25Z**, in the doc chain thread (Claude Code 2.1.322, `CLAUDE_CODE_ENTRYPOINT=remote_projects`). `~/.claude/settings.json` held the repository's `hooks` block: `SessionStart` entries for `stop_hook_patch.py` and `docket-digest.sh`, `PreToolUse` entries for `guard.sh` on edits, Bash and MCP calls, and the `PostToolUse` entries. After the thread compacted, its session start printed the docket digest and the effort trial's line that a thread is in neither arm. A `git push` printed the pull-request skill's note from the Bash guard. `~/.claude/stop-hook-git-check.sh` held the corrected `unpushed=` line that `stop_hook_patch.py` writes.
