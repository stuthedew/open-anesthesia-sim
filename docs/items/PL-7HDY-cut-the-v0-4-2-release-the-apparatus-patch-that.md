---
id: PL-7HDY
title: 'Cut the v0.4.2 release: the apparatus patch that completes docket-store'
priority: P2
effort: S
status: done
classes: planning, docs
feature: planning-cadence
milestone: v0.4.3
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases/, docs/items/
added: 2026-09-05
closed: 2026-09-05
pr: 365
not-delegable: proving a release cut means cutting the release. No command
---

**Problem.** Six items have closed since v0.4.1 (eight by the time the cut
merged; see below) and nothing has stamped them
into a release. Filed before the work per `CLAUDE.md`'s housekeeping rule: a
release cut carries no `PL-` id until somebody files one, so every in-flight
guard reads it as nobody's work — which is how two sessions cut v0.3.7
independently (`PL-66FP`). `PL-J7Y7` is the precedent from the v0.4.1 cut and
`PL-647D` from v0.4.0.

**Why it matters.** The stamp is what makes `milestone:` answerable per item,
and the notes are the only place the release says what it was *for*. Left
uncut, the next release claims work that belongs to this one, and the version
table stops describing the history.

**Where.** `pyproject.toml` and `uv.lock` (the version, written by `make
release`); `ROADMAP.md`'s version table, `current baseline` mark and a new
baseline section; `docs/releases/v0.4.2.md`; the six items' `milestone:`
fields.

**Approach.** `make release VERSION=0.4.2`, never `bin/docket release` alone —
the tool writes the version into `pyproject.toml` and stops, but `uv.lock`
records the project's own version too, so the next `make check` fails on `uv
sync --locked` for a reason unrelated to the release. That happened on both
releases the command existed for before `make release` wrapped the two.

The version is named rather than incremented: `docket.toml` sets
`version_policy = "manual"` because the number marks the capability boundary a
release crosses, which no class label carries. **0.4.2 is the right name here**
— six apparatus items, no new simulator capability, and `ROADMAP.md` gives
0.5.0 to "the case you can branch here", which is unstarted.

What the tool cannot generate is the prose: `ROADMAP.md` needs a version-table
row, the `current baseline` mark moved onto it, and a baseline section saying
what the release was for. `bin/docket release` names each statement it makes
stale, with line numbers; `make check` is what proves those edits landed, and
running it earlier fails on edits nobody has been asked for yet.

**Done when.** `pyproject.toml` and `uv.lock` read 0.4.2, the items carry
`milestone: v0.4.2`, `docs/releases/v0.4.2.md` exists, `ROADMAP.md` carries the
row, the moved baseline mark and the prose, `make check` is green, and the
project owner has the two `git tag` commands filled in — the tool stops before
tagging on purpose, so a release is reviewed before it is marked.

**Re-cut once, deliberately.** #361 merged into `main` while this pull request
was in flight, closing `PL-D551` and `PL-W9DW`. GitHub's auto-merge updated the
branch, which put those commits inside the span the v0.4.2 tag will cover while
the tool had already assigned their items to 0.4.3 — `PL-028F` exactly. Rather
than hand-edit `milestone:` (a provenance field nothing guards, `PL-JSRH`), the
cut was reset and re-run against the merged base so the tool did the stamping:
nine items by the second re-cut, and the notes describe what the tag will
actually contain.
`PL-7HDY` itself was reopened before the re-cut so it lands in the next release,
which is where `PL-J7Y7` went and is the convention.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.2 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Its subject is the instruction budget every session pays and the guards that keep work visible. Resident text can now *shrink*: 563 characters whose carriers already existed were routed out of `CLAUDE.md`, and resident rules gained the retirement test that checks have had since `PL-ZBJ0` — until now a rule could only be added, because nothing said when one had stopped earning its place, and the total falls 44 545 to 44 166 characters. Beside it `tools/rules_paths_check.py` gained its second rule: a `paths:` entry that is anchored and points at nothing is refused, the same silent failure as the `./` spelling v0.4.0 closed, arriving in the form that reads as correct at every glance — a transposed directory name — and the message names the nearest existing ancestor rather than only the offence. Two provenance guards close: seven items stranded on abandoned branches are recovered, two of them created by the score-architecture drops, and the pull-request title check stopped racing the retitle it asks for, which had been showing a red run that meant nothing on a green pull request. Landing during this release's own pull request, the gate learned what it costs to run: the `floor` job billed a whole minute for eight seconds of work and held one of twenty account-wide concurrent job slots, so its steps moved inside `checks` *ahead of* the uv install — which strengthens the no-virtualenv claim rather than weakening it, because at that point no virtualenv exists to fall back on — and a spending limit and usage alert now exist, where the first sign of Actions overage had been the invoice. `README.md`'s status section is corrected too: it understated the operator split's disagreement with the exact solution as 1.2e-2 percentage points where `docs/MODEL.md` gives 2.3e-2 over the same domain, which is the kind of divergence between a summary and its specification that the `v0.4.x` track exists to remove. Nine items, one of which is the v0.4.1 cut itself.
