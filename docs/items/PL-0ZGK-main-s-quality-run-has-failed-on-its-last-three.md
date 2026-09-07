---
id: PL-0ZGK
title: main's quality run has failed on its last three merges and nothing surfaces it: the whole-store verify replay runs only on push to main, so a green pull request turns main red after it lands
priority: P2
effort: M
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.9
touches: .github/workflows/quality.yml, .claude/hooks, tools/main_ci_status.py, docs/ARCHITECTURE.md
added: 2026-09-07
closed: 2026-09-07
pr: 438
verify: uv run pytest tests/unit/test_main_ci_status.py && grep -q 'main_ci_status' .claude/hooks/docket-digest.sh
---

**Problem.** `main`'s `quality` workflow has concluded `failure` on its last
three completed pushes, and no session is told. The failing step is the same one
each time, and every other step passes.

**Measured 2026-09-07** via the Actions API:

| Run | Head | Conclusion |
| --- | --- | --- |
| 1533 | `2c73fe9` (#426) | failure |
| 1531 | `888c1f4` (#425) | failure |
| 1529 | `83516af` (#424) | failure |

Run 1533's job has 24 steps. Steps 1-13 all succeed — `doc_check`,
`branch_id_check`, `rules_paths_check`, `bin/docket check`, `ruff`, `mypy`, the
full suite at 100% coverage. Step 14, "verify replay, scoped to what this branch
changed", is **skipped** (`if: github.event_name == 'pull_request'`). Step 15,
"verify replay, the whole store", is the **failure**, and steps 16-20 are then
skipped.

The error it fails on reproduces locally: `bin/docket check --verify` reports
`PL-0GTC` and `PL-SR8F` open with a command that already passes.

**Why it matters.** The two halves of `quality.yml`'s replay are mutually
exclusive by design — `PL-…`'s reasoning is sound, that a branch's question is
the items it edited and the whole store is a fact about `main` — but the
consequence is that this class of error **cannot** be seen before it lands. A
pull request replays only its own items and goes green; the whole-store sweep
runs after the merge, on a push nobody is watching, and there is no notification,
no digest line and no local check that reads it. `make check` does not run
`--verify` at all, deliberately, for the cost.

So the default branch has been red for at least three merges with every session
believing the tree is clean, and each new merge adds another red run to a branch
already red — which is the state that trains a reader to stop looking. It is also
upstream of everything: every merge passes through it.

**What is *not* the problem.** The sweep is correct. `PL-0GTC` (MODEL.md's
step-atomicity section still calls the class `RespiratorySystem`) and `PL-SR8F`
(MODEL.md calls the case-opening displacement 'two orders milder') are genuinely
open with work that landed — `PL-SR8F`'s phrase was gone by `67b279b`,
`PL-ZVS7`'s own commit. Closing those two turns `main` green today. This item is
about the **second** merge that goes red the same way, unnoticed, whenever an
item is next finished without being closed.

**Decision needed.** Where should this signal reach a session, given that the
scoped/whole-store split is worth keeping and that `make check` should not pay
for a 163-second replay on every run? Three candidates, none costed:

1. **The session-start digest reads `main`'s last `quality` conclusion** and says
   so. Cheapest to act on — a session learns it before choosing work — and it
   generalises to every future red, not just this error. Needs network in the
   hook, which nothing there currently assumes.
2. **Run the whole-store sweep on pull requests too**, accepting the ~163 s. It
   catches this before the merge rather than after, at the price the scoped step
   was introduced to avoid, and it makes every pull request answerable for the
   whole store rather than for its own diff.
3. **A scheduled run that opens or updates an issue when `main` is red.** Keeps
   both CI steps as they are and moves the notification out of band; adds a
   mechanism to maintain.

**Where.** `.github/workflows/quality.yml` steps 14-15 and the comment above
them; `.claude/hooks/` for the digest that a session actually reads;
`subprojects/docket/src/docket/checks.py` is where the error itself is raised
(`_verify_required` and the already-passes report).

**Done when.** A session or the project owner learns that `main`'s quality run is
failing without having to open the Actions tab, and the chosen mechanism is
recorded here with why the other two were declined.

**Note.** Closing `PL-0GTC` and `PL-SR8F` is the immediate repair and is not this
item. Do that first; this item exists so the next occurrence is seen.

**Decided 2026-09-07 (project owner): candidate 1.** The session-start digest
reads `main`'s last `quality` conclusion, in `tools/main_ci_status.py`, called
from `.claude/hooks/docket-digest.sh`. It prints one line when that verdict was
not a success and nothing otherwise.

**Why the other two were declined.**

*Candidate 2 — run the whole-store sweep on pull requests too* — was recommended
first and withdrawn on reading `.github/workflows/quality.yml`. It reverses
`PL-SDHR` (the verify replay is 87 s of the checks job's 152 s), a `done`
decision from v0.4.3 that moved the sweep off pull requests deliberately and
with measurements. The cost has grown since: 177 s against PR runs of 110-130 s,
so it roughly doubles to triples every run, on every push to the 9 branches then
in flight, and `PL-SDHR` established that the bill grows with the size of the
queue rather than of the change.

The decisive objection is not cost, though. It makes every pull request
answerable for the whole store, so one session finishing work without closing
its item turns *every* open pull request red — a failure those authors did not
cause and cannot fix. That is `CLAUDE.md`'s "being routed around" test, and it
reproduces this item's own failure mode, a red that trains readers to stop
looking, at nine times the frequency.

*Candidate 3 — a scheduled run that opens an issue* — declined as the most
mechanism for the least reach: it adds a moving part to maintain and delivers
the signal to a place sessions do not read, when the digest is already the one
text every session sees.

**The recorded objection to candidate 1 was wrong**, which is why it was
reconsidered. "Needs network in the hook, which nothing there currently
assumes" is false: `.claude/hooks/docket-digest.sh` already runs `git fetch
--quiet --unshallow origin` (`PL-K2ZK`). Reading a *run conclusion* needs the
API rather than git, so that was tested rather than assumed — the repository is
public, so an unauthenticated call answers with no token.

**Verified against real data rather than fixtures alone.** Replayed over the
API's own history, the tool reproduces this item's incident exactly —
`main's quality run #1533 on 2c73fe9b concluded failure` — and stays silent on
today's `main`. The run that proved the design necessary is #1559 and #1555,
both `cancelled`: the two newest completed runs on `main` at the time of
writing, so a naive "read the latest completed run" would have reported a
non-verdict and said nothing useful. `pick_run` passes over those to the newest
run that actually concluded.

**Where it deliberately does not live.** Not in `docket`: that package answers
from a bare offline checkout and knows nothing about GitHub, and
`subprojects/docket/README.md` states the rule this would have broken. Not in
`.claude/hooks/` either, beyond the one line that calls it — the logic is
testable and the hook is not, and `docs/ARCHITECTURE.md` records why hooks stay
thin.

**Not fixed here.** `PL-T7VS` (a red `doc_check` voids the whole-store replay
for the 29 items gated behind it) is the adjacent finding: this item makes a
*failing* replay visible, and that one is about a replay that reports green
without having answered.
