---
id: PL-GVC0
title: The item id prefix is hard-coded as `PL-`, the one thing in docket that is not configurable
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/vcs.py, docket.toml
added: 2026-08-30
classes: infra
---

**Problem.** `store.ID_PREFIX = "PL-"` and the branch-name regex in
`vcs.BRANCH_ID_RE` both spell this repository's id prefix into the package.
Every other project-specific value — protected paths, debt classes, the check
command, the roadmap and version filenames, the band limits — already reads
from `docket.toml`, and `config.py` says in its own docstring that it exists
"so the package is usable outside the repository it grew in".

**Why it matters.** It is the only thing standing between the package and a
second project, and it fails quietly rather than loudly: a project using a
different prefix gets ids that generate, files that write, and a `flight`
command that silently recognizes no branch as carrying work, because the
regex matches nothing. Nothing errors.

Small enough to be worth doing at the moment a second consumer appears, and
not before: with one consumer the setting has no second value to be tested
against, and an untested configuration seam is a claim rather than a feature.

**Where.** `store.py` (`ID_PREFIX`, used by `new_id` and the filename shape),
`vcs.py` (`BRANCH_ID_RE`, which also encodes the id *shape* — three digits or
four consonant-safe characters), `config.py` and `docket.toml`.

**Done when.** A project can set its own prefix in `docket.toml` and have id
generation, filenames and branch detection all follow it, with a test
covering a prefix that is not `PL-`.
