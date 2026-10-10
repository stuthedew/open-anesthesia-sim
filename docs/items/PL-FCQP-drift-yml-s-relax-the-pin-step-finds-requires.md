---
id: PL-FCQP
title: drift.yml's relax-the-pin step finds requires-python in pyproject.toml with a regex anchored per line, so a requires-python-shaped line inside a multi-line string ahead of the key is rewritten in its place while the real pin stays, and the step's one-match guard passes; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: .github/workflows/drift.yml, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1389
payoff: the drift job refuses a pyproject.toml whose parsed interpreter pin it did not relax, so it cannot test the pinned interpreter while its guard reports the pin relaxed
verify: grep -q tomllib .github/workflows/drift.yml && grep -qF '"drift pin, a requires-python line inside a multi-line string' tests/unit/test_doc_check.py
---

**Problem.** drift.yml's relax-the-pin step finds requires-python in pyproject.toml with a regex anchored per line, so a requires-python-shaped line inside a multi-line string ahead of the key is rewritten in its place while the real pin stays, and the step's one-match guard passes; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), reaching past
the earlier sweeps into the workflows' own `run:` scripts. The step that lets
the drift job test the next CPython rewrites `pyproject.toml` with `re.subn` of
a pattern anchored at line starts (`re.M`), `count=1`, and raises unless it made
one substitution. TOML 1.0 lets a multi-line string hold any line, a
`requires-python = "..."` one included, and such a line is the string's
content, not the key.

**Reproduced 2026-10-06** against python3 3.11.15's `tomllib`, running the
step's own code over a `pyproject.toml` whose `[project]` table holds, ahead of
the key, a multi-line string with a line shaped like it:

```text
[project]
name = "x"
description = """
requires-python = "anything"
"""
requires-python = ">=3.14,<3.15"
```

The substitution rewrote the line inside the string, so `n == 1` and the guard
passed, and `tomllib` still read `requires-python` as `>=3.14,<3.15`. The key's
own value written as a multi-line string gives `n == 0`, and the step raises
naming the shape, so that form is declined by name. Latent:
`pyproject.toml` holds no multi-line string, and the consequence would surface
a step later, as uv refusing or the next step reporting the pinned series.

**Why it matters.** The drift job is the project's monthly warning that the
next CPython breaks the build, and the step's guard is what stops it testing
the pinned interpreter while saying otherwise. Rewriting a line inside a
string instead of the key, the step passes its own guard with the pin
unchanged, so the job fails a step later for a reason it does not name, or
reports the pinned series as though nothing newer existed.

**Generator check.** A member of `PL-R417`: a reader takes a physical line for a
TOML statement where a multi-line string carries one across it, the fact
`PL-3DD9`, a member, fixed in `version_in`. The workflows' `run:` scripts were
outside the earlier sweeps' reach.

**Done when.** The step reads and checks the key with `tomllib` before writing,
refusing a file whose parsed `requires-python` it did not change, and the
`drift.yml` change is held for the owner's read as a workflow edit.

**Built 2026-10-10 (`#1389`).** The step still finds the line with the
anchored pattern, since `tomllib` reads TOML and writes none, and now reads its
rewrite back with `tomllib` before writing it: the parsed `requires-python` has
to be the relaxed bound and every other value in the file the same, or the
step raises naming the pin TOML still reads. Two `drift pin, ` cases in
`PL-R417`'s guard run the step's own script, cut out of `drift.yml` at its
heredoc: the multi-line string fixture above is refused, where main's step
wrote the file with the pin unchanged, and the project's own `pyproject.toml`
is relaxed to `>=3.14`. The `drift.yml` change holds the pull request for the
owner's read, as the Done-when asks.
