---
id: PL-XZD0
title: Nothing reconciles the jobs that report a status check on pull_request against the branch-protection required list, in either direction: PL-KPP1 covers removing one by comment alone, and nothing at all covers adding one
status: untriaged
feature: pr-title-enforcement
added: 2026-09-17
---

**Problem.** Nothing reconciles the jobs that report a status check on pull_request against the branch-protection required list, in either direction: PL-KPP1 covers removing one by comment alone, and nothing at all covers adding one

**Why it matters.** Two failures, one root, and the repository currently
addresses half of one of them with prose.

- **Removing or renaming** a reporting job orphans the requirement named after
  it. Every pull request then waits forever on a check that cannot arrive -
  pending rather than failing, so it does not look like a break. `PL-D551`
  deleting `quality.yml`'s `floor` job did exactly this (`PL-KPP1`, `#377`).
  The remedy was a comment in each workflow.
- **Adding** one creates a check nothing makes required. `PL-H8YD` is the
  instance: `PL-3V8K` split the title check out of `checks` into its own job to
  fix the `edited`-trigger problem, which silently moved it out from behind the
  only requirement that had been gating it. It stayed ungated for eleven
  releases, and `#654` merged on a failed `pr-title` because of it.

Both comments say the same thing - "the required list lives in repository
settings, which no script here can read, so nothing in `make check` or CI will
catch the next one". **That premise is true of `make check` and false of CI.**
A workflow can read `GET /repos/{owner}/{repo}/branches/{branch}/protection`
and compare the required contexts against the jobs that report on
`pull_request`, which is exactly the deterministic reconciliation `CLAUDE.md`
prefers over a rule a session has to remember.

**The design work is the permission, and it is the reason to think before
building.** That endpoint needs more than the default `GITHUB_TOKEN` read
scope, and `PL-N5WZ` is this project's recorded dead end on exactly this
terrain - "a push made with `GITHUB_TOKEN` starts no workflow, so a protected
default branch never sees required checks report", where every configuration
that would have made it work weakened the gate. So settle what token this needs
and what it costs *before* writing the check; a guard that needs a
broadly-scoped secret to protect a two-job list may be worse than the comment.

**Name the number before building it.** This repository has had exactly two
jobs that report a status check on `pull_request` - `checks` and `pr-title` -
across its whole history, and the set changed twice: once by deletion
(`PL-KPP1`) and once by addition (`PL-H8YD`). So the event rate is about one per
five months, and `CLAUDE.md`'s gate for building a mechanism is whether it will
genuinely run again. Against that, both changes were silent, both cost real
damage, and neither was caught by anything. Decide on those two numbers rather
than on how nice the check would be.

**Done when.** A decision is recorded - in `ROADMAP.md` or in the workflows'
own comments - either naming the check that reconciles the two lists and what
token it uses, or saying that the comment is the whole remedy and why a check
is not worth its permission. `PL-KPP1`'s and `PL-H8YD`'s comments point at that
decision instead of each restating the premise separately.
