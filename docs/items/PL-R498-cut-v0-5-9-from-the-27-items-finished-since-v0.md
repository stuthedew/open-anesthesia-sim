---
id: PL-R498
title: Cut v0.5.9 from the 27 items finished since v0.5.8: gate dispositions move onto the item, main requires an up-to-date branch against merge skew, an item filed more than 14 days ago is re-confirmed before it is worked, and docs/MODEL.md is corrected on how the chart's percent axis is scaled, with nothing in src/ moving
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-24
payoff: the 27 items finished since v0.5.8 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.9\"" pyproject.toml
---

**Problem.** Cut v0.5.9 from the 27 items finished since v0.5.8: gate dispositions move onto the item, main requires an up-to-date branch against merge skew, an item filed more than 14 days ago is re-confirmed before it is worked, and docs/MODEL.md is corrected on how the chart's percent axis is scaled, with nothing in src/ moving

The project owner asked for the cut by number on 2026-09-24 (project owner,
2026-09-24, ratified, over leaving the 27 to ride a later release), in a
session opened for it. They were answering `PL-TQN2`'s session, whose closing
block asked for a fresh session to cut v0.5.9 once no other session was
cutting it. `list_sessions` showed none, and `origin/main` carried no
`docs/releases/v0.5.9.md`.

`bin/docket release --dry-run` listed 27 at filing, completing
`brief-state-agreement`, `debt-aging`, `gate-disposition-store` and
`merge-skew`. Anything that merges before the cut ships in it too, so re-run
the dry run rather than trusting this count. Then run
`make release VERSION=0.5.9`, make the `ROADMAP.md` edits it names (the
version-table row, the current-baseline mark and the baseline section) and run
`make check`. The tag is the owner's to push, per
`.claude/skills/docket/modes/release.md`.
