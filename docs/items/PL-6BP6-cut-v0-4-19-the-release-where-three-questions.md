---
id: PL-6BP6
title: "Cut v0.4.19: the release where three questions were answered and core/ did not change a line"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 537
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.19"' pyproject.toml && test -f docs/releases/v0.4.19.md
---

**Problem.** Ten items finished since v0.4.18 and none had shipped, so
`bin/docket next` and the session-start digest asked every session to offer a
release before taking new work.

**Why it matters.** Filed before the cut rather than after it, per `CLAUDE.md`'s
rule that repository work taking a commit of its own is filed first: every
in-flight guard this project has matches a `PL-` id, and a release cut has none
until somebody starts one. `PL-66FP` is what the unfiled version cost - two
sessions cut v0.3.7 within the hour and the second was discarded at the merge.
The live session list was checked before starting: one session
(`claude/lucid-mendel-6kavwt`) had *offered* v0.4.19 and was idle awaiting the
answer, and none was cutting it.

**Done when.** `pyproject.toml` is at 0.4.19, `docs/releases/v0.4.19.md` exists,
`ROADMAP.md` carries the version-table row, the moved `current baseline` mark
and the baseline section, and `make check` passes.

**What the release turned out to be about.** Three of the ten entries are `P1`
and all three settle a question rather than add behavior: what the readouts show
while two runs are displayed (`PL-1XPX`), what does *not* cause desflurane's
five-minute washout residual (`PL-RFLN`), and how a session reaches a source
PubMed cannot give it (`PL-XJ5P`). `ROADMAP.md`'s baseline section carries the
account.

**"core/ did not change a line" is a tree-object identity, not a reading of the
diff.** Measured across `v0.4.18..origin/main`: `src/anesthesia_sim/core/`
resolves to `7a49512` at both ends and `src/anesthesia_sim/data/` to `d5a26cf`,
so the model implementation and every stored parameter are byte-identical and no
equation, constant, numerical method or unit moved. `tests/reference/` gained
251 lines and lost none, so every pinned published and canonical value that
stood at `v0.4.18` still stands. What did change is `app/` (three interface
entries), `docs/MODEL.md`, and `.github/workflows/quality.yml`, which gained
`PL-FZ6T`'s vocabulary check.
