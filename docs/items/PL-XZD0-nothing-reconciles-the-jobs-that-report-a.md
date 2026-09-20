---
id: PL-XZD0
title: Nothing reconciles the jobs that report a status check on pull_request against the branch-protection required list, in either direction: PL-KPP1 covers removing one by comment alone, and nothing at all covers adding one
priority: P2
effort: S
status: done
classes: infra
feature: pr-title-enforcement
touches: .github, tools/required_checks_check.py, tests/unit/test_required_checks_check.py, docket.toml, docs/ARCHITECTURE.md
added: 2026-09-17
closed: 2026-09-19
pr: 740
payoff: stops a renamed CI job leaving pull requests waiting forever on a check that can never arrive
verify: grep -q 'def test_pl_kpp1_a_deleted_job_orphans_its_requirement' tests/unit/test_required_checks_check.py
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

**Decision needed.** Whether CI should reconcile the two lists at all, and if
so with what credential. Three candidate answers, and the permission is what
separates them: a workflow reading
`GET /repos/{owner}/{repo}/branches/{branch}/protection` with a token scoped
beyond the default `GITHUB_TOKEN` read grant; the same reconciliation run by
hand at release time and recorded as a step; or the comment in each workflow
standing as the whole remedy. Decide it on the two numbers this brief already
carries - one set change per five months, both silent, both costly - and on
`PL-N5WZ`'s recorded dead end, not on how useful the check would feel.

**Done when.** A decision is recorded - in `ROADMAP.md` or in the workflows'
own comments - either naming the check that reconciles the two lists and what
token it uses, or saying that the comment is the whole remedy and why a check
is not worth its permission. `PL-KPP1`'s and `PL-H8YD`'s comments point at that
decision instead of each restating the premise separately.

## Answered 2026-09-19: build it, because the premise the brief rested on is false

**The decision is to reconcile in CI, with no credential at all**, and the case
that settled it is not the one this brief framed. The brief expected the answer
to turn on a token: `GET /repos/{owner}/{repo}/branches/{branch}/protection`
needs the `administration` permission, an Actions `GITHUB_TOKEN` can never hold
it - `administration` is not one of the keys a workflow's `permissions:` block
may set - and a guard needing a broadly-scoped secret to protect a two-job list
would plausibly be worse than the comment. All of that is true, and it is about
the wrong endpoint.

`GET /repos/{owner}/{repo}/branches/{branch}` carries
`protection.required_status_checks.contexts`, and on a public repository it
answers **unauthenticated**. Measured 2026-09-19 against this repository:

| Call | Result |
| --- | --- |
| `.../branches/main/protection`, session token | 403 `Resource not accessible by integration` |
| `.../branches/main`, same token | 200, `contexts: ["checks", "pr-title"]` |
| `.../branches/main`, **every token stripped from the environment** | 200, same contexts |

So the cost side of the trade this brief set up is zero - no secret, no
permission grant, nothing widened - and `PL-N5WZ`'s dead end does not reach it:
that one is about a *push* made with `GITHUB_TOKEN` starting no workflow, which
is a write, and this is a read of public metadata. Against an event rate of one
set change per five months, both silent and both costly, a guard that costs
nothing but the code is worth building. Had the credential been needed, the
answer here would have been the comment.

**A second fact, found while measuring, changed the design.** This repository
carries both settings surfaces: one active ruleset (`Base`, id 21260116) whose
rules are `deletion`, `pull_request` and `non_fast_forward` - and **no**
`required_status_checks` rule - alongside classic branch protection, which is
where the two contexts actually live. GitHub's UI steers toward rulesets, so
moving that setting would empty the surface a naive check reads and fill one it
does not, and the check would report "nothing required" and pass. That is
`CLAUDE.md`'s first compounding-friction test exactly - a check passing while
its guarantee is void - so `tools/required_checks_check.py` reads both surfaces,
unions them, and **treats an empty union as a hard failure** rather than as
agreement.

**What was built.** `tools/required_checks_check.py`, stdlib only, run as a
*step inside* `quality.yml`'s `checks` job. A step rather than a job because a
new job reports a new status check that would itself need adding to the
required list - the exact trap `PL-H8YD` records - so as a step it inherits the
requirement `checks` already carries and adds no entry to the list it guards.
It is not wired into `make check`: its input is not in the tree, and `make
check` runs offline in a bare checkout.

It refuses rather than guesses where it must - a matrix job, a reusable
workflow call, an unreadable `on:` block, an unreachable API - because a job
silently dropped from the reporting set reads as "nothing to reconcile" and
passes. A job that reports a check and is deliberately not required declares
`# not-required: <reason>` above its key, so the first advisory-only job does
not turn this into a check that fires every run, which `CLAUDE.md` retires.

**Verified end to end against live settings, not only in fixtures.** Renaming
`checks` to `quality-checks` in a scratch copy of the workflows produced both
findings at once, read against the repository's real required list:

    FAIL - required but reported by no job: checks
    FAIL - reports on a pull request but is not required: quality-checks

**The comments converge, as this item asked.** `quality.yml` and
`pr-title.yml` each kept the load-bearing-name fact and now point at the tool's
docstring for the rule, the two regressions and the measurement. `pr-title.yml`
keeps the one thing readable from nowhere else in the tree - that its job
entered the required set on 2026-09-17 and why it had been outside it. The two
comments had already drifted: each described the direction its own regression
had taken, and neither described the other.
