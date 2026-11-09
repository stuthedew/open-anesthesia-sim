---
id: PL-R498
title: Cut v0.5.9 from the 27 items finished since v0.5.8: gate dispositions move onto the item, main requires an up-to-date branch against merge skew, an item filed more than 14 days ago is re-confirmed before it is worked, and docs/MODEL.md is corrected on how the chart's percent axis is scaled, with nothing in src/ moving
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.10
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-24
closed: 2026-09-24
pr: 980
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

**Cut 2026-09-24.** 27 items, as the dry run said at filing, and no pull
request was open to add one. Cut with `make release VERSION=0.5.9`, which
recorded 27 `pr:` numbers before rendering the notes, stamped the 27
`milestone: v0.5.9`, wrote `docs/releases/v0.5.9.md`, bumped `pyproject.toml`
and relocked `uv.lock`. None is a milestone and every number above this one is
spent - `bin/docket wave` reserves 0.6.0 through 0.9.0 - so this is a patch on
§ "Versioning decision"'s test. Four are Gate 2 entries (`PL-LF2C`, `PL-QYBW`,
`PL-VJPJ`, `PL-WVJ0`), which stands at 46 of 185 cleared at this cut, and eight
are v0.6.0 deferrals. Four features complete: `brief-state-agreement`,
`debt-aging`, `gate-disposition-store` and `merge-skew`. No v0.5.9 item merged
inside v0.5.8's tag, which is on its own cut's merge, so v0.5.8's notes take no
pointer.

`src/` is byte-identical to v0.5.8 (`37b0a4c`). `docs/MODEL.md` moves by
`PL-QYBW`'s correction: from v0.4.32 it said the chart's percent axis is scaled
by the alveolar peak, and the code has fixed it at 3 MAC since v0.4.0. That
item's title is left as filed because `ROADMAP.md`'s frozen lists quote it, so
the notes carry a nested line under its bullet saying the premise is false;
the line sits under the bullet rather than after its reference because
`release.REFERENCED_RE` anchors the reference at the end of the bullet's line.

**`#978` is not this cut.** It opened at the branch's first push, carrying only
the capture and the start claim, and was merged six minutes later while the cut
was uncommitted, so `main` holds `8428844c`, "PL-R498: cut v0.5.9 from the 27
items finished since v0.5.8 (#978)", with this file in it and nothing else.
The branch was restarted from `main` under the same name and re-claimed, and
the cut arrives in its own pull request. Filed as `PL-H14W`. Tag the cut's own
merge commit, never `8428844c`.

Filed while cutting: `PL-PRSF`, an angle-bracket placeholder in a title
vanishing from the rendered notes.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.9 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Twenty-seven items, all apparatus and documentation, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed, and every number above it is spent, v0.6.0 through v0.9.0 being given to milestone sections. **Nothing in `src/` moved, and this cut says so by tree identity alone**: `src/` resolves to `37b0a4c` at v0.5.8 and here, so `core/` (`d9e3ca9`), `data/` (`ab3499f`) and `app/` (`f3c6e26`) are byte-identical, and `tests/reference/` (`a184830`), `README.md` and `.github/` (`275baf5`) with them. **`docs/MODEL.md` moves by a correction** (`148686b` to `fd139ea`): from v0.4.32 it said the chart's percent axis is scaled by the alveolar peak, where the code has fixed it at 3 MAC for every agent (`CHART_AXIS_TOP_MAC`) since v0.4.0. `PL-QYBW` keeps that one linear axis (project owner, 2026-09-23, ratified, over a reader-selected logarithmic scale) and corrects the three statements, and `PL-H5DV` corrects planned-milestone item 27's claim about how much agent fat holds. **Four features complete.** `gate-disposition-store`: `PL-WD5Z` moves a gate's dispositions from `ROADMAP.md` prose onto a `deferred-from:` field on the item, closing `PL-58JD`, `PL-59QW` (which completes `brief-state-agreement`), `PL-FD5Q` and `PL-VFJ3` with it. `merge-skew`: `PL-70VB` repairs the red `main` that `#967` and `#970` produced by merging cleanly, the third instance within 30 days, so the trigger `PL-Z0SM` recorded fired, the project owner turned on strict up-to-date checks for `main`, and `PL-6MW8` revises `CLAUDE.md`'s base-merge rule for them. `debt-aging`: `PL-TQN2` has `bin/docket show` print an open item's age and what changed under its `touches`, and ask past 14 days for re-confirmation. Six more finish the owner's generator audit and say what the new-mechanism pause holds, `PL-GHHW` and `PL-PXZ3` share one landing test, `vcs.change_landed`, and the rest fix the queue tool. **Four are Gate 2 entries**, which stands at 46 of 185 cleared at this cut, eight more are v0.6.0 deferrals, and `PL-8543`, the v0.5.8 cut, closes here because a cut cannot stamp itself.
