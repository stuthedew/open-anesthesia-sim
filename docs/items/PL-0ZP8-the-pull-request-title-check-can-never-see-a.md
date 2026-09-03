---
id: PL-0ZP8
title: The pull-request title check can never see a corrected title
priority: P2
effort: S
status: done
closed: 2026-09-03
classes: defect, infra
feature: workflow-reliability
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-03
verify: python3 tools/doc_check.py check && grep -q 'edited' .github/workflows/pr-title.yml && ! grep -q pr_title_check .github/workflows/quality.yml
---

**Problem.** `tools/pr_title_check.py` fails a pull request whose title does
not lead with the ids it closes, and prints the remedy: *"Rename the pull
request to lead with the ids."* Renaming the pull request does nothing.

`.github/workflows/quality.yml` carried no `types:` on its `pull_request`
trigger, so it used the Actions default set — `opened`, `synchronize`,
`reopened` — which **does not include `edited`**. A rename fires no event.
And re-running the failed job does not help either: an Actions re-run replays
the original event payload, so `github.event.pull_request.title` is still the
stale title and the job fails identically.

So the check's printed remedy was unreachable. The only way out was pushing an
unrelated commit to manufacture a `synchronize` event — which is the
workaround the harness rules forbid for exactly the reason it is bad, and
which a session with no other work to push cannot perform at all.

**Why it matters.** This is `CLAUDE.md`'s "friction that compounds" shape: it
is paid by every pull request whose title needs correcting, which is every
pull request whose scope grew after it was opened — the common case for this
project, where a session opens the pull request with the work and then keeps
working. It fails the retirement test's mirror image: the check gives the
*right* answer and names a remedy nobody can follow, so the honest options
were to route around it or to be stuck.

It also cost the thing the check exists to protect. `pr_title_check.py`'s own
docstring records `#220`, where a title naming none of its three items landed
on `main`, destroyed provenance `docket check` reads, and blocked the v0.3.0
release. A check that cannot be satisfied is one a future session has an
incentive to disable.

**Found.** `#257`, 2026-09-03. The pull request was opened closing one item,
grew to close three, was renamed to lead with all three — and CI still failed
on the title captured when the run was triggered.

**What landed.** The check moved to its own workflow,
`.github/workflows/pr-title.yml`, with
`types: [opened, synchronize, reopened, edited]`.

A trigger is per-workflow, which is why this is a new file rather than a job.
Two alternatives were considered and rejected:

- *Add `edited` to `quality.yml`'s trigger.* Re-runs the full suite — lint,
  mypy, the entire test run — on every pull-request body edit.
- *Add `edited`, and guard the heavy jobs with `if: github.event.action !=
  'edited'`.* A job skipped by `if:` reports the conclusion `skipped`, not
  `success`, and how required status checks treat that is not something to
  discover on a protected branch.

Two improvements come free. The check reported *last*, after the full suite;
as its own job it reports in seconds, which is when a title problem is
cheapest to fix. And it runs under a bare `python3` with no `uv sync`, because
`tools/pr_title_check.py` depends on nothing outside the standard library.

**Verified by reproduction.** The original failure was reproduced locally with
the stale title in `PR_TITLE`, then the same command shown passing with the
corrected one, before pushing.

**Done when.** A rename re-runs the title check; `quality.yml` no longer
invokes `pr_title_check.py`; and the full suite does not re-run on a
pull-request body edit.
