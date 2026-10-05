---
id: PL-LNDJ
title: docket's front-matter reader keeps a YAML block-scalar header in a field's value and closes the block on any line opening with ---, so reason: >- reads as '>- Duplicate of ...' and a ---y line ends the front matter; live on two dropped items
priority: P2
effort: S
status: ready
classes: defect
feature: front-matter-round-trip
touches: subprojects/docket/src/docket/model.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a YAML block-scalar header or a stray dashed line in an item's front matter can no longer put text into a value nobody wrote, or drop every field below it, while check reports no errors
verify: grep -q 'def test_a_block_scalar_header_is_never_read_as_part_of_the_value' subprojects/docket/tests/test_model.py && grep -q 'def test_front_matter_closes_only_on_a_line_that_is_exactly_three_dashes' subprojects/docket/tests/test_model.py
---

**Problem.** docket's front-matter reader keeps a YAML block-scalar header in a field's value and closes the block on any line opening with ---, so reason: >- reads as '>- Duplicate of ...' and a ---y line ends the front matter; live on two dropped items

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`_fold` and `parse_front_matter` read `reason: >-` with its folded lines as ">- Duplicate of PL-LT77..." and ">- Measured 2026-09-04...", live at `docs/items/PL-B1DQ-a-v0-4-8-tag-exists-on-a-commit-whose-pyproject.md`:7 and `docs/items/PL-K1DL-splitting-make-check-by-path-docket-changes.md`:10, both dropped. `FRONT_MATTER_RE` (model.py:32) closes on any line that merely opens with `---`: a block holding `---y` before `status: done` reads status `''` and a body starting `y`, and `unread_front_matter_lines` returns nothing. Not a member of `PL-R417`: each value's extent is read whole. The second is latent.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, `parse_item` over the two live files read `PL-B1DQ`'s `reason` as `'>- Duplicate of PL-LT77, which is the same'` and `PL-K1DL`'s as `'>- Measured 2026-09-04 and rejected on three'`, and `bin/docket set PL-K1DL --payoff` on a scratch copy exited 0 having rewritten the field as the single line `reason: >- Measured 2026-09-04 and rejected on three counts, ...`. `parse_front_matter` over the lines `id: PL-K7QX`, `title: t`, `---y`, `status: done` returned only `id` and `title`, with a body starting `y` and `unread_front_matter_lines` returning `()`. In a scratch store the same `---y` line placed above `touches:` gave an item that `show` said "declares no touches", while `bin/docket check` exited 0 with "No errors"; placed above `status:` it was reported only as "no `status`", which names the field the line hid rather than the line.

**Why it matters.** `PL-9HD1` made `_front_matter_pairs` the one reader of where a value ends, and these are two places it still reads that wrongly with nothing to say so: an answer handed over partial as complete, the floor in `.claude/rules/apparatus-standard.md`. The block-scalar half is live, and any `docket set` on either item turns the YAML header into literal text at the front of a one-line value, a file no YAML reader would read as that reason. The closing-line half is latent but silent: a `----` or `---y` line typed into the block ends the front matter early, every field under it falls into the body, and a `touches:` lost that way takes the item out of every lane at `check` exit 0.

**Generator check.** An instance of `PL-9HD1`'s fact, the item front-matter value grammar: where a field's value ends and which spellings it may take, filed after that head closed on 2026-09-21. The one reader that head built keeps a spelling it does not implement and ends the block on a line that is not its end. One of three such instances, with `PL-0779` and `PL-WJM4`, recorded under `PL-HXJY` as a generator whose fix did not hold.

**Done when.** Both halves hold in `subprojects/docket/src/docket/model.py`'s reader. A field written with a `>-` or `|` block-scalar header is either read as YAML reads it, so `PL-B1DQ`'s `reason` starts "Duplicate of PL-LT77" and `PL-K1DL`'s starts "Measured 2026-09-04", or declined by name the way `block_list_keys` declines a block list; in neither case does the header reach the value. And the front matter closes only on a line that is exactly `---`, so a `---y` or `----` line inside the block is reported as a line no field reads, and the fields under it are still read. `test_a_block_scalar_header_is_never_read_as_part_of_the_value` and `test_front_matter_closes_only_on_a_line_that_is_exactly_three_dashes` in `subprojects/docket/tests/test_model.py` pin the two halves.
