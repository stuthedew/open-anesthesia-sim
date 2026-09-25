---
id: PL-PLV0
title: verify's falsifies: advisory says the line had to reach the base before the branch's first commit and that triage is the only pass that can write it, though PL-TKFD's route amends the base mid-work from an item-only branch
priority: P3
effort: S
status: ready
classes: defect
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, .claude/skills/docket/modes/triage.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: a session whose branch declares a falsifies: the base lacks is told the route that still works - declare it on the base and re-audit - instead of that nothing could have been done
verify: ! grep -qF 'so triage is the only pass' subprojects/docket/src/docket/verify.py && ! grep -qF 'why triage is the only pass that can write it' .claude/skills/docket/modes/triage.md
falsifies: triage is the only pass that can write it
---

**Problem.** verify's falsifies: advisory says the line had to reach the base before the branch's first commit and that triage is the only pass that can write it, though PL-TKFD's route amends the base mid-work from an item-only branch

**Captured 2026-09-25 in #1017**, the pull request that closed `PL-B8HZ` and
`PL-TKFD`. It was left unfixed there because changing the string changes a
pinned assertion.

**Reproduced 2026-09-25 against 46954a81.** In `verify.py`'s `_check_item`,
the `elif item.falsifies and not declared` branch still prints "the line had
to reach {base} before this branch's first commit, so triage is the only pass
that can write it". `test_a_branch_declaration_names_the_window_it_missed` in
`subprojects/docket/tests/test_verify.py` pins both halves of that sentence.
`read_commission` reads the item with `git show {base}:{items_dir}/<file>`,
which is the base's tip at the moment `verify` runs, not the fork point. So a
declaration merged onto the base mid-work does fold. That is the route
`.claude/skills/docket/modes/close-out.md` prescribes in its paragraph "A
waiver is amended where the commission lives", under `PL-TKFD` (project owner,
2026-09-25, ratified), and the sentence is false. The heading "`falsifies:`,
and why triage is the only pass that can write it" in
`.claude/skills/docket/modes/triage.md` makes the same claim. Its own body
already qualifies it ("the last pass that can write it for nothing").

**Why it matters.** The advisory fires in exactly the case the `PL-TKFD` route
exists for: a branch declaring a `falsifies:` its base does not hold. At that
moment it tells the session that nothing could have been done, which steers
it away from the route the close-out mode prescribes. The case is rare, about
2 folds in 502 close-outs (`PL-YZJD`), and the close-out mode states the
route beside it. That is why this is P3.

**Done when.** The advisory names the route that is still open: declare the
waiver on the base from an item-only branch, let it merge, bring the base in
and re-audit. It no longer says the window shut at the branch's first commit.
The test pins the new wording, and the `triage.md` heading no longer says
triage is the only pass. Renaming that heading stops closed `PL-YZJD`'s
recorded `verify:` from resolving. A closed item's command is a record and is
not repaired, so that is expected.

**`falsifies:`**, written from the string the title quotes. It names the
assertion `assert "triage is the only pass that can write it" in
note.detail`, which this work removes by definition. The same test's other
assertion, `"before this branch's first commit"`, is removed only if the new
wording drops that phrase. If it does, that assertion needs its own
declaration through the `PL-TKFD` route.

**Generator check.** An instance of `PL-B8HZ`'s fact: which copy of an item,
the base's or the branch's, is authoritative for each contract field. Here the
base's copy is read at its tip when `verify` runs, not as of the branch's
first commit. It was filed in the commit that closed that head, as a leftover
the head knowingly deferred. That makes it bookkeeping of the close, not a new
mechanism.
