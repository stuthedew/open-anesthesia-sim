---
id: PL-QSWS
title: No item or roadmap entry covers dependency and toolchain drift, which a multi-year horizon makes a certainty rather than a risk
priority: P2
effort: S
status: done
closed: 2026-09-02
pr: 239
classes: infra, docs
feature: dev-tooling
touches: pyproject.toml, .github/workflows/drift.yml, ROADMAP.md
verify: test -f .github/workflows/drift.yml && grep -q 'uv sync --upgrade' .github/workflows/drift.yml && grep -q 'Keeping the toolchain current' ROADMAP.md
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

**Decided 2026-09-02 (project owner).** The recommended option: a periodic
scheduled run against the latest interpreter with dependencies unpinned,
reporting rather than gating. The other two were declined - "nothing scheduled,
fix on breakage" leaves the delta to grow to whatever width a gap produces, and
automated dependency pull requests are the broad automation the evidence this
project cites says accumulates noise until it is routed around (`PL-ZBJ0`).

**What landed.** `ROADMAP.md` gains "Keeping the toolchain current", stating the
policy, what notices, what deliberately does not happen, why it reports rather
than gates, and the condition for retiring it.
`.github/workflows/drift.yml` implements it as two monthly jobs plus
`workflow_dispatch`:

- `dependencies` — `uv sync --upgrade`, so the newest release every bound in
  `pyproject.toml` already allows. No constraint is edited, so a failure means
  a dependency broke us inside a range this project has already accepted.
- `interpreter` — newest stable CPython, with `requires-python`'s upper bound
  relaxed *in the runner only*. uv refuses an interpreter outside
  `requires-python`, which is right everywhere else and is the thing this job
  has to see past. The relaxation is a scripted edit that fails loudly if
  `pyproject.toml`'s shape changes, rather than silently re-testing the pinned
  version.

**The bound-crossing half is reported, not attempted.** `uv pip list
--outdated` runs with `continue-on-error`, so a Flet 1.0 or a pydantic 3 shows
up as available without turning the run red or being auto-adopted. Crossing a
major bound is a deliberate migration. Without this step nothing would ever
mention that the migration had become possible, which was the largest gap in
the original finding.

**Ordering note, recorded rather than hidden.** The `verify:` command here was
written *after* the work, which is the opposite of what the `docket` skill
requires and what `PL-L9JS` exists to enforce. It was checked against
`origin/main` in a scratch checkout before being recorded - exit 1 without the
work, 0 with it - so it discriminates, but that is a weaker guarantee than
having watched it fail first.

**Not verified end to end.** `drift.yml` has valid YAML and its steps use the
same actions and pinned versions as `quality.yml`, but a scheduled workflow
cannot be exercised from a pull request. `workflow_dispatch` is on it so the
first real run can be triggered by hand; until that has happened once, treat
the job as untested rather than working.

