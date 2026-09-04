---
id: PL-Y0RZ
title: Nothing enforces that only core/parameters.py imports Pydantic
priority: P2
effort: S
status: done
classes: infra, docs
feature: core-boundaries
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py, Makefile, .github/workflows/quality.yml, docket.toml, src/anesthesia_sim/core/parameters.py
added: 2026-09-02
closed: 2026-09-04
pr: 289
verify: uv run pytest tests/unit/test_parameters.py && grep -q 'import_boundary_check' Makefile
---

**Problem.** The invariant holds today — `grep -rn pydantic src/anesthesia_sim/`
returns hits only in `core/parameters.py` — but nothing checks it. Any later
change could import `pydantic` into `core/circuit.py`, a compartment, or the
controller, and every gate would stay green.

**Why it matters.** That boundary is the entire reason the
`_...Payload`/public-dataclass pairs exist, which PL-007 has just written down
at each payload class and on `_StrictPayload`: a payload validates one JSON
document and is discarded, so what the rest of the core holds is a plain
frozen dataclass with no dependency on the validation library. If Pydantic
leaks into a compartment, the pairs stop buying anything and the
documentation asserting they do becomes false — the worse of the two
outcomes, because it reads as verified when it is not. `CLAUDE.md` names
exactly this shape: a claim answerable by reading the tree belongs in a
script rather than in prose that nobody re-measures.

**Where.** `src/anesthesia_sim/core/` and `src/anesthesia_sim/app/`;
`src/anesthesia_sim/core/parameters.py` is the one module allowed the import,
and `_StrictPayload`'s docstring is the prose this would keep honest.

**Approach.** A standard-library check, in the shape `tools/` already uses:
walk `src/anesthesia_sim/**/*.py` with `ast`, collect every `import` and
`from ... import`, and fail on a `pydantic` root outside the allowed module.
`tools/contrast_check.py` reads `app/` with `ast` rather than importing it and
is the model to follow, including staying importable by a bare `python3`.
Whether `app/` should also be forbidden the import is the judgment: the core
boundary is the one the pairs exist for, but the interface has no business
holding validation models either.

**Named at triage:** `tools/import_boundary_check.py`, so the `verify:`
command can name it. Change the name freely - the command is what would then
need updating, not a commitment.

**On the `verify:` command.** The `grep` is over the `Makefile` rather than
over the tool, deliberately: a tool that exists but is not wired into `make
check` enforces nothing, and "fails `make check`" is what the Done-when
actually says. `tests/unit/test_parameters.py` is the paired half that passes
today and covers the module the boundary exists to protect; it runs in 0.13 s,
so it costs nothing inside `docket check`.

**Done when.** A Pydantic import outside the allowed module fails
`make check`, and the allowed module is named in one place a reader can find.

**Resolved 2026-09-04.** `tools/import_boundary_check.py` walks every module
under `src/anesthesia_sim/` with `ast` and fails on a `pydantic` root outside
`core/parameters.py`. It reports three further states as errors, each closing a
way the check could pass while meaning nothing: an `allowed` entry naming a
file that no longer exists (a rename would otherwise move the exception
somewhere nothing checks), an `allowed` entry that no longer makes the import
(an exception outliving its reason - `contrast_check.py`'s
shortfall-that-starts-passing rule, applied to allowances), and a declared tree
matching no source files at all (a moved package leaves the walk with nothing
to inspect, and passing over nothing is indistinguishable from passing).

**The `app/` judgment, which this item left open: forbidden there too.** The
pairs exist for `core/`, so `core/` is the half with an argument behind it. The
interface is included because nothing supplies a reason for the asymmetry -
`app/` reads parameters through the same seam functions, as already-validated
frozen dataclasses, so an import there would be new coupling buying nothing.
One allowed-module list also makes the rule statable in a sentence, *exactly
one module in this package imports Pydantic*, where "forbidden here, permitted
there" is a rule a reader has to look up.

Two smaller calls, both recorded in the module docstring: a `TYPE_CHECKING`-
guarded import counts (the property is about the types a module's API mentions,
not only about what it loads at runtime), and `import_module("pydantic")` with
a literal name counts, while a computed name is a stated limit rather than a
gap to close - the guard is against an accident, not against evasion.

**It runs under `uv run python`, not the bare `python3` the other tools use**,
and that is about the input rather than the tool. `src/` targets 3.14;
`app/chart_downsampling.py`'s PEP 695 `def first_index_at_or_after[SampleT](`
is a `SyntaxError` to the 3.11 parser `tools/` promises to run under, and
`ast.parse`'s `feature_version` only narrows accepted syntax rather than
extending it. So the parser has to be the one the source is written for.
`tools/ignore_check.py` is the same category for a different reason; the tool
itself stays standard-library-only and parses at the floor, which is what
`tests/unit/test_tools_portability.py` holds it to.

That finding generalizes past this item and is captured as `PL-L17Q`:
`contrast_check.py` runs in CI's `floor` job and reads `app/` with `ast`,
working today only because the two files it reads happen to carry no 3.12+
syntax. `PL-JRV5` is the same finding framed around the wrong fix, dropped
against `PL-L17Q`.

`_StrictPayload`'s docstring now names the check, so the prose asserting the
property points at the thing that measures it.
