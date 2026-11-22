---
id: PL-Q3BN
title: Describe every docket feature in one registry, show each description in status and feature, and refuse an item whose feature is not listed
status: untriaged
feature: feature-registry
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, docs/features.toml, docket.toml
added: 2026-11-22
---

**Problem.** Describe every docket feature in one registry, show each description in status and feature, and refuse an item whose feature is not listed

A docket feature is only the free-text `feature:` field on an item. Nothing in
the repository says what any of the 211 names in use covers, so a session
filing an item guesses which group it joins from the name alone, and a reader
of `bin/docket status` sees a list of names with no meaning attached. GitHub
and GitLab both keep labels as a registry, one name and one short description
each
([GitHub](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels),
[GitLab](https://docs.gitlab.com/user/project/labels)).

The project owner said yes to building it (project owner, 2026-11-22, on the
coordinator's proposal).

**Build.**

1. One registry file listing every feature any item carries, each with a
   one-line plain description of what belongs in it, written from its items.
2. `bin/docket status` and `bin/docket feature` print the description beside
   the name.
3. `bin/docket check` refuses an item whose feature is not in the registry.

**Approach.** The registry is `docs/features.toml`, one `name = "description"`
line per feature, named by a new `features_file` key in `docket.toml`. It is a
file of its own, not a table in `docket.toml`, because every new feature adds a
line to it and `docket.toml` is one of the `gate_paths` that mark a delegated
diff as having edited its own checks. The package default is empty, which
turns the check off and prints no descriptions, so a project that keeps no
registry sees no change. The check applies to closed items as well as open
ones: the registry describes every name in use, and `bin/docket feature` on a
finished feature should still say what it was.
