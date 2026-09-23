---
id: PL-8543
title: Cut v0.5.8 from the six items finished since v0.5.7: a verify: command outside the admitted shapes is refused when it is written, and a closed generator head or a misspelt front-matter key stops passing silently, with nothing in the simulator moving
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-23
payoff: the six items finished since v0.5.7 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.8\"" pyproject.toml
---

**Problem.** Cut v0.5.8 from the six items finished since v0.5.7: a verify: command outside the admitted shapes is refused when it is written, and a closed generator head or a misspelt front-matter key stops passing silently, with nothing in the simulator moving

The project owner asked for the cut by number on 2026-09-23 (project owner,
2026-09-23, ratified, over leaving the six to ride a later release), answering
the session that offered it. That session filed this item and stopped before
starting it, for length: its spend was 175,487 against `CLAUDE.md`'s 150,000
budget.

`bin/docket release --dry-run` listed six at filing: `PL-1P5V`, `PL-BBT8`,
`PL-CT07`, `PL-DSPM`, `PL-KNWP` and `PL-QP9Z`. Anything that has merged
since, such as `PL-BX1C` (pull request #952, open at filing), ships in this cut
too, so re-run the dry run rather than trusting this list. Then run
`make release VERSION=0.5.8`, make the `ROADMAP.md` edits it names (the
version-table row, the current-baseline mark and the baseline section) and run
`make check`. The tag is the owner's to push, per
`.claude/skills/docket/modes/release.md`.
