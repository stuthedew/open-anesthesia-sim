---
id: PL-6BP6
title: "Cut v0.4.19: the release where three questions were answered and core/ did not change a line"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.20
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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.19 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> The second half of that is a tree-object identity rather than a reading of the diff: `src/anesthesia_sim/core/` resolves to `7a49512` at both `v0.4.18` and this release, and `src/anesthesia_sim/data/` to `d5a26cf`, so every equation, constant, numerical method, unit and stored parameter is byte-identical and not one number the model produces was recomputed; `tests/reference/` gained 251 lines and lost none, so every pinned published and canonical value still stands. All three `P1` entries settle a question instead of adding behavior. `PL-1XPX` decides what the readouts show while two branches are displayed — both runs, paired per compartment, each naming its run in text — and refuses a difference readout on a domain ground rather than a layout one, because the arithmetic difference of two alveolar fractions is not a quantity with a conventional clinical reading; the readout cap that was recommended and approved is recorded as refused by `docs/MODEL.md` § "Minimum displayed outputs", which already forbids a required value leaving the display with the curve that draws it. `PL-RFLN` removes a candidate for desflurane's five-minute washout residual: the published apparatus's dead space is an alveolar-ventilation decrement rather than an inspired fraction, and at the published magnitude it closes only a quarter to two fifths of the 2.33 published SD while pushing an isoflurane cohort that was inside its spread out of it — the common-mode failure every earlier candidate died of, now pinned by two mutation-checked reference tests, with the parameter file again unchanged. `PL-XJ5P` closes the hole under `.claude/rules/citing-sources.md`'s promise that "there is a route": a private reference corpus is adopted as the terminal route, verified end to end from a session before the rule was written, and what a *miss* means is written down — record the gap and put the reading to the owner, rather than narrowing the claim or taking a search summary for a reading. Three interface entries apply the same standard from the reader's side: the readout row names the substance its numbers belong to (`PL-TCD1`), the new-case dialog's carry-over sentence names only settings the reader can actually set (`PL-0Q1T`), and the wash-in panel's 786 characters of standing prose are gone (`PL-F9TQ`). Two more turn a convention into something that runs: `PL-FZ6T` holds `core/` to `docs/MODEL.md` in code — every Symbols Code cell must resolve to a real attribute, the retired accessor names may not reappear, and a partition-coefficient identifier must name both phases outward from the gas phase — and `PL-RC0M` replays a blocked item's `verify:` command so it cannot rot unnoticed and redden whichever pull request unblocks it. `PL-B667` states the upper bound `core/` has always enforced in five places. Ten items.
