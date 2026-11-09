---
id: PL-V3GD
title: Cut v0.4.32 from the 4 items finished since v0.4.31: the release that completes pr-title-enforcement
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.4.33
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 747
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.32"' pyproject.toml
---

**Problem.** Cut v0.4.32 from the 4 items finished since v0.4.31: the release that completes pr-title-enforcement

The four are `PL-4DCG` (the anesthesia-machine survey), `PL-R5VS` (the `v0.4.31`
cut itself), `PL-XZD0` (reconciling CI's reporting jobs against the
branch-protection required list) and `PL-JVHL` (the chart hover answering for
every run inside the radius). All four are merged on `origin/main`; `v0.4.31` is
cut and tagged, so nothing is outstanding from the previous release.

`0.4.32` is the number because no capability boundary is crossed — it is the
mechanical guess and it is also the right one. Offered to the project owner and
approved on 2026-09-20.

**The cut also clears four `pr:` backfills.** `PL-4DCG` (#742), `PL-JVHL`
(#743), `PL-R5VS` (#739) and `PL-XZD0` (#740) are marked `done` on the base and
record no `pr`. `bin/docket record` bare writes every number the base can
supply; let it ride the release commit rather than composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.32` — never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` (or `make fix`) for the four `pr:` numbers above.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a baseline
   section saying what the release was *for*. Nothing generates that prose.
4. `make check`, which is what proves step 3 landed. Running it earlier fails on
   edits nobody has been asked for yet.
5. Commit, push, open the pull request, merge.
6. The tag is the **project owner's** to push — tag pushes fail from a session
   here, convincingly, reporting `Everything up-to-date` while `git ls-remote
   --tags` shows nothing (`PL-N936`). Paste the three commands filled in, with
   no angle-bracket placeholder, and say the tag is outstanding until they
   confirm it.

**Why it matters.** The release train is this project's cadence, and the
session-start digest asks every session to offer the release before taking new
work — so an uncut release is re-raised in every session until somebody cuts it.
It also gates the next one: `bin/docket release` refuses to cut while the
previous release is untagged.

**Done when.** `pyproject.toml` reads `0.4.32`, `docs/releases/v0.4.32.md`
exists, `ROADMAP.md` carries the row and the baseline section, `make check`
passes, and the tag is pushed.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.32 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Six items, and the first since `v0.4.28` in which anything a learner can reach moves at all: `src/anesthesia_sim/app/` resolves to `3aabb65` at `v0.4.28`, `v0.4.29`, `v0.4.30` and `v0.4.31` alike and to `d00924e` here - two files, +343/-60, and all of it `PL-JVHL`. **Nothing computational moved** - `src/anesthesia_sim/core/` resolves to `89683c3` at both ends and `src/anesthesia_sim/data/` to `d9f9c5b`, so no equation, parameter, numerical method, unit or stored scientific value changed, and `tests/reference/` resolves to `fcb3eca` at both, so every published-reference expected value is byte-identical and still met. A patch because correcting which run a readout answers for crosses no capability boundary, and because every number above it is spent. **`PL-JVHL` is the release.** `nearest_trace_point` kept the single globally nearest drawn point inside a 12 px radius; on the fat trace both runs' points sit inside that radius over the whole of the hoverable axis, so which run answered was settled by arithmetic finer than a reader's hand and nothing in the box said which had won - a threefold difference in stored fat concentration, between a run still carrying agent and one 48 minutes into emergence, turning on a 2 px movement. Both targeting rules the item proposed were then measured and **refuted**, identical to today's behaviour to the digit on every case and for reasons that are facts about this chart rather than about the implementation; what shipped instead is that **every run inside the radius answers, each under its own name**, which takes the share of contended hovers that change their answer from 9.0-9.2% to 0.0% by removing the choice rather than by making it better. **It completes `pr-title-enforcement`, 2 of 2:** `PL-XZD0` adds `tools/required_checks_check.py`, which reconciles the jobs that report a status check on `pull_request` against the branch-protection required list - the brief expected the answer to turn on a credential and the measurement refuted that premise, since `GET /repos/{owner}/{repo}/branches/{branch}` carries `protection.required_status_checks.contexts` and answers unauthenticated on a public repository. `PL-4DCG` surveys the anesthesia machines in current clinical use for the variables that reach a computed number, and falsifies a volume-only machine profile before one is built. `PL-R5VS` is the v0.4.31 cut, `PL-T2YR` recovers two items stranded on a branch whose session opened no pull request, and `PL-TGFY` takes `PL-Z34C` off v0.5.0's frozen gate list onto the sequenced-past disposition.
