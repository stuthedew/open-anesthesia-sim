---
id: PL-8PT6
title: subprojects/docket/uv.lock is not gitignored, so running uv from inside the subproject leaves an untracked lockfile a git add -A would commit
priority: P3
effort: S
status: done
classes: infra
touches: .gitignore, subprojects/docket/README.md
added: 2026-09-13
closed: 2026-09-13
pr: 515
verify: python3 tools/doc_check.py check && git check-ignore -q subprojects/docket/uv.lock
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

**Decided 2026-09-13 by the project owner: both halves.** Ignore the path, and
say where the tests run.

**Ignoring it alone was the tempting answer and is the weaker one**, for a
reason worth recording: it fixes the wrong *commit* and makes the wrong *run*
harder to notice. `.venv/` was already ignored, so the untracked `uv.lock`
appearing in `git status` was the only visible sign that a second environment
existed at all. Ignoring that too buys a clean `git status` at the cost of the
last symptom - and the run is the half that matters, because tests passing
against a dependency set nobody reviewed and CI never runs is a weaker answer
wearing the same green tick.

So the ignore is paired with a `## Running the tests` section in
`subprojects/docket/README.md` that states the root invocation, says why
(`testpaths` and `pythonpath` in the root `pyproject.toml` already put these
tests in the root suite), and names the wrong invocation explicitly along with
what it leaves behind. Naming the wrong one matters: `cd subprojects/docket &&
uv run pytest` is the *obvious* command when the files being edited are there,
which is exactly how this session reached it.

**The ignore is anchored, not bare.** `/subprojects/docket/uv.lock` rather than
`uv.lock`, because the root lockfile is tracked and a bare pattern would match
it too. Tracked files are not un-tracked by a later ignore rule, so nothing
would have broken immediately - which is what makes the bare form the
dangerous version rather than the obviously wrong one.

**Measured 2026-09-13.** With a stray `subprojects/docket/uv.lock` present,
`git status --short` and `git add -A --dry-run` both report it zero times;
before the rule it appeared as `??` and would have been staged. The `verify:`
command was watched failing with `.gitignore` stashed and passing with it
restored.

**Not built: a check that fails on the stray file's presence.** It was the
first thing considered, since `CLAUDE.md` routes a decidable rule to a script
before prose. It was refused because this README calls the package standalone
and means it - somebody developing `docket` on its own has a legitimate reason
for a venv here, and a `make check` that failed on one would forbid a
supported workflow to prevent a mistake the two cheaper halves already cover.
