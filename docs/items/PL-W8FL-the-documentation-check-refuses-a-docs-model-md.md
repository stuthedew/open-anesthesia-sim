---
id: PL-W8FL
title: The documentation check refuses a docs/MODEL.md paragraph whose test is named in the For-developers note below it, so every clinician paragraph that states a number must carry a test name or an item id; the prose review proposed moving them out on PL-BSYT and PL-ZDZ0 and was turned down for this reason
priority: P1
effort: S
status: done
classes: defect
feature: reader-first-prose
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md
deferred-from: v0.7.0 - captured after the freeze; it changes which paragraphs a documentation check accepts, not a displayed value
added: 2026-11-03
closed: 2026-11-04
pr: 2006
payoff: a docs/MODEL.md paragraph can tell a clinician what a readout means without test names and item ids in it, because the developer note below it may carry them
verify: grep -q 'def test_a_developer_note_holds_the_numeric_paragraphs_above_it' tests/unit/test_doc_check.py
---

**Problem.** In a `docs/MODEL.md` section that is held by its numeric paragraphs, such as § "Displayed precision", `_holds_its_figures` in `tools/doc_check.py` passes a paragraph only when the paragraph itself names a test, cites a source, gives a date, or says ``no test yet (`PL-XXXX`)``. A test named in the "**For developers.**" note below the paragraph does not count. `.claude/rules/plain-writing.md` sends test names and numerical detail to that note. So the rule and the check contradict each other, and the check wins because it fails the build. The clinician then meets 60-character test names and item ids in the middle of the paragraph that tells them what a readout means. `docs/MODEL.md` held 257 test names and 176 item ids on 2026-11-03.

**Measured 2026-11-03.** A rewrite of the MAC passage of § "Displayed precision", taken from `PL-ZDZ0`'s branch at `e4ae4220a`, named all three tests in a developer note directly below two clinician paragraphs. The check failed it with one error for each clinician paragraph. The same rewrite with one test name moved back into each paragraph passed. In `PL-BSYT` and in `PL-ZDZ0`'s pull request (#1992), the prose review proposed moving the test names to the note, and the session turned it down for this reason.

**Reproduced 2026-11-04.** With the MAC rewrite that the owner approved in `PL-J1ZM` applied to `docs/MODEL.md` at `ad573142c`, `uv run python tools/doc_check.py check` exits 1. Its one error is on the clinician paragraph, which it says "names no test and does not declare that it has none". The developer note directly below that paragraph names all three tests. The same tree without the rewrite exits 0.

**Why it matters.** Until the check accepts a test named in the note, every rewrite of § "Displayed precision" has to leave test names and item ids in the paragraphs a clinician reads. Seven `docs/MODEL.md` rewrite items wait on this fix for that reason: `PL-BSYT`, `PL-J37P`, `PL-9331`, `PL-PS5H`, `PL-XBJ3`, `PL-XT53` and `PL-YVL0`.

**Recommended.** Let a "**For developers.**" note hold the numeric paragraphs directly above it, back to the previous heading or the previous note, when the note names a test or says one is owed. The run stops at the first paragraph that passes on its own. A date or a published source in the note holds only the note itself. The note is then the one place the test is named, so no hidden marker has to repeat it. The tie is no looser than today's, where one named test holds every figure in its paragraph whether or not it computes them. Keep `PL-TCD3`'s rule that a `provenance:` or `derived:` marker holds only the figures it ties.

**Narrowed 2026-11-04, after both blind reviews.** The first version held every numeric paragraph back to the heading. § "Displayed precision" has no subheading, so one note after the MAC passage held the older paragraphs on parameter spread and wash-in times, which its test does not compute. The note's test name also hid those paragraphs' own ``no test yet (`PL-19W8`)`` and (`PL-TDX0`) forms from the queue, so closing either item would have failed nothing. Now the note's reach stops at a paragraph that names a test, declares one owed, or passes by a date, a source or its markers, and that paragraph's own form is the one checked. The closed-declaration error now says the test is named where the declaration stands, since that may be the note.

**Done when.** The `PL-ZDZ0` rewrite with its tests named only in the developer note passes `uv run python tools/doc_check.py check`. A test pins that a note holds the paragraphs above it and not the ones below it.

**Generator check.** One mechanism, found twice so far. It is a check refusing correct work, which the product-focus rule treats as blocking, so it is a defect fix and the pause on new workflow mechanisms does not hold it.
