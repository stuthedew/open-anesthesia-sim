---
id: PL-8PT6
title: subprojects/docket/uv.lock is not gitignored, so running uv from inside the subproject leaves an untracked lockfile a git add -A would commit
status: untriaged
added: 2026-09-13
---

**Problem.** subprojects/docket/uv.lock is not gitignored, so running uv from inside the subproject leaves an untracked lockfile a git add -A would commit

**Why it matters.** `subprojects/docket/` is a standalone package with its own
`pyproject.toml`, so `uv run` works from inside it - and doing so bootstraps a
private `.venv` **and writes a `uv.lock` that has never existed in this
repository** (`git log -- subprojects/docket/uv.lock` is empty; `git ls-files`
does not list it). `.gitignore` covers `.venv/`, so the environment is
invisible, but the lockfile is left untracked and a `git add -A` - which is how
this project's sessions routinely stage a batch - would commit it.

That would be a wrong file rather than a harmless one. The root
`pyproject.toml` declares `testpaths = ["tests", "subprojects/docket/tests"]`
and puts `subprojects/docket/src` on `pythonpath`, so the subproject's tests
are meant to run from the repository root against the root environment. A
committed subproject lockfile would assert a second, independently resolved
dependency set that nothing installs from and nothing checks, and
`make check`'s `uv sync --locked` would not notice it.

**Observed 2026-09-13**, while working `PL-KBD0`: a session ran
`cd subprojects/docket && uv run pytest tests/test_checks.py`, which is the
obvious invocation when the tests being edited are in that directory. It
created `.venv`, `.ruff_cache` and `uv.lock`, and the lockfile then appeared in
`tools/doc_check.py candidates` output as a changed file. It was deleted rather
than committed, and the run was repeated from the root.

**Where.** `.gitignore`; the `uv.lock` line would sit beside the existing
`.venv/`.

**Decision needed.** Whether the answer is to ignore the path, or to make the
subproject harder to run from inside. Ignoring it is one line and stops the
accident reaching a commit, but leaves a session running against a second
environment whose resolution nobody reviewed - the tests would pass there and
prove less than they look like they prove. The alternative is to say somewhere
a session will read it that the subproject's tests run from the root, which is
what `testpaths` already implies and what no prose states. The two are not
exclusive and the first is cheap; the second is the one that prevents the
wrong run rather than the wrong commit.

Note the near-identical case already handled: `.ruff_cache/` is ignored at the
root and showed as `!!` in the same `git status`, so the pattern of
subproject-generated artifacts is known and this one was simply missed.
