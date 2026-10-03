---
id: PL-S641
title: docs/maintainer.md has no section for re-running tag-release.yml where a session cannot - a dispatch GitHub refuses the session, or a tag origin holds on another commit - so the owner meets those steps only through bin/docket release's refusal, where § 'Sweep branches now' is the precedent for an owner-run workflow
priority: P3
effort: S
status: ready
classes: docs
touches: docs/maintainer.md
added: 2026-09-30
payoff: the owner can tag a release a session could not, from their own runbook, without a session to read the steps out
verify: grep -qiE '^## .*tag-release' docs/maintainer.md
---

**Problem.** docs/maintainer.md has no section for re-running tag-release.yml where a session cannot - a dispatch GitHub refuses the session, or a tag origin holds on another commit - so the owner meets those steps only through bin/docket release's refusal, where § 'Sweep branches now' is the precedent for an owner-run workflow

**Why it matters.** `docs/maintainer.md` is where the owner looks for what only they can do. Since `PL-F23S` (2026-10-03) re-running `tag-release.yml` is a session's, as a new dispatch on `main`; what stays the owner's is the fallback, and with its steps only in the release mode and `bin/docket release`'s refusal, the owner meets them only through a session, and an untagged release is what `PL-H1JD` records.

**Done when.** `docs/maintainer.md` has a section beside § "Sweep branches now, or restore one the sweep deleted" giving the owner's steps for the two cases a session cannot settle: running `tag-release.yml` from Actions > tag-release > Run workflow on `main`, or `python3 tools/tag_release.py --apply` from a clone, where GitHub refused the session's dispatch; and what to do where origin already holds the tag on another commit. It matches the release mode and the refusal and is checked against GitHub's current documentation.

**Narrowed 2026-10-03 (`PL-F23S`).** Filed when every re-run was the owner's. The owner's rule of 2026-10-03 made the re-run a session's, so this keeps only the fallback. Whether a session's dispatch is refused at all is not measured yet: the first untagged release measures it, and if the dispatch works the first case may never arise, leaving only the tag on another commit.

**Reproduced 2026-10-01.** No heading in `docs/maintainer.md` mentions a release or a tag.

**Generator check.** A one-off gap in the owner's runbook; no head states where the owner reads steps that are theirs.
