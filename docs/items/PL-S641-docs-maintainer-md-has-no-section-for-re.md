---
id: PL-S641
title: docs/maintainer.md has no section for re-running tag-release.yml after a failed run, though the run is the project owner's: the steps sit in release mode and in bin/docket release's refusal, where § 'Sweep branches now' is the precedent for an owner-run workflow
priority: P3
effort: S
status: ready
classes: docs
touches: docs/maintainer.md
added: 2026-09-30
payoff: the owner can re-run a failed release tag from their own runbook, without a session to read the steps out
verify: grep -qiE '^## .*tag-release' docs/maintainer.md
---

**Problem.** docs/maintainer.md has no section for re-running tag-release.yml after a failed run, though the run is the project owner's: the steps sit in release mode and in bin/docket release's refusal, where § 'Sweep branches now' is the precedent for an owner-run workflow

**Why it matters.** `docs/maintainer.md` is where the owner looks for what only they can do, and re-running `tag-release.yml` after a failed run is theirs; with the steps only in the release mode and `bin/docket release`'s refusal, the owner meets them only through a session, and an untagged release is what `PL-H1JD` records.

**Done when.** `docs/maintainer.md` has a section beside § "Sweep branches now, or restore one the sweep deleted" giving the owner's steps to re-run `tag-release.yml` after a failed run, matching the release mode and the refusal, checked against GitHub's current documentation.

**Reproduced 2026-10-01.** No heading in `docs/maintainer.md` mentions a release or a tag.

**Generator check.** A one-off gap in the owner's runbook; no head states where the owner reads steps that are theirs.
