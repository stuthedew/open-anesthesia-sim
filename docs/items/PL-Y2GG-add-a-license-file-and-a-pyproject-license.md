---
id: PL-Y2GG
title: Add a LICENSE file and a pyproject license field before the repository goes public
priority: P2
effort: S
status: ready
classes: infra
touches: LICENSE, pyproject.toml, README.md
added: 2026-08-25
---
**Problem.** The repository has no `LICENSE` file and `pyproject.toml`
declares no license field.

**Why it matters.** Without a license, the default is exclusive copyright:
nobody may use, copy, modify or redistribute the code, which contradicts what
`README.md` says the project is ("An open-source, deterministic anesthesia
simulation for education"). This blocks the repository going public, and it
blocks any citation or reuse in a teaching setting, which is the project's
stated purpose. It also has to be settled *before* outside contributions
arrive rather than after, since relicensing later needs every contributor's
agreement.

**Where.** A new `LICENSE` at the repository root, the `license` and
`license-files` fields in `pyproject.toml`, and the statement in `README.md`.

**First step.** The license choice is the project owner's, not a default to be
picked on their behalf. The scientific-provenance obligations in `CLAUDE.md`
argue for a permissive license with an explicit no-warranty clause given the
educational-not-clinical disclaimer, but that is a recommendation and not a
decision.

**Done when.** A license is chosen by the project owner, present as `LICENSE`,
declared in `pyproject.toml`, and stated in `README.md`.
