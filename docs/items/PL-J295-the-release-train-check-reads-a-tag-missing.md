---
id: PL-J295
title: The release-train check reads a tag missing from a shallow clone as a release that was never tagged
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
milestone: v0.2.8
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-08-31
verify: uv run pytest tests/unit/test_doc_check.py -k shallow
---

**Problem.** `make check` fails in a fresh web-session container, on `main`,
with no local changes:

```
FAILED tests/unit/test_doc_check.py::test_this_repository_is_clean
  ROADMAP.md:37: v0.0.1 is marked completed but git holds no tag for it,
  so no commit in its span maps to the release it went out in
```

...and seven more like it. The tags are not missing. The container clones
shallowly, the older tags point at commits outside the fetched depth, so
`git tag --list` returns 3 of the repository's 11. Measured 2026-08-31:
`git fetch --tags` then re-running the same test passes in 0.10s.

**This is `PL-XCYB` again, one reader over.** That entry — already admitted to
v0.2.8's frozen list — established that a check must refuse to answer in a
shallow checkout rather than answer wrongly, and `merged_pull_requests` now
declines with its reason. `vcs.tags()` has the identical exposure and no such
guard, so the release-train check reads "not fetched" as "never tagged". The
docstring on `tags()` even anticipates the caller-decides problem for the
*empty* case and stops one step short of the partial one, which is the case
that actually fires: with zero tags `is_untagged` correctly reads "this project
does not tag", and with three of eleven it confidently reports eight false
findings.

**Why it matters.** It is also why this is first. Every session must run `make check`
before finishing or committing, and every web session starts from a shallow
clone. So every session either spends the diagnosis this one spent — read the
failure, doubt its own diff, stash, re-run, compare against the remote — or,
worse, learns that a red suite here is background noise and stops reading it.
That is the failure mode that makes every later check worthless.

The arithmetic is the compounding-friction test in `CLAUDE.md`: a few minutes
of diagnosis, or one wrongly-trusted red suite, times every remaining session
in v0.2.8, v0.3.0 and v0.4.0. Deferring it is a decision to pay it that many
more times, so it is recommended now rather than filed.

**Where.** `tools/doc_check.py`'s release-train check. The fix follows the
precedent `PL-XCYB` set rather than inventing one: decline when the checkout
cannot see the whole tag set, reporting a check that did not run, instead of
reporting every unreachable tag as a missing one. Fetching tags in the
session-start hook is a workaround for this container, not a fix — a bare or
offline checkout still misreports.

**Done when.** `make check` passes in a fresh shallow container against
unmodified `main`; the release-train check names its refusal when the tag set
is incomplete rather than reporting findings; and a test covers the shallow
case the way `test_a_shallow_clone_declines_and_says_why` covers `PL-XCYB`'s.
