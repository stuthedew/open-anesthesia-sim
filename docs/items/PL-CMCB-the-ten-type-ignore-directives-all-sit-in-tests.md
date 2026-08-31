---
id: PL-CMCB
title: The ten type: ignore directives all sit in tests/, outside the mypy gate, so warn_unused_ignores never evaluates them
status: untriaged
added: 2026-08-31
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
