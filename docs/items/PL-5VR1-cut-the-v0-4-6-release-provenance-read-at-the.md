---
id: PL-5VR1
title: "Cut the v0.4.6 release: provenance read at the source"
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases
added: 2026-09-06
closed: 2026-09-06
pr: 411
not-delegable: proving a release-time change means cutting a release; there is no command that can be run beforehand
---

**Problem.** Eleven items finished since v0.4.5 with no release behind them,
and `bin/docket wave` read the beat as clearing Gate 1 while the digest offered
0.4.6 in every session.

**Why it matters.** `bin/docket release` refuses to cut while the previous
release is untagged, and `milestone:` stamping is what lets a later reader ask
what shipped when. Unshipped finished work also makes the digest's release
offer repeat in every session until somebody acts on it.

**Where.** `pyproject.toml` and `uv.lock` (the version), `docs/releases/v0.4.6.md`
(generated), and `ROADMAP.md` - the version-table row, the `current baseline`
mark moved off v0.4.5, the baseline section rewritten, and a release-narrative
entry added.

**Approach.** `make release VERSION=0.4.6`, never `bin/docket release` alone -
the tool writes the version into `pyproject.toml` and stops, and `uv.lock`
records the project's own version too, so the next `make check` fails on `uv
sync --locked` with the tree half-updated. Then the prose the tool does not
generate, then `make check`.

**Done, 2026-09-06.** Cut on the project owner's instruction after the
recommendation to hold was overtaken: the five parallel sessions that argued
for waiting had all landed. The version was named rather than incremented, per
`ROADMAP.md`'s "Versioning decision"; 0.4.6 was also the mechanical guess,
because this release crosses no capability boundary - it is gate-clearing and
provenance work inside the `v0.4.x` track.

Eleven items stamped. `src/anesthesia_sim/core/` is byte-identical to v0.4.5
and every stored value in `src/anesthesia_sim/data/` is unchanged; the only
`src/` changes are three `app/` files from `PL-GYH2`. Gate 1 stands at 17 of
121 cleared.

**The tag is outstanding and is the project owner's to run** - a session cannot
push a tag ref from this environment (`PL-N936`: `git push --dry-run` reports
`[new tag]` and the real push dies on `send-pack: unexpected disconnect` while
`git ls-remote --tags` shows nothing). The commands are in the closing block of
the reply that cut it, filled in against the merge commit.
