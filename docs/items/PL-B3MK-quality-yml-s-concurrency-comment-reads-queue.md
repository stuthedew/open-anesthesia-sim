---
id: PL-B3MK
title: quality.yml's concurrency comment reads queue: max from SchemaStore because docs.github.com and github.blog are blocked, but docs.github.com answered on 2026-10-05 (github.blog is still refused at CONNECT), so the claim can be checked against GitHub's own prose and the comment re-dated
status: untriaged
touches: .github/workflows/quality.yml
added: 2026-10-05
---

**Problem.** quality.yml's concurrency comment reads queue: max from SchemaStore because docs.github.com and github.blog are blocked, but docs.github.com answered on 2026-10-05 (github.blog is still refused at CONNECT), so the claim can be checked against GitHub's own prose and the comment re-dated

**Found 2026-10-05 by `PL-848V`'s thread (`#1366`)**, which read GitHub's
workflow syntax and trigger pages on docs.github.com for its trigger reader.
Probed from the cloud container that day: `curl` to
`https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions`
answered 301 past CONNECT, and `https://github.blog/` was refused at CONNECT
(403). The comment is the one above `concurrency:` in
`.github/workflows/quality.yml`, reading "are both blocked by this container's
egress proxy"; `tests/unit/test_ci_concurrency.py` holds the group to it.
Whether `queue: max` can be scoped by expression, and whether it combines with
`cancel-in-progress`, can now be read from GitHub's own prose rather than the
schema's declaration, and the comment can say when the hosts were measured.
