---
id: PL-8DDG
title: Add CITATION.cff so the simulator is citable, and decide whether CONTRIBUTING.md is warranted yet
priority: P3
effort: S
status: done
classes: docs
feature: project-introduction
touches: CITATION.cff
added: 2026-09-05
closed: 2026-09-05
pr: 338
verify: test -f CITATION.cff && grep -q '^cff-version: 1.2.0$' CITATION.cff && grep -q '^license: Apache-2.0$' CITATION.cff
---

**Problem.** The repository root had `LICENSE` and nothing else of the
community set: no `CITATION.cff`, no `CONTRIBUTING.md`. Found while deciding
`PL-RM83` (what `README.md` is for), against the documentation standards
recorded in that item.

**Why it matters.** `CITATION.cff` was the clear half. GitHub parses a root
`CITATION.cff` into APA and BibTeX snippets behind a "Cite this repository"
control, so the cost is one small file and the return is that anyone writing
about the simulator cites it correctly and consistently. Lee 2018 makes it
rule 10 of ten — "tell people how to cite your software" — and recommends
exactly this file. It matters more here than for most hobby projects: the
project owner writes resident curriculum material and journal articles, so a
citable simulator is likely to be cited in their own work first, and an
uncitable one gets referenced as a bare URL that rots.

**What was done.** `CITATION.cff` at the repository root, CFF 1.2.0, carrying
the four required keys plus `abstract`, `type`, `repository-code`, `license`
(Apache-2.0, matching `LICENSE` and `pyproject.toml`) and `keywords`. The
author entry reuses the name and GitHub noreply address already in
`pyproject.toml` rather than a personal address, so making the repository
public publishes nothing new about the owner.

**`version` and `date-released` are deliberately absent.** Both are optional in
CFF 1.2.0 and both go stale at every release. Nothing in `make check` reads
this file, so a stale version here would be exactly the silently-wrong
statement `tools/doc_check.py` exists to prevent, arrived at through a file the
tool does not cover. If a DOI is ever minted — Zenodo mints one per GitHub
release, and JOSS is the other route — the version fields come with it and must
be written by the release path rather than by hand; that is a change to
`docket release`, and it is the point at which to add them, not before.

**The `CONTRIBUTING.md` question, answered: not yet.** JOSS requires community
guidelines covering how to contribute, report issues and seek support, and
`PL-RM83` decided that audience A — a contributor interested in both
anesthesiology and code — is one of the two readers the README is written for,
which argues for one. Against it: the repository is not public, so that
audience does not exist yet, and a `CONTRIBUTING.md` describing the
`bin/docket` queue and the agent-session workflow would be documenting
scaffolding to nobody. The holding position is a "Contributing" section in the
rewritten README pointing at issues, which is `PL-N092`'s to write, and a real
`CONTRIBUTING.md` when the repository goes public — recorded as a candidate on
`PL-XYRN` (decide when the repository goes public, and run the human-facing
pass immediately before it).

**Not verified from here.** That GitHub's "Cite this repository" control
actually renders cannot be checked from a container against a private
repository. The file parses and carries the required keys; confirm the control
when the repository is next opened in a browser.
