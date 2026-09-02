---
id: PL-QSWS
title: No item or roadmap entry covers dependency and toolchain drift, which a multi-year horizon makes a certainty rather than a risk
priority: P2
effort: S
status: needs-decision
classes: infra
feature: dev-tooling
touches: pyproject.toml, .github/workflows/quality.yml
added: 2026-09-02
---

**Problem.** Nothing in `docs/items/` or `ROADMAP.md` says what happens when
this project's dependencies move. Searched 2026-09-02: no open item mentions an
upgrade, a deprecation or an end-of-life, and `ROADMAP.md` contains no horizon
language at all. Every version constraint in `pyproject.toml` was written for
the version that was current when it was written:

- `requires-python = ">=3.14,<3.15"` — a single minor version, and
  `[tool.ruff] target-version = "py314"` and `[tool.mypy] python_version =
  "3.14"` repeat it. CPython ships a minor release a year, so this pin is
  wrong within twelve months and wrong three to five times over the horizon.
- `flet[all]>=0.86,<1.0` and `flet-charts>=0.86,<1.0` — Flet is **pre-1.0**.
  The upper bound excludes the release most likely to break the entire
  presentation layer, and says nothing about what to do when it arrives.
- `pydantic>=2.12.4,<3.0` — pydantic 3 is excluded by the same shape.
- `mypy>=2.3.1`, `pytest>=9.1.1`, `ruff>=0.16.4` are floors with no ceiling,
  so the quality gate's behaviour changes under the project without notice.

**Why it matters.** `CLAUDE.md` names the failure this project guards against
as effort abandoned when the codebase becomes unmanageable. Over one year,
frozen pins are a reasonable answer and drift is somebody else's problem. Over
several, they are the mechanism: the tree stops building on a current
interpreter, the upgrade that would fix it is now four versions wide, and the
cost of returning after a break exceeds what a hobby project will pay.

This is not hypothetical here, and the evidence is already in the repository.
`pyproject.toml` carries a comment recording that pydantic 2.12.4 began passing
`prefer_fwd_module=` to `typing._eval_type`, a keyword CPython added between
3.14.0rc2 and 3.14.0 final, raising `TypeError` while evaluating the deferred
annotations in `core/parameters.py` — closed upstream as "not planned" because
the release candidate was never a supported target. One dependency moving one
patch version against one interpreter build broke the scientific core's
parameter loading. That is the shape, and it arrived inside a single release.

The safety-critical standard raises the stakes past ordinary maintenance:
`core/parameters.py` is the validated-parameter boundary, so a silent
behavioural change in the library that parses agent and patient data is a
change to what the simulator computes. Pydantic's own major versions have
changed validation and coercion semantics before.

**Where.** `pyproject.toml` holds every constraint, in four places for the
interpreter alone (`requires-python`, `[tool.ruff] target-version`,
`[tool.mypy] python_version`, and `.python-version`).
`.github/workflows/quality.yml` runs the `floor` job, which is the existing
machinery closest to this and should be read before anything new is built.

**Approach — the decidable part, and the part that is not.** The decision this
wants first is a *policy*, not a script: what this project does when a
dependency moves, written where a session reads it. Candidates, cheapest first,
and only the owner can choose between them:

1. **Nothing scheduled; fix on breakage.** Legitimate for a hobby project, and
   the current implicit answer. It should be stated rather than inherited, so a
   session stops re-deciding it.
2. **A periodic scheduled CI run against the *latest* interpreter and
   unpinned dependencies**, reporting rather than gating. This is the shape
   that suits the horizon: it finds the break while the delta is one version
   wide, and it fails a job nobody is waiting on rather than the gate.
3. **Automated dependency pull requests.** Highest upkeep, and the evidence
   review this project already cites warns that narrow automation works and
   broad automation accumulates noise until it is routed around (`PL-ZBJ0`).

Recommend 2, and do not build it before the policy is chosen — a scheduled job
with no agreed response to a red result is an advisory nobody acts on, which
is exactly what `PL-ZBJ0`'s retirement test now forbids adding.

**Not a version-bump campaign.** The point is knowing when a bump is needed and
having somewhere to record the answer, not raising numbers on a schedule. The
current pins are correct today.

**Found.** 2026-09-02, when the project owner corrected the horizon in
`CLAUDE.md` from one year to multi-year. The audit that preceded it had judged
the codebase structurally healthy on current-state measurements — no import
cycles, median function length 13 lines in `docket` and 7 in `src/` — and those
measurements say nothing about drift, which is the failure mode a longer
horizon adds and the shorter one hides.

**Done when.** `ROADMAP.md` or `CLAUDE.md` states what this project does when a
dependency or the interpreter moves, the answer names who or what notices, and
any mechanism built to support it reports rather than gates.

**Decision needed.** Which of the three responses above does this project
adopt when a dependency or the interpreter moves — fix on breakage (1), a
scheduled report against latest (2), or automated dependency pull requests
(3)?

**Recommended: 2, stated as policy now and built as a separate item later.**
It is the only one that matches a multi-year horizon without adding a gate
that can block work: it finds a break while the delta is one version wide,
and it fails a job nobody is waiting on. Option 1 is defensible and is what
the project does today by default; the value of choosing it deliberately is
that sessions stop re-opening the question. Option 3 is ruled out on this
project's own evidence, which `PL-ZBJ0` (retire a check that has stopped
earning its place) records.

Answering this closes the item by writing the chosen policy into
`ROADMAP.md`; the scheduled CI job, if 2 is chosen, is a second item scoped
after the answer.
