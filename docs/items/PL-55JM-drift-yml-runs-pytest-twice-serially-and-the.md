---
id: PL-55JM
title: drift.yml runs pytest twice serially, and the comment explaining why it stays bare is about --cov rather than about -n auto
status: untriaged
added: 2026-09-04
---

**Problem.** drift.yml runs pytest twice serially, and the comment explaining why it stays bare is about --cov rather than about -n auto

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `.github/workflows/drift.yml` runs `uv run pytest` twice, both
bare. `quality.yml`'s pytest step carries the comment that explains why:
"`drift.yml` deliberately keeps its bare `uv run pytest`: a coverage failure
there would report as a dependency break, which is the opposite of what that
workflow is for. `PL-22Z3`."

**The gap.** That reason is entirely about `--cov`, and it is a good one. It
says nothing about `-n auto`, which cannot cause a coverage failure because
there is no coverage gate on those lines. So the parallelism question has
never actually been decided for `drift.yml` - it was only decided for the
coverage flag, and a reader meeting the comment would reasonably conclude both
were settled together.

**Found while working `PL-FX3N`** (put `-n auto` on `make test`), which had to
enumerate every place the flag lives to say what it was and was not joining.
Left rather than fixed: `PL-FX3N`'s `touches` was `Makefile, README.md`, and
widening a branch past its brief is what `CLAUDE.md` forbids.

**Why it is small, and might be worth dropping.** `drift.yml` runs on a
schedule and never on a pull request - it reports and does not gate - so its
wall clock costs nobody's iteration. That is the argument for leaving it. The
argument against is that four places now carry or omit this flag, and one of
them omits it for a reason that does not cover the omission.

**A wrinkle worth deciding rather than assuming.** `drift.yml` runs `uv sync
--upgrade`, so `-n auto` there would also exercise whatever `pytest-xdist`
resolves to - which is arguably exactly what a drift workflow is for, and
arguably one more moving part in a job whose red results are supposed to be
news. Decide which.

**Where.** `.github/workflows/drift.yml`, both `- run: uv run pytest` lines;
`quality.yml`'s comment if the answer changes what it should say.

**Done when.** Either both lines carry `-n auto`, or `quality.yml`'s comment
(or `drift.yml`'s own) says the parallelism flag was considered for them
separately from the coverage flag and deliberately left off.
