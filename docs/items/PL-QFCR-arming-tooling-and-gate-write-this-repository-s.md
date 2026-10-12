---
id: PL-QFCR
title: arming.TOOLING and GATE write this repository's layout into the docket package, which reads every other path it depends on from docket.toml
priority: P3
effort: S
status: ready
classes: refactor
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/config.py, docket.toml
blocked-by: PL-5DZ8, PL-8QMD, PL-ZGYX
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
payoff: docket.toml becomes the one place the package reads this repository's paths from, so moving the tooling or reusing docket in another repository changes a setting instead of holding every tooling change there for a read
verify: ! grep -qF '"subprojects/docket/"' subprojects/docket/src/docket/arming.py
---

**Problem.** arming.TOOLING and GATE write this repository's layout into the docket package, which reads every other path it depends on from docket.toml

**Found** building `PL-K6B2`, whose `touches` reach neither `config.py` nor `docket.toml`, so the tooling's path went in as a module constant beside `claims.CUTOVER_MARKER`, the one precedent. `config.py` says of `notes_file` that the package "keeps no notion of any particular repository's layout"; `CUTOVER_MARKER` goes when `PL-CH3Z` lands, and these two stay. A `docket.toml` field is a new field, which the generator pause holds.

**Reproduced 2026-09-26 against 78b1a02b.** `arming.py:98` is `TOOLING = "subprojects/docket/"` and `:104` is `GATE = TOOLING + "src/docket/arming.py"`, while `config.py`'s `notes_file` comment says the package "keeps no notion of any particular repository's layout". No `docket.toml` field means either path: `gate_paths` names the checks a delegated diff may not edit, and holds neither.

**Why it matters.** Once `PL-CH3Z` deletes `CUTOVER_MARKER`, these are the only paths of this repository the package states outside `docket.toml`, against a principle `config.py` writes down. The stakes are the principle rather than a wrong answer: both constants fail closed. Moved, or used in another repository, `TOOLING` matches nothing and every tooling change is held for a read, and `test_cli` pins `GATE` to the module's real path.

**Done when.** `arming.py` names no path of this repository: the tooling and the gate are read from `docket.toml` through `config.py`, and a project declaring neither gets today's fail-closed answer. Tests hold both.

**Blocked, triage 2026-09-26.**
- **Held by the generator pause.** The fix is a new `docket.toml` field, confirmed: no existing field means the tooling or the gate, and reusing `gate_paths` would re-specify it. The constants give no wrong answer, so this is not a defect in what exists. A request from the project owner lifts the pause for this item (`PL-6Q9L`).
- `blocked-by` named the six open items carrying `generator: live` on 2026-09-26. Every one has since closed, and on 2026-10-04 it names `PL-R417`, the one head `bin/docket generators` then marked still generating. The pause's own test is `bin/docket generators` marking no head "still generating"; a head recorded spent while open, or a new live one, moves that without touching this list, so check the command before unblocking.

**Generator check.** One-off. The fact misread is where this repository's layout is recorded: `docket.toml`, not a module constant. No head's `misread:` states it, and its one other instance, `claims.CUTOVER_MARKER`, is deleted by `PL-CH3Z` rather than filed. The cause was `PL-K6B2`'s `touches`, which reached neither `config.py` nor `docket.toml`.

[superseded 2026-10-12: `PL-R417` no longer holds it; the pause it ended restarted with #1419's three live heads, below] **The pause ends with `PL-R417`, closed 2026-10-11 in `#1392`.** `PL-R417` was the last head `bin/docket generators` marked still generating, and with it closed the command marks none, so the pause this waited on ends when `#1392` merges. Nothing else holds it: `arming.TOOLING` and `GATE` are still module constants. It stays `blocked` only because `ready` needs a `verify:` command and a `payoff:`, which `bin/docket set` refuses `ready` without and triage writes beside the work; `bin/docket check` names it ready to promote meanwhile.

[superseded 2026-10-12] **Re-read 2026-10-12 under `PL-2349`**, whose check now refuses a `blocked` item whose every blocker has closed. `PL-R417`'s closure ended the generator pause on 2026-10-11, and `PL-74T0` restarted it the next day: #1419 (`febb37b4`) recorded `PL-5DZ8`, `PL-8QMD` and `PL-ZGYX` as live heads, and `bin/docket generators` marks all three still generating. Nothing else this brief names holds it, so it stays held by the pause, now blocked on those three - though the pause's own test is still `bin/docket generators` marking no head "still generating", not this list. The `verify:` and `payoff:` are written now, so the pull request that ends the pause can promote it in one write. The fault stands: `grep -n '^TOOLING' subprojects/docket/src/docket/arming.py` prints `TOOLING = "subprojects/docket/"`. `verify:` passes once `arming.py` no longer spells that path, and was seen failing (exit 1) on 2026-10-12; the tests Done-when asks for are the reviewer's to read.

**Promoted to `ready` 2026-10-12.** `PL-8QMD` closed as the last head
`bin/docket generators` marked still generating, so the generator pause that
held this item has ended (`CLAUDE.md` § "What this project is"), and the
`verify:` and `payoff:` written above stand.
