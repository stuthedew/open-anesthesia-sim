---
id: PL-W5LG
title: Hold CI config to the same path checks as the documentation
priority: P2
effort: S
status: done
classes: infra, session-cost
feature: dev-tooling
touches: tools/doc_check.py, .github/workflows/quality.yml, tests/unit/test_doc_check.py
verify: uv run pytest tests/unit/test_doc_check.py
added: 2026-08-24
pr: 106
closed: 2026-08-31
---

**Problem.** `tools/doc_check.py` resolves every path cited in the
documentation, so deleting a file is caught immediately wherever a document
mentions it. It does not look at `.github/workflows/`, which references
repository scripts by path in `run:` steps. When `tools/punch_list.py` was
deleted, every documentation reference was reported and fixed, while the CI
step invoking it was missed entirely and would have failed on merge.

**Why it matters.** A broken CI reference is found at the worst possible
moment - after review, on the merge - and the checker that exists precisely to
prevent stale path references had no visibility into it. The gap is narrow and
the fix is small, but the failure mode is a red build on `main`.

**Where.** `tools/doc_check.py` (`DOC_GLOBS` covers markdown only),
`.github/workflows/quality.yml`.

**First step.** Decide the mechanism. The existing citation checker reads
backticked paths and markdown links, neither of which appears in YAML, so this
is a separate check rather than another glob: parse `run:` steps for tokens
that look like repository paths and assert each resolves.

**Done when.** Deleting or moving a script referenced by a CI step fails
`make check` locally, before the change reaches CI.

**Context.** Found while sweeping for references to the retired punch list.
The documentation sweep was clean at the time, which is what made the gap
worth recording rather than just fixing the one line.
