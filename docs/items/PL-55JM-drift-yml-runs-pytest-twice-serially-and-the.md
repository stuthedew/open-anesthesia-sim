---
id: PL-55JM
title: drift.yml runs pytest twice serially, and the comment explaining why it stays bare is about --cov rather than about -n auto
status: needs-decision
priority: P2
effort: S
classes: infra, test
feature: dev-tooling
touches: .github/workflows/drift.yml, .github/workflows/quality.yml
verify: python3 tools/doc_check.py check && ! grep -qE '^ *- run: uv run pytest$' .github/workflows/drift.yml && ! grep -q 'deliberately keeps its bare' .github/workflows/quality.yml
added: 2026-09-04
---

**Problem.** `.github/workflows/drift.yml` runs `uv run pytest` twice - once at
the end of the `dependencies` job and once at the end of the `interpreter` job -
and both are bare. `quality.yml`'s pytest step carries the comment that appears
to explain why: "`drift.yml` deliberately keeps its bare `uv run pytest`: a
coverage failure there would report as a dependency break, which is the opposite
of what that workflow is for. `PL-22Z3`."

**Why it matters.** That reason is entirely about `--cov`, and it is a good one:
`--cov-fail-under=100` measures this project against its own policy, so a red
drift run caused by it would say nothing about dependencies. It says nothing
about `-n auto`, which is a different kind of flag. `pytest-xdist>=3.8.0` is a
declared `dev` dependency (`PL-WCZV`), and both `drift.yml` jobs run `uv sync
--upgrade --dev` - so the workflow already resolves whatever xdist is newest and
then never executes it. A declared dependency the drift job upgrades and never
runs is precisely the hole its own header says it exists to close: "every
constraint in `pyproject.toml` goes untested against the world moving past it."

The comment is the second half of the cost. A reader meeting it would reasonably
conclude both flags were settled together, so the parallelism question stays
answered-by-appearance rather than answered.

**Decision needed.** Do `drift.yml`'s two pytest runs carry `-n auto`, or stay
bare with `quality.yml`'s comment corrected to say the parallelism flag was
considered separately from the coverage flag and deliberately left off? Either
answer closes the item; what cannot stand is the comment continuing to imply
both were settled together.

**Recommended, for the session that takes this: add `-n auto` to both lines.**
Left at `needs-decision` rather than answered - triage sets fields, it does not
resolve the question an item poses (`PL-ZSV6`). The reasoning is recorded here
so the decision costs one read rather than a re-investigation. The `--cov`
reasoning does not transfer, and the distinction is clean: `--cov` measures the
project against its own policy, so a red there is not news about dependencies;
`-n auto` *runs* a dependency, so a red there is exactly the news this job
exists to deliver. Two objections were weighed and both fail:

- *Parallelism could make a red run ambiguous.* Any parallel-unsafe test in this
  suite is already red on every pull request, because `quality.yml` and `make
  check` both run the whole suite at `-n auto`. The gate has retired that risk.
- *One more moving part in a job whose red results are supposed to be news.* An
  xdist regression **is** a dependency break, which is the category this job is
  built to find - unlike a coverage-threshold failure, which is not.

Aligning the topology is the secondary benefit. `make test`, `make check` and
`quality.yml` all run parallel now, so a serial `drift.yml` differs from the
gate on two axes - dependency versions *and* execution topology - when the point
of a drift job is to vary one.

Speed is not the argument and should not be offered as one. The job is monthly,
never runs on a pull request, and gates nothing, so its wall clock costs
nobody's iteration; the saving is CI minutes.

**Where.** `.github/workflows/drift.yml`, both `- run: uv run pytest` lines
(currently 71 and 172). `.github/workflows/quality.yml`, the comment above its
own pytest line (currently 61-63), which has to stop saying `drift.yml`
"deliberately keeps its bare `uv run pytest`".

**Done when,** on the recommended answer - the `verify:` command encodes it, so
a session taking the other path rewrites both. Both `drift.yml` pytest lines
carry `-n auto`, and
`quality.yml`'s comment names the two flags separately: `--cov` stays off
`drift.yml` for the reason it already gives, `-n auto` goes on because xdist is
a declared dependency that job should be exercising.

**Found while working `PL-FX3N`** (put `-n auto` on `make test`), which had to
enumerate every place the flag lives to say what it was and was not joining.
Left rather than fixed there: `PL-FX3N`'s `touches` was `Makefile, README.md`,
and widening a branch past its brief is what `CLAUDE.md` forbids.
