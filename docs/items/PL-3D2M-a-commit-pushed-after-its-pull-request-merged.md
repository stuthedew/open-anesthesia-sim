---
id: PL-3D2M
title: A commit pushed after its pull request merged lands nowhere, and nothing outside the item store notices
priority: P2
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md
added: 2026-09-04
closed: 2026-09-04
pr: 313
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_branch_pushed_to_after_its_pull_request_merged_is_reported' subprojects/docket/tests/test_vcs.py
---

**Problem.** A pull request merges the head it was opened against. A commit
pushed to the same branch afterwards is merged by nothing - nothing merges a
merged pull request a second time - so it lands nowhere, and it is silent in
every direction that would normally catch a mistake. There is no conflict, no
red check and no advisory; the branch reads as merged, the pull request reads
as merged, and the next session starts from a default branch missing work
everyone believes landed.

**The title and the problem statement above are corrected from what this item
was captured as, and the correction is the finding.** Captured as *a pull
request merged at a stale head* - GitHub squashing a head older than the
branch's tip - which is a different mechanism with a different detector, and
which is not what happened. Checked against GitHub's own record of `#284`:
`head.sha` at merge was `7f87bf5`, its three commits were `dc03044` and two
merges of `main`, and comparing that head against the commit that landed it
shows `main` holding all of it. The lost commit `9fee36c` is in none of them.
`#286`, the recovery, says it outright: "That pull request merged at its first
commit, so the behavior change pushed to the same branch afterwards never
landed." The merge took the whole head; the push came after it, at `01:17`
against a merge at `01:16`.

Worth keeping rather than quietly rewriting, because the misdiagnosis was
load-bearing: it named a detector that cannot see this failure, and it named it
in the "Approach" a later session would have built.

**Observed 2026-09-04.** The dropped commit carried a `CLAUDE.md`-mandated
behavior change - a rule the project owner had asked for in that session - plus
`PL-ZSV6` and a status correction to `PL-55JM`. It was found only because the
session happened to verify the merge against `origin/main` file by file.
Recovered by restarting the branch on the merged `main` and carrying the commit
forward, as `#286`.

**Why it matters, and where the existing cover stopped.** The item store was
already watched: `bin/docket stranded` and the session-start digest report an
item that exists only on a branch, so `PL-ZSV6` would have surfaced in the next
session. Nothing watched anything else. The `.claude/skills/docket/SKILL.md`
edit in that same commit - the actual behavior change - was invisible to every
check the project runs, and would have stayed lost until someone noticed
sessions still doing the corrected thing. The asymmetry was the finding: the
queue had a stranded-work detector and the tree had none.

**Decision (2026-09-04): detect it from the branch refs, as the item's first
option proposed. The second option is not merely disfavoured - it cannot
work.** The fork was "detect it in `stranded`/the digest by reusing the
existing merged-versus-unmerged walk, or check at merge time against the GitHub
API". Three measurements settle it:

- **A merge-time check would see nothing.** GitHub freezes `refs/pull/<n>/head`
  when the pull request closes, so a commit pushed afterwards appears in no
  pull-request ref. Fetched all 311 of this repository's pull refs (1.9 s) and
  compared each merged head against the commit that landed it: **0 discrepancies
  and 0 conflicts across all 204 merged pull requests.** The loss is invisible
  from that side. It would also have made `docket` learn about this harness,
  which `PL-SK88` says it must not - but that argument was never needed.
- **The branch ref is the evidence, and it survives precisely because of the
  failure.** Merged head branches are deleted here - origin holds 2 branches
  against 311 pull requests - so an ordinary merged branch leaves no ref. A
  post-merge push recreates one. The ref that should not exist is the signal.
- **The discriminator is a branch split across the base.** Content partly on
  the base and partly not. A branch nobody merged has landed nothing; a branch
  merged whole never reaches the read. Measured against the one live branch the
  day this was built: 0 landed against 17 outstanding, the clean signature of
  work in progress, so the rule was silent on the only ref it had to be silent
  on.

**What was built.** `vcs.orphaned`, printed by `bin/docket stranded` beside the
stranded items and carried by the session-start digest as one line when there
is one. It names the branch, the outstanding paths, the commit carrying them and
the `git checkout` line that recovers each. `format_stranded`'s closing claim -
"this says nothing about *code* on a branch" - is now answered rather than
merely admitted.

Deciding a ref is unlanded now computes the landed/outstanding split rather than
short-circuiting on it, so the per-blob `git log --find-object` walk was replaced
by one walk of the base's objects: **0.033 s against 0.62 s** for the seventeen
walks it replaces on this repository, so the complete answer costs less than the
partial one did.

**What it can get wrong, in the direction chosen deliberately.** Two sessions
running `bin/docket record` write the same tool-dictated line, so one branch can
hold a blob identical to one the other landed and read as partly landed while it
is simply live. That is a false alarm costing a glance, against a false silence
costing the work.

**Not renamed on disk.** The file keeps the slug of the old title. `PL-S5LB`
records that `_number_closing` has no rename detection, so renaming an item file
makes `bin/docket record` recover the renaming commit's number instead of the
closing one - a stale slug is the cheaper of the two.

**Done when.** A commit left behind on a branch whose pull request has already
merged is reported by something the next session reads, whether or not it
touched `docs/items/`. Done.
