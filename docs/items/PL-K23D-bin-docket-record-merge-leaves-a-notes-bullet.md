---
id: PL-K23D
title: bin/docket record --merge leaves a notes bullet that notes_bullets declines unrestated without saying so, so the command's report omits the bullet it could not write; latent
priority: P3
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-18
pr: 1595
payoff: a session running record --merge is told which shipped notes bullets it could not give a route back to their change, instead of reading the repair as complete until a later check says otherwise
verify: grep -q 'def test_record_merge_names_a_notes_bullet_it_declined_to_restate' subprojects/docket/tests/test_cli.py
falsifies: restate_references(
---

**Problem.** bin/docket record --merge leaves a notes bullet that notes_bullets declines unrestated without saying so, so the command's report omits the bullet it could not write; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`cli._restate_notes` goes through `release.restate_references`, which drops `notes_bullets`' decline record, so a bullet continued from the margin is left alone and `record --merge` does not name it; `bin/docket check` does. Its output is true about what it wrote, which is why it is not a member of `PL-R417`, but it is a decline that stops short of the answer that ran. Latent: none of the 79 notes files holds the form.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, a scratch `docs/releases/v9.9.9.md` holding `- PL-K7QX a title wrapped`, then `carried on from the margin` at column zero, then `- PL-B1C2 an ordinary title`, with both items recording a `pr`: `release.notes_bullets` declined the first bullet onto its list ("line 6: this line carries on the entry above it without an indent"), `release.restate_references` returned `('PL-B1C2',)` and nothing about the decline, and `cli._restate_notes` with `dry_run=True`, the repair `record N --merge` runs, printed only "docs/releases/v9.9.9.md: would restate 1 bullet(s) that shipped with no route back to the change: PL-B1C2" and no word of `PL-K7QX`. Re-counted the same day: 79 notes files, and `notes_bullets` declines no bullet in any of them.

**Why it matters.** `_restate_notes` is "the only supported route" to a shipped bullet missing its number, so its report reads as the whole of what the notes owed: a session that runs `record --merge` and reads it takes the notes as repaired while one bullet still has no route back to its change, and learns otherwise only if it also runs `check`. The decline exists and is dropped on the way: `restate_references` hands `notes_bullets` a throwaway list, where `unreferenced_by_version` passes `check` the same record. That is a partial answer rounded off as whole, the failure `.claude/rules/apparatus-standard.md` names as its floor.

**Since 2026-10-17** (`PL-JTP1`, `#1475`): `notes_bullets` returns its
declines beside the bullets instead of putting them on a list the caller
passes, and `restate_references` unpacks them into `_declined` beside a
comment naming this item, so the throwaway list above is that name now and
the route is unchanged: return it from `restate_references`.

**Generator check.** A one-off: one function drops the decline record another returns, so the report rounds a partial answer off as whole, the floor in `.claude/rules/apparatus-standard.md`, which no head's `misread:` states as a fact.

**Done when.** `bin/docket record N --merge SHA`, and its `--dry-run`, names each notes bullet it declined to restate, by file and line with the walker's reason, beside the bullets it restated: the record `notes_bullets` writes reaches `_restate_notes` through `restate_references` instead of a discarded list, and the declined bullet is still left byte for byte as it was. `test_record_merge_names_a_notes_bullet_it_declined_to_restate` in `subprojects/docket/tests/test_cli.py` runs `record --merge` over a notes file holding a bullet carried on from the margin and asserts both.

**Built and held back, 2026-10-18, on `#1594`.** The build in the
`Done when` worked and its tests passed: `restate_references` returned a third
value, the declines from `notes_bullets`, and `_restate_notes` printed each one
as "docs/releases/vX.md line N: <the walker's reason>. Left as it was, so this
bullet may still have no route back to its change", under both `--merge` and
`--dry-run`. `bin/docket verify --self` then refused it. Two assertions in
`tests/test_release.py` compare the whole return value, so adding a third
value had to change them. That is
`test_a_title_wrapped_onto_an_indented_line_keeps_its_reference` and
`test_a_bullet_carried_on_from_the_margin_is_declined_and_left_alone`. A
declaration counts only where the base holds it, so `#1594` adds the
`falsifies:` line above and leaves the code out.

**Next step.** Once `#1594` has merged, rebuild it on a fresh branch from
`main`. Change `restate_references` to return
`(text, repaired, declined)` and update its `-> tuple[...]` annotation and
docstring. Drop the comment above `notes_bullets` there that names this item.
In `cli._restate_notes`, unpack three values and print each decline before the
`if not repaired` test. Update the callers in `tests/test_release.py`
(`restated, repaired, _ = ...`), and the two `==` assertions to the three-value
form. Add `test_record_merge_names_a_notes_bullet_it_declined_to_restate` to
`tests/test_cli.py`. It writes `- PL-B1C2 a title wrapped`, then
`carried on from the margin` at column zero, then `- PL-K7QX A closed item`
under `## v0.2.5` and `### infra` in `_releasable_owed_clone`. It runs the
dry run and then the real run, and asserts that both print
"docs/releases/v0.2.5.md line 6: ". It also asserts that the margin bullet is
left byte for byte and that `PL-K7QX` gains its number.

**Rebuilt 2026-10-18 on `#1595`**, once `#1594` had put the `falsifies:` line
on `main`, exactly as the next step above describes.
