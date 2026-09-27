---
id: PL-Y4NS
title: tests/unit/test_pr_title_check.py's two --discover tests read the real checkout's origin, because repo_slug comes from tools/open_pull_requests.py and the _git stub never reaches it, so both fail in any clone whose origin is not a GitHub URL
status: untriaged
touches: tests/unit/test_pr_title_check.py
added: 2026-09-27
---

**Problem.** tests/unit/test_pr_title_check.py's two --discover tests read the real checkout's origin, because repo_slug comes from tools/open_pull_requests.py and the _git stub never reaches it, so both fail in any clone whose origin is not a GitHub URL

**Observed 2026-09-27, by `PL-F08Y`.** Every timing run in a `git clone
--shared` of this checkout, whose `origin` is therefore a local path, failed
`test_a_stale_title_on_the_open_pull_request_fails_locally` (`main()` returned
0) and `test_a_discovered_title_that_leads_with_everything_passes` (it printed
nothing). Both pass in a checkout whose `origin` is the GitHub URL. The tests
replace `pr_title_check._git` with `_remote()`, which answers `remote get-url`
for them, but `main()`'s `--discover` branch calls `repo_slug()`, imported
from `tools/open_pull_requests.py`, which asks the real repository. With no
GitHub slug, `main()` skips silently and returns 0. The stub's own `remote
get-url` answer shows the tests meant the slug to come from it, so the fix is
most likely to stub `repo_slug` beside `_git`, or to route it through `_git`.
Any checkout whose `origin` is not a GitHub URL fails the same way: a local
clone, as here, or a mirror hosted elsewhere.
