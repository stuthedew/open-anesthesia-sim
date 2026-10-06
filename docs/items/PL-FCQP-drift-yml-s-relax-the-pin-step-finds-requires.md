---
id: PL-FCQP
title: drift.yml's relax-the-pin step finds requires-python in pyproject.toml with a regex anchored per line, so a requires-python-shaped line inside a multi-line string ahead of the key is rewritten in its place while the real pin stays, and the step's one-match guard passes; latent
status: untriaged
feature: one-answer
added: 2026-10-06
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

**Generator check.** A member of `PL-R417`: a reader takes a physical line for a
TOML statement where a multi-line string carries one across it, the fact
`PL-3DD9`, a member, fixed in `version_in`. The workflows' `run:` scripts were
outside the earlier sweeps' reach.

**Done when.** The step reads and checks the key with `tomllib` before writing,
refusing a file whose parsed `requires-python` it did not change, and the
`drift.yml` change is held for the owner's read as a workflow edit.
