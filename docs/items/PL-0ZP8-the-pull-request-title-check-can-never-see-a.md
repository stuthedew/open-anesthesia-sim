---
id: PL-0ZP8
title: The pull-request title check can never see a corrected title
priority: P2
effort: S
status: dropped
closed: 2026-09-03
reason: Duplicate of PL-3V8K, which found and fixed the same defect independently and landed on main in #256 hours earlier. Both diagnosed it identically - `quality.yml`'s bare `pull_request:` trigger excludes `edited`, so the rename the check asks for fires no event, and an Actions re-run replays the stale title - and both fixed it the same way, by splitting the check into `.github/workflows/pr-title.yml` with `types: [opened, synchronize, reopened, edited]`. On merging main into #257 the two collided as an add/add conflict; main's version was taken verbatim, so this branch now changes neither workflow and this item closes nothing. Dropped rather than deleted so the independent confirmation is not lost, and so the one difference between the two fixes stays findable: this branch pinned `actions/setup-python` at the 3.11 floor and main's runs the runner's default interpreter, which is captured separately as PL-79N5.
classes: defect, infra
feature: dev-tooling
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-03
---

**Problem.** `tools/pr_title_check.py` fails a pull request whose title does
not lead with the ids it closes, and prints the remedy: *"Rename the pull
request to lead with the ids."* Renaming the pull request did nothing.

`.github/workflows/quality.yml` carried no `types:` on its `pull_request`
trigger, so it used the Actions default set — `opened`, `synchronize`,
`reopened` — which **does not include `edited`**. A rename fires no event.
And re-running the failed job does not help either: an Actions re-run replays
the original event payload, so `github.event.pull_request.title` is still the
stale title and the job fails identically.

**Found independently, on a different pull request.** `#257`, 2026-09-03: the
pull request was opened closing one item, grew to close three, was renamed to
lead with all three, and CI still failed on the title captured when the run
was triggered. `PL-3V8K` had found the same thing on `#256` and its fix was
already merged; neither session could see the other's work.

**Why it is recorded rather than deleted.** Two sessions reaching the same
diagnosis and the same fix within hours is evidence about the defect — it was
reachable by ordinary use, not a corner case — and `docket`'s own rule is that
a finding dropped without a reason gets raised again by the next person who
notices it. The `reason` above carries where the work actually lives.

**The one substantive difference, not carried across.** This branch's
`pr-title.yml` pinned `actions/setup-python` to the 3.11 floor; main's runs
the runner image's default `python3`. Main's version was taken verbatim
anyway, because editing a file that had just landed under another item to
import a preference from a duplicate is not a merge resolution. `PL-79N5`
records the resulting coverage gap and the two ways to close it.

**Superseded by.** `PL-3V8K` (`quality.yml` does not run on `pull_request`
`edited`), done, merged in `#256`.
