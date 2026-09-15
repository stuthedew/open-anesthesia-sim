---
id: PL-9TNJ
title: Decide whether to report the I001-plus-cache interaction to astral-sh/ruff: #5449 has the same root cause open for INP001 only, and PL-QSJM established both halves (match_sources probes the full dotted path, FileCacheKey is mtime and mode alone)
priority: P3
effort: S
status: needs-decision
classes: infra
feature: dev-tooling
touches: docs/items
added: 2026-09-15
---

**Problem.** Decide whether to report the I001-plus-cache interaction to astral-sh/ruff: #5449 has the same root cause open for INP001 only, and PL-QSJM established both halves (match_sources probes the full dotted path, FileCacheKey is mtime and mode alone)

**What PL-QSJM established, 2026-09-15.** Both halves of the mechanism, verified
against ruff 0.16.4 and its source:

- isort's `match_sources` resolves first-party by probing the **full dotted
  path** under the `src` roots, so one file's verdict depends on whether a
  different file exists.
- ruff's `FileCacheKey` is the linted file's **mtime and permission bits alone** -
  no content hash, no reference to any other path.

So deleting a module leaves every file importing it replaying a clean verdict it
can no longer earn. Reproduced in a minimal tree and on this repository at
`abf855b2`; the delete direction goes stale, the add direction does not.

**Why it matters.** astral-sh/ruff#5449 is open and names the same root cause
for `INP001` - "we don't invalidate the cache when an `__init__.py` is added or
removed" - assigned, with no comments since. Nothing upstream covers the `I001`
case, and ruff's documentation describes cache invalidation nowhere. A report
carrying both halves is a genuinely new one rather than a duplicate, and if it
lands, this project stops carrying `--no-cache` and the 27 ms that go with it.

**Decision needed.** Whether to spend the time filing it upstream. This is the
project owner's call rather than a session's, because it is the first thing this
project would publish into another project's tracker under its own name, and
`ROADMAP.md`'s public-facing pass is deliberately not yet due (`PL-XYRN`). The
three options: file it with the reproduction above; say nothing and keep the
local fix; or comment the `I001` reproduction onto #5449 rather than opening a
new issue, which is cheaper and risks being read as a different bug. No
engineering here depends on the answer - `PL-QSJM` is closed and the gate is
correct either way.

**Done when.** The owner has chosen, and this item carries either the issue or
comment URL, or a `reason` recording the decision not to report and this item is
dropped.
