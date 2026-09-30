---
id: PL-ZZHZ
title: capture.md's merged-branch restart recipe still hands every remote deletion to the project owner ('say the remote deletion is outstanding and leave it to the owner'), where PL-X8SV's branch sweep now deletes a finished claude/* branch daily and only a branch it keeps reaches the owner, so its copy of the recipe and no-prune-guard.sh's (PL-J3TV) no longer say the same thing
priority: P2
effort: S
status: ready
classes: defect, docs
feature: parallel-sessions
touches: .claude/skills/docket/modes/capture.md, .claude/hooks/no-prune-guard.sh
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-30
payoff: a session restarting a merged branch leaves its remote copy to the branch sweep and hands the owner only a branch the sweep keeps, whichever of the two copies of the rule it read
verify: grep -qF 'python3 tools/branch_sweep.py' .claude/skills/docket/modes/capture.md && grep -qF 'left to the branch sweep and the project owner' .claude/hooks/no-prune-guard.sh
---

**Problem.** capture.md's merged-branch restart recipe still hands every remote deletion to the project owner ('say the remote deletion is outstanding and leave it to the owner'), where PL-X8SV's branch sweep now deletes a finished claude/* branch daily and only a branch it keeps reaches the owner, so its copy of the recipe and no-prune-guard.sh's (PL-J3TV) no longer say the same thing

**Why it matters.** This is the recipe a session follows when `bin/docket
stranded` or `bin/docket branch` names a branch whose pull request merged and
left a commit behind (`PL-3D2M`, `PL-8M8H`), and as written it ends every such
recovery by handing the owner a remote deletion: the hand-made deletion list
`PL-X8SV` retired (project owner, 2026-09-26, ratified, over a list built by
hand). For this branch the deletion is not the owner's at all. The sweep holds
it while its commit reads as left behind, a commit carried across stops reading
that way once its change is on `main` (`vcs.change_landed`), and the sweep then
archives the branch under `refs/archive/` and deletes it. A deletion run by
hand skips that archive, so the recipe also steers the owner to the less
reversible of the two routes. And the two copies of the rule now disagree, so
which one a session follows depends on whether it was refused a prune or read
the skill. The hook's push refusal carries a third copy in the pre-sweep words:
"Deleting branches on the remote is left to the project owner: list them in the
reply".

**Done when.** `.claude/skills/docket/modes/capture.md`'s restart block holds
the three commands the hook prints, and its paragraph says the branch on the
remote is `branch-sweep.yml`'s, with the reply naming one to the owner only
where `python3 tools/branch_sweep.py` keeps it and it should go anyway. The push
refusal in `.claude/hooks/no-prune-guard.sh` says the same, and
`tests/unit/test_no_prune_guard.py` passes unchanged.

**Generator check.** The fact misread is who deletes a branch on the remote,
which `PL-X8SV` moved from the owner to `branch-sweep.yml` and which six places
restate as prose: `CLAUDE.md`'s housekeeping bullet, `docs/worker.md`
§ "Ref operations a session cannot perform", two paragraphs of this file's
subject and two deny messages in `.claude/hooks/no-prune-guard.sh`. `PL-X8SV`
updated three of them and `PL-J3TV` a fourth. That is `PL-G424`'s fact, "The
link between a document sentence and the tree fact it restates", in the prose
drift its rule leaves to the capture rule (`.claude/rules/citation-drift.md`
§ "What this does not reach"). So this is an instance of that head filed after
it closed, not a new head: two items on the fact (`PL-J3TV`, this one) is under
the three a head needs, and the third stale copy, the push refusal, is repaired
here rather than filed.
