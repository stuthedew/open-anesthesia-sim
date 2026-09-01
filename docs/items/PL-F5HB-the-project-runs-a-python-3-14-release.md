---
id: PL-F5HB
title: The project runs a Python 3.14 release candidate, not 3.14 final
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.2.8
touches: pyproject.toml, .python-version, uv.lock, .github/workflows/quality.yml, README.md
added: 2026-08-30
closed: 2026-08-30
commit: fb81597
pr: 96
verify: uv run python -c "import sys; assert sys.version_info.releaselevel == 'final', sys.version"
---

**Problem.** The project's locked interpreter is **3.14.0rc2**, verified with
`uv run python -c "import sys; print(sys.version)"`. Python 3.14.0 final shipped
2025-10-07 and the series is at 3.14.7, so the environment every test and every
release runs on is a release candidate carrying none of the bugfix or security
releases since.

Two further things disagree with each other around it:

- `pyproject.toml`'s exact pin `pydantic==2.12.0` is justified by a comment
  naming that rc build specifically (`pydantic>=2.12.4` crashing on this
  project's compat shim), so the pin's stated reason is tied to an interpreter
  the project should not still be on.
- `.python-version` says `3.14`, which resolves forward to whatever 3.14.x is
  available, while `uv.lock` holds the rc. The two files describe different
  interpreters, and which one a contributor gets depends on their cache.

**Why it matters.** Determinism is a stated requirement of this project, and
"the same inputs give the same outputs" is only worth as much as the
reproducibility of the environment producing them. A release candidate is
explicitly not supported upstream, and the divergence between `.python-version`
and the lock means a new checkout can silently run a different interpreter from
CI. Nothing in the queue mentions any of it.

**Where.** `.python-version`, `pyproject.toml` (the `requires-python` floor and
the pydantic pin with its comment), `uv.lock`.

**Approach.** Move to the current 3.14.x, re-lock, and re-check whether the
pydantic pin's justification still holds on it — the crash it names may be
fixed, may persist, or may need re-testing against a later pydantic; whichever
it is, the comment must end up describing the interpreter actually in the lock.
Then make `.python-version` and the lock agree rather than leaving one to
resolve forward.

**Done when.** `uv run python` reports a final 3.14.x release,
`.python-version` and `uv.lock` name the same interpreter, the pydantic pin's
comment describes the build actually in use, and `make check` passes on it.
