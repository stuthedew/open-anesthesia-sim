---
id: PL-CMCB
title: The ten type: ignore directives all sit in tests/, outside the mypy gate, so warn_unused_ignores never evaluates them
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: tests/unit/test_simulation_view.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_verify.py
added: 2026-08-31
not-delegable: the deliverable is a verdict on ten suppressions, not an exit code - mypy over the test trees reports dozens of pre-existing errors either way, so "which of these ignores is inert" is read out of its output rather than returned by it, and the prose recording why a live one stays is a judgment
---

**Problem.** `grep -rn 'type: *ignore' --include='*.py'` finds twelve hits.
Two are not directives - `subprojects/docket/src/docket/verify.py:43` holds
the string in its `SUPPRESSIONS` tuple, and
`subprojects/docket/tests/test_release.py:139` names it in prose. The other
ten are real directives, and every one of them is under `tests/` or
`subprojects/docket/tests/`:

```
subprojects/docket/tests/test_cli.py:199, :217      [attr-defined]
subprojects/docket/tests/test_checks.py:40          [arg-type]
subprojects/docket/tests/test_model.py:36           [arg-type]
subprojects/docket/tests/test_plan.py:242           [arg-type]
subprojects/docket/tests/test_verify.py:72, :80     [arg-type]
tests/unit/test_simulation_view.py:1000, :1146      [method-assign]
```

(`subprojects/docket/tests/test_verify.py:133` is an eleventh occurrence, but
inside a string literal that is written into a fixture file, not a directive
on the line it appears on.)

`[tool.mypy] files` is `["src", "tools", "subprojects/docket/src"]`, so mypy
never reads any of those files. `strict = true` enables
`warn_unused_ignores`, but a directive in a file outside `files` is never
evaluated by it, so none of these ten has ever been checked. Any of them
could already suppress nothing.

**Why it matters.** This is exactly the defect PL-ZN0N and PL-69J3 just
cleared for `noqa`, arriving through the other tool. An inert `type: ignore`
reads as a deliberate exemption and is not one, and the reader who trusts it
concludes the type checker has an opinion here when it has never looked.
The `noqa` half was only found because someone ran the rule by hand; nothing
runs this one at all.

**Where.** The ten sites above, and `pyproject.toml`'s `[tool.mypy] files`.

**Approach.** Do not start by widening `files` to include `tests`. The
comment above `files` records the measurement that argues against it - 39
errors in 7 files, 27 of them `[arg-type]` in `test_simulation_view.py` where
hand-built doubles stand in for Flet's `Page` and `Control` - and that
comment is the standing decision, not an oversight to correct.

The cheap first pass is a measurement rather than a change: run mypy over the
test tree once, by hand and out of the gate, with `warn_unused_ignores` on,
and see which of the ten are inert. That answers whether there is a problem
at all, and it costs one command. If some are inert, delete them and record
the reason for the rest as prose, exactly as PL-69J3 did. Whether the gate
should then be widened is a separate question with the cost the `files`
comment already names, and belongs in its own item.

Note the two `[method-assign]` directives in `tests/unit/test_simulation_view.py`
are the likeliest to be live - they rebind a bound method on an instance,
which mypy does reject - and the four `[arg-type]` ones construct a model
from `**base`, which is the pattern the `files` comment calls "the gate
arguing with a required practice".

**Done when.** Each of the ten directives is known to be live or has been
removed, the live ones say why in prose where the reason is not obvious, and
the decision about `[tool.mypy] files` is either taken or written down as a
separate item.

**Triaged 2026-08-31.** P3, `infra`, `dev-tooling`, and `not-delegable` rather
than carrying a `verify:` command - see the front matter for why. P3 rather
than P2 because the directives are inert *reporting*, not inert *checking*:
the gate covers `src`, `tools` and `subprojects/docket/src` and is unaffected
by anything under `tests/`, so nothing type-checked is going unchecked. It is
the same band `PL-ZN0N` and `PL-69J3` were given for the `noqa` half of the
identical problem, and it should not be started ahead of them being the
precedent.

`pyproject.toml` is deliberately absent from `touches`: widening
`[tool.mypy] files` is the separate item the Done-when names, and the standing
decision recorded in the comment above `files` is not this item's to overturn.
The first pass is a measurement out of the gate, which changes no file at all.

Not admitted to v0.2.8's frozen list: it completes no entry on it. `PL-020`
(widen the type-check gate past `src`) is the nearest, and it is `done` and
bounded to the paths it named.
