---
id: PL-PG0S
title: No check or CI job runs the mutation tool's first step, so a new unit test that cannot run inside the mutation copy of the tree stops every mutation run until a session next needs one: PL-GP8G's two tests and PL-CTXZ's deselected test, in the week of 2026-11-09
status: untriaged
added: 2026-11-11
---

**Problem.** No check or CI job runs the mutation tool's first step, so a new unit test that cannot run inside the mutation copy of the tree stops every mutation run until a session next needs one: PL-GP8G's two tests and PL-CTXZ's deselected test, in the week of 2026-11-09

**What happens.** mutmut first runs the selected unit tests inside `mutants/`, a copy of the tree. A unit test that reads a file the copy does not hold, or that lists the functions of a model module, fails there and passes everywhere else. `make check` and `quality.yml` never run that step, so the mutation check stays broken until a session's close-out next needs it. `PL-GP8G` found two such tests that landed on 2026-11-09 and 2026-11-11. `PL-CTXZ`'s branch deselects a third and records that while it ran under mutmut "no mutant was tried on any branch". `PL-R8HY` records that the same first step took about 19 minutes on 2026-11-11 where the tool's docstring says about two and a half.

This is a finding about workflow tooling, so the pause on new workflow mechanisms applies to any new check. Found by the unit-testing review of 2026-11-11.
