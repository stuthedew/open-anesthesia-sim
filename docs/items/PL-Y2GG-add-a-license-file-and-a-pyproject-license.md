---
id: PL-Y2GG
title: Add a LICENSE file and a pyproject license field before the repository goes public
priority: P2
effort: S
status: needs-decision
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

**Decision needed.** Which license. This is the project owner's call and not
a default to be picked on their behalf, which is why this item sits at
`needs-decision` rather than `ready`. The recommendation is a permissive
license with an explicit no-warranty clause - MIT or Apache-2.0 - because the
educational-not-clinical disclaimer needs the warranty disclaimer to have
legal force behind it as well as documentary force, and because a permissive
license is what lets the cited model and its provenance be reused in teaching
material without a further conversation. Apache-2.0 over MIT if an explicit
patent grant is wanted; MIT if brevity matters more. A copyleft license is the
alternative if the priority is that derived simulators stay open, at the cost
of making reuse inside institutional teaching software harder.

**Done when.** A license is chosen by the project owner, present as `LICENSE`,
declared in `pyproject.toml`, and stated in `README.md`.
