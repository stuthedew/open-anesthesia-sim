---
id: PL-CHF2
title: PL-TH7P asks for the near-duplicate print that PL-TZ7T shipped in #793, so an open ready item names a test (test_new_prints_candidate_duplicates) that will never exist and its verify command can never pass
priority: P2
effort: S
status: done
classes: housekeeping
touches: docs/items
added: 2026-09-20
closed: 2026-09-21
payoff: an open ready item that can never pass its verify stops being offered by bin/docket next, so no session spends its length rediscovering that #793 already shipped the work
verify: grep -q '^status: dropped' docs/items/PL-TH7P-docket-new-should-print-the-items-a-capture.md
---

**Problem.** `PL-TH7P` (`docket new` should print the items a capture might
duplicate) is `ready` and `P2`, and asks for the near-duplicate print that
`PL-TZ7T` shipped in `#793`. Its `verify:` pins a test by name -
`grep -rq 'def test_new_prints_candidate_duplicates' subprojects/docket/tests` -
and no test of that name exists or will: the work landed under
`test_new_names_an_existing_item_with_a_near_identical_title` and
`test_new_says_nothing_about_an_item_declaring_a_different_path` in
`subprojects/docket/tests/test_cli.py`, beside a whole
`subprojects/docket/tests/test_duplicates.py`. So the command fails on a tree
that already holds the behaviour, and no reading of its exit will ever say why
- a `grep` for a test name pins the *name*, never the behaviour, and fails
identically whether the work is absent or present under another `def`
(`PL-6TN8`, `PL-0M32`).

**Checked 2026-09-21** against `origin/main` at `c5e91328`, clause by clause of
`PL-TH7P`'s own **Done when**:

| `PL-TH7P` asks for | what `#793` (`4c282700`) shipped |
| --- | --- |
| prints candidates when any exist | `cli.cmd_new` calls `duplicates.near_duplicates`, prints `render.format_near_duplicates` |
| prints nothing when none do | `test_new_says_nothing_about_an_item_declaring_a_different_path` |
| never prompts, never blocks | searched before the write, printed after it, `return 0` on either path |
| a test for a capture that overlaps an existing item | `test_new_names_an_existing_item_with_a_near_identical_title` |
| a test for one that overlaps nothing | the same pair, plus `test_a_capture_declaring_nothing_searches_nothing` |
| `subprojects/docket/README.md` documenting it | § `docket new`, "It says when the capture may already be in the store, and files it anyway" |

**The one clause not shipped is the one that was measured wrong.** `PL-TH7P`
asks for title-word overlap as a *selector* - "open items sharing a significant
word with the new title". `PL-TZ7T` scored exactly that over the 1,362-item
store: it catches 0 of 13 known duplicate pairs at any threshold flagging fewer
than 768 pairs, and the only clusters it does find at a usable threshold are
the items *meant* to recur - sixteen "Triage the N captures on DATE", three
groups of release cuts and tags. It fires on the wrong set. The shipped key is
the declared path selecting and the title only ranking inside that selection,
which puts the true duplicate in the top 3 for 8 of 9 pairs. So the residual is
*refuted* rather than outstanding, and it stays findable: `duplicates.py`'s
module docstring, the `DISPLAY_FLOOR` comment and the README each carry the
refutation where a later session will meet it.

**Why it matters.** `PL-TH7P` is `ready`, so `bin/docket next` can offer it,
and the session that takes it spends its length rediscovering that the work is
done - the exact cost the near-duplicate print exists to stop, paid by the item
that asked for it. It is also a silent-wrong-answer surface of the kind
`CLAUDE.md` says to interrupt for: `docket check --verify` replays every open
item's command, and this one exits non-zero forever on a tree where the
behaviour is present, which is indistinguishable from an unstarted item.

**The disposition was already ruled, and deferred for one reason that has since
lapsed.** `PL-JKML`'s duplicate sweep (merged in `#796`) read this pair, put it
to an independent reviewer told to refute it - a stage that killed 25 of 42
candidate pairs, including one high-confidence same-finding - and recorded it
as a **high-confidence same-finding with `PL-TZ7T` as survivor**. It was one of
two rows the sweep deliberately did not act on, and the stated reason was that
`PL-TZ7T` was live on `origin/claude/recurrence-signal-feature-3hnynt`. That
branch merged as `#793` on 2026-09-20. `PL-TZ7T` already records `PL-TH7P` as a
repeat filing (`recurrences: 2026-08-30 PL-TH7P`), so once the drop lands the
store carries the link both ways.

**Nothing of `PL-TH7P`'s is lost with it.** Its two historical instances are
each recorded on the items themselves rather than only in its prose: `PL-2R01`
is `dropped` with `reason: duplicate of PL-68XK`, and `PL-0TRS`'s brief says
"Closed 2026-08-31 by `PL-020`'s work". Its file stays in `docs/items/` per the
rule that a drop is never a delete, so its brief remains the fullest statement
of the pre-`PL-TZ7T` evidence and the reason is what stops the finding being
re-raised.

**Done when.** `PL-TH7P` is `status: dropped` with a `reason` naming `PL-TZ7T`
and `#793` as what shipped the behaviour, `PL-JKML` as where the same-finding
ruling is recorded, and the title-only key as refuted rather than outstanding.
