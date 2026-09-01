---
id: PL-768D
title: The tools/ import guard reads the running interpreter's stdlib, not the floor's
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: dev-tooling
touches: tests/unit/test_tools_portability.py, .github/workflows/quality.yml
added: 2026-09-01
---

**Problem.** `tests/unit/test_tools_portability.py`'s import guard, added by
`PL-QDH7`, allows any name in `sys.stdlib_module_names`. That frozenset is the
standard library of the interpreter *running the test* - the project
virtualenv, on the 3.14 `pyproject.toml` pins - not of the 3.11 floor
`subprojects/docket/pyproject.toml` declares, which is the interpreter the
tools actually have to run under. A module added to the standard library
between the two is therefore allowed by the guard and absent where it matters.
Demonstrable in one command in this container, where bare `python3` really is
3.11.15 and the virtualenv 3.14.7: `annotationlib` and `compression` are in
3.14's set and not in 3.11's.

**Why it matters.** It is a hole in a guard whose entire purpose is closing
one, and it fails *open* - the guard passes and `make check`'s final
`python3 tools/doc_check.py check` raises `ModuleNotFoundError`, which is the
exact failure `PL-QDH7` was written to prevent. The reverse direction is safe:
a module removed after the floor (PEP 594's dead batteries) is missing from the
running interpreter's set and rejected here while still importable at the
floor, which is a false positive and loud.

The same gap runs one level up, and triage is where it became visible.
**Nothing in CI runs either tree at the floor at all.**
`.github/workflows/quality.yml` runs `uv run python tools/doc_check.py check`
under the virtualenv, and `bin/docket check` under whatever system `python3`
the runner image ships - neither pinned to 3.11. So both portability suites are
*approximations of a run nobody performs there*: the parse test's
`feature_version=floor` gates the syntax CPython version-checks rather than
parsing as 3.11 would, and the import test reads the wrong interpreter's
stdlib. Locally the real thing does happen - `make check`'s last line is a
genuine 3.11 invocation in this container, and that is what caught the original
`SyntaxError` on 2026-08-31, per `tools/ruff.toml`'s own account. CI is the
half with no such backstop.

Narrow on the module-set question alone: CPython added two top-level modules
across 3.12-3.14, and neither is one a documentation checker would reach for.
Not narrow once the CI gap is counted with it.

**Where.** `tests/unit/test_tools_portability.py` - the `VENDORED` frozenset
and `test_no_tool_imports_outside_the_standard_library` beside it, whose
docstring names the bound and both live examples and would need that paragraph
deleted. `.github/workflows/quality.yml` if the route below is taken.
`subprojects/docket/tests/test_portability.py` carries the same approximation
for its own tree and is in scope for the same fix.

**Done when.** Nothing under `tools/` can reach a module the floor interpreter
lacks without a check failing, and no test docstring records the gap as still
open. Stated as the outcome rather than as a mechanism because the mechanism is
the open decision below.

**Decision needed.** Which mechanism closes it - and whether the fix is the
test or CI? The four routes are below with a recommendation, and the choice is
not a detail of implementation: routes 1-3 edit an assertion in
`tests/unit/test_tools_portability.py`, route 4 leaves that assertion as it is
and adds a CI job that makes it non-load-bearing. They rewrite **Done when**
differently and touch different files. No measurement is outstanding; what the
answer needs is on the record here.

**Options.** The standard library carries no versioned module index, so nothing
derives the floor's set the way `sys.stdlib_module_names` derives the running
one. Three routes were recorded at capture; a fourth surfaced at triage and is
the recommendation.

1. **Subtract a hand-written set of post-floor names.** Closes it exactly
   today. Rejected on reflection: the set has to cover every module added
   between the floor and whatever interpreter runs the suite, *forever*, so
   each Python upgrade silently reopens the same fail-open hole until somebody
   remembers to extend it. A guard that re-creates its own bug on every upgrade
   is the wrong shape for this.
2. **Ask the bare `python3` on PATH for its own `sys.stdlib_module_names` by
   subprocess.** Answers for the interpreter `make check` really uses, but
   makes a gate's verdict depend on the machine it runs on, and buys nothing in
   CI where that interpreter is not the floor either.
3. **Accept the bound and drop this with a reason.** Defensible on the module
   set alone; not once the CI gap above is counted.
4. **Run both trees at the floor in CI - recommended.** A second job in
   `.github/workflows/quality.yml`: `actions/checkout`, `actions/setup-python`
   at 3.11, then `python3 tools/doc_check.py check` and `bin/docket check`.
   That tests the promise rather than approximating it - imports, syntax and
   runtime behavior at once, with no allowlist, no staleness and nothing to
   maintain as the standard library moves. It is green today: both commands
   were run at 3.11.15 in this container during triage and exit 0, so it lands
   as a guard rather than as a fix. `actions/setup-python` is safe here where
   `setup-uv`'s `python-version:` input is not - the workflow's existing
   comment warns about the latter setting `UV_PYTHON`, which a separate job not
   using uv never touches.

   It does not replace the two portability suites: they run in `make check`
   before a push, name the offending file and import, and catch a
   lazily-imported module inside a branch the CI run never takes. What it does
   is make their approximations no longer load-bearing, which is what lets this
   item's docstring paragraph go.

**Triaged 2026-09-01.** P2, `defect`/`infra`, `dev-tooling`, beside `PL-QDH7`
which created the guard. `needs-decision` rather than `ready`, so `bin/docket
next` does not offer it and no `verify:` is owed until the mechanism is settled
- it differs per route, and the rule is to run one and watch it fail before
writing it down. `touches` names both candidate files, which is the
conservative answer for concurrency while the route is open. Captured after
v0.2.8's gate was frozen, so it belongs to the next gate rather than this one.
