---
id: PL-VJFQ
title: Nothing enforces that KNOWN_SHORTFALLS only shrinks, so the contrast ledger could become the suppression list ui-color.md forbids in prose
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: tools/contrast_check.py, .claude/rules/ui-color.md, tests/unit/test_contrast_check.py, .github/workflows/quality.yml, Makefile, tools/doc_check.py, docs/items/PL-KJXS-a-qbytearray-passed-where-qt-s-c-signature.md
added: 2026-09-13
closed: 2026-09-30
verify: grep -q 'in the change that introduces or alters its colour' tools/contrast_check.py && grep -q 'introduces or alters its colour' tests/unit/test_contrast_check.py && grep -q 'contrast_check.py --base origin/main' Makefile && grep -q 'contrast_check.py --base' .github/workflows/quality.yml
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

**Done when.** [superseded 2026-09-30: the owner's answer below replaced this with the narrower check's Done when] Either a check enforces the direction against a baseline that
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

**Answered 2026-09-30: build the narrower check** (project owner, 2026-09-30,
ratified, over the literal "only shrinks" check and over recording it for
review alone). The owner saw the failure message the check would print and
chose it as recommended.

**Done when.** `python3 tools/contrast_check.py --base <ref>` fails on a
`KNOWN_SHORTFALLS` entry the base lacks whose foreground or background is absent
from the base palette or holds a different value there, and says so in a block
naming each entry, the colour, and whether it is new or altered, with the remedy
(re-pick it, or fix what is drawn around it, per `ui-color.md` judgment 4). A
base that cannot be read fails and says what could not be read. `make check`
runs it with `--base origin/main`; the `checks` job runs it with the pull
request's base. Tests cover: an entry added alongside a new colour, alongside an
altered colour and alongside an altered background (each fails); `#187`'s shape,
an entry for an unchanged colour (passes); no entry added (passes, nothing
printed); an unreadable base (fails, named). `.claude/rules/ui-color.md` § "The shortfall list
is not a suppression list" says what the check decides and what stays with
review: an entry for an unchanged colour, correct for a newly declared
requirement or a changed measurement, not for a layout move onto a surface it
fails.

**Build notes, from the session that re-confirmed it** (stopped for length, not
for the work):

- `read_palette` reads every module under `app/` from disk through
  `app_modules`. For the base, list them with `git ls-tree -r --name-only <ref>
  -- src/anesthesia_sim/app` and read each with `git show <ref>:<path>`; move
  the AST walk into a helper that takes source text, so both readings share it.
- The base's keys: parse `git show <ref>:tools/contrast_check.py` and read the
  `KNOWN_SHORTFALLS` annotated assignment's literal keys.
- `Requirement.key` is `(foreground, background)` but `EitherRequirement.key` is
  `(label, background)` with a label of `"A or B"`, so map each new key to its
  requirement through `{r.key: r for r in REQUIREMENTS}` and compare every name
  in `candidates` plus `background`. A key naming no requirement is already
  reported as `stale_shortfalls`.
- Count the new findings into `Report.error_count`, which is the one place the
  error kinds are listed (`PL-TP75`).
- Wiring: the `Makefile` line running `tools/contrast_check.py`; in
  `.github/workflows/quality.yml`, the `checks` job's `contrast_check.py` step,
  which already has full history (`fetch-depth: 0`). Pass the base on
  `pull_request` through `env:` as the verify replay step passes
  `VERIFY_BASE: origin/${{ github.base_ref }}`, and run without `--base` on a
  push to `main`, where the pull request's run was the gate.
- Sweep the tool's module docstring ("Known shortfalls, and why they do not
  simply fail the build") and the comment above `KNOWN_SHORTFALLS`.
- The `verify:` pins the block header's words "in the change that introduces
  or alters its colour" in the tool and a test, and the two wiring lines. Keep
  them, or rewrite the verify in the same commit and say why.
