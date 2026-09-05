---
id: PL-PVHD
title: Move CI to the self-hosted runner while the repository is private
status: untriaged
feature: ci-cost
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-05
---

**Problem.** Move CI to the self-hosted runner while the repository is private

**Why it matters.**

**Where.**

**Done when.**

**Blocked on the runner's provisioning, diagnosed 2026-09-05 on #357 head
`8a9df1a`.** The workflow change is correct; the host cannot yet run it. Three
problems, and the first is the one that matters:

1. **`git` is not on the runner's PATH.** `actions/checkout` fell back to
   `The repository will be downloaded using the GitHub REST API`, so the
   workspace has no `.git` at all. `fetch-depth: 0` becomes a no-op and every
   history-dependent check loses its input. This is worse than the visible
   failure: `bin/docket check` and `tools/doc_check.py` *decline* their history
   reads rather than erroring, so fixing only problem 3 would yield a green run
   that verified materially less than it claims. The `fetch-depth: 0` comment
   on the `checks` job and `PL-99Y4` are about exactly this failure mode.
2. **`/usr/sbin/pwrstat` is on PATH as though it were a directory**, giving
   `ENOTDIR` on every executable lookup. Almost certainly `/usr/sbin` was
   meant. Likely the cause of 1.
3. **`actions/setup-python` cannot supply 3.11 on Debian 12** - `actions/python-versions`
   publishes prebuilt CPython for Ubuntu only. Debian 12's own `python3` is
   already 3.11, so the interpreter exists; the action's download path has
   nothing to fetch. This is the open design question rather than a
   configuration fix: using the system `python3` would arguably serve the
   `floor` job's bare-interpreter contract better than a downloaded build, but
   it couples the declared floor to the host OS, and
   `tests/unit/test_tools_portability.py` holds the workflow's concrete pin to
   `subprojects/docket/pyproject.toml`'s `requires-python`.
