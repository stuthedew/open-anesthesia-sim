---
id: PL-VJFQ
title: Nothing enforces that KNOWN_SHORTFALLS only shrinks, so the contrast ledger could become the suppression list ui-color.md forbids in prose
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: dev-tooling
touches: tools/contrast_check.py, .claude/rules/ui-color.md, tests/unit/test_contrast_check.py, .github/workflows/quality.yml, Makefile
added: 2026-09-13
---

**Problem.** Nothing enforces that KNOWN_SHORTFALLS only shrinks, so the contrast ledger could become the suppression list ui-color.md forbids in prose

**Why it matters.** `.claude/rules/ui-color.md` gives `KNOWN_SHORTFALLS` two
jobs and forbids a third use in prose: an entry may not be added to make a
change go green. Nothing checks that. The ledger is the one structure in the
tree whose whole purpose is to hold a failing measurement without failing, so
it is also the one place where a colour change can be waved through by editing
a list rather than a colour.

`PL-MHQK` is where this surfaced, and it is the inverse of that item's
finding. That item asked whether the block prints too often; the answer was no,
*because the list is shrinking* - three entries when it was written, one today
[2026-09-30: none since `#621`, see § "Re-confirmed" below],
`PL-GNN1` and `PL-GVXP` having closed. The decision to leave the printing alone
rests on that direction continuing, and the direction is exactly what nothing
enforces.

**Where.** `tools/contrast_check.py`, `KNOWN_SHORTFALLS` and `format_report`;
`.claude/rules/ui-color.md`, the paragraph forbidding an entry added to go
green.

**Decision needed.** Whether a check can express "only shrinks" at all, and
against what baseline. A count compared to a number committed in the file is
the cheap version and is self-defeating - the number is edited in the same
commit as the entry. Comparing against the merge base is the real version and
needs the tool to read a ref, which it does not today and which `PL-MHQK`
declined to add for the printing question. A third option is to leave it to
review and record here that it is deliberate, which is honest only if the
reason is written down where a reviewer of a colour change will read it.

Worth deciding *before* the list next grows rather than after: the first
wrongly-added entry is the one nobody notices.

**Done when.** Either a check enforces the direction against a baseline that
cannot be edited in the same commit as the entry, or the decision to leave it
to review is written into `.claude/rules/ui-color.md` beside the prohibition it
backs, where a reviewer of a colour change will actually read it. Deferring
without recording one of the two is the outcome this item exists to prevent,
so it is not an available ending.

**Re-confirmed 2026-09-30: the problem stands, but "only shrinks" is the wrong
property to enforce.** Three facts have moved since this was filed.

- **The list is empty**, and has been since `#621` (`PL-W8DQ`, 2026-09-15 CDT)
  cleared its last entry. The comment above `KNOWN_SHORTFALLS` says that is the
  state to keep it in, and that an empty list is no reason to delete the
  mechanism.
- **It has grown once, and that growth was correct.** Counted by parsing the
  dict at every commit that changed `tools/contrast_check.py`: 3 entries at
  `#183`, 4 at `#187`, then 3, 2, 1 and 0. `#187` fixed `MUTED`, and in the same
  change declared `ACCENT` as text on `PANEL` and `BACKGROUND` - no `ACCENT`
  requirement existed before it - found both failing, and listed them against
  `PL-30P6`, which fixed them in `#190`. No colour in either pair changed in
  `#187`. That is the use `ui-color.md` permits, "a shortfall you are
  tracking", and a check that the list only shrinks would have refused it.
- **Every agent the roadmap adds brings a colour** - nitrous oxide (planned
  item 6), the intravenous agents (items 13-15) - and the three agent colours
  the palette holds today are fixed by ISO 5360 (`app/theme.py`'s header).
  Judgment 4 of `ui-color.md` makes a fixed colour one to present around, never
  to change, which is exactly where an entry becomes the tempting way to go
  green.

So the property worth checking is the prohibition itself, not the direction:
**an entry added in the same change that introduces or alters either colour of
its pair.** That is decidable from the diff against the merge base, refuses the
case the rule forbids, and passes `#187`.

**Recommended: build that check** (session recommendation, 2026-09-30).
`tools/contrast_check.py --base <ref>` reads `KNOWN_SHORTFALLS` and the palette
at the base with `git show`, and fails on an entry the base lacks whose
foreground or background is new since the base or holds a different value
there. `make check` passes `--base origin/main`; the `checks` job in
`.github/workflows/quality.yml` passes the pull request's base, as its verify
replay already does, and already fetches full history. A base that cannot be
read fails rather than passing unread. What the check cannot decide goes into
`ui-color.md` beside the prohibition: an entry for an unchanged colour, which is
correct when a requirement is newly declared or a measurement changes, and not
when a layout change moved the element onto a surface it fails.

Not leaving it to review, the third option above: that guard would have to hold
at the moment a milestone brings a colour that cannot be changed, with nothing
to remind anyone it exists. And not the literal "only shrinks", which refuses
the one addition the list has had.

**Put to the owner 2026-09-30:** the Done when above asks for a check that
"enforces the direction". The recommended one enforces the prohibition instead
and allows growth where no colour changed. Build it in that form?
