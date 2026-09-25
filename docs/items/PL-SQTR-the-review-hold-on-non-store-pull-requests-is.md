---
id: PL-SQTR
title: The review hold on non-store pull requests is not delivering review - the owner armed many in the browser unread because the manual merge felt slow, and 22 more carry the API-armed signature, 11 of those touching src/, tests/, CLAUDE.md or .github/
priority: P1
effort: M
status: needs-decision
classes: defect
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
---

**Problem.** `bin/docket arm` answers `hold` for any pull request that changes a path outside `docs/items/`, so that the owner's merge is a read before code reaches `main`. In practice it was a click.

**Evidence.**

- The owner, 2026-09-25: "I was annoyed with constantly having to manually hit merge since I felt slowed down, so I had frequently been hitting enable auto merge on GitHub without much due diligence", done "on the browser".
- A proxy scan by a reviewer subagent in `PL-NZC0`'s design round, not verified by hand: since 2026-09-23, 79 pull requests merged, 48 by auto-merge. Of those, 22 changing more than item files were armed with no commit message, which is the API signature: browser arming pre-fills the message with the description (`docs/maintainer.md`). Eleven of the 22 touch `src/`, `tests/`, `CLAUDE.md` or `.github/`: #931, #937, #941, #943, #946, #948, #957, #959, #980, #984, #992. Whether sessions armed those at the owner's request or unasked is open; the owner's browser arming would carry the description, so it probably accounts for other pull requests than these.
- No pull request since 2026-09-23 carries a GitHub review or review comment (0 of 79). Every one is authored by the owner's account, so that channel may not exist at all.

**Why it matters.** `docs/maintainer.md` says the maintainer reviews every safety-critical diff. A gate that fires on every pull request and almost never finds anything trains the click it was meant to prevent: complacency under multiple-task load "cannot be overcome with simple practice" (Parasuraman and Manzey, *Hum Factors* 2010;52(3):381-410, doi:10.1177/0018720810376055). It is `CLAUDE.md`'s "being routed around" test, so the fix goes first rather than to the roadmap.

**Decision needed, for the owner, with the recommendation.** Whether to take
each of the three below. The owner's answer of 2026-09-25 (#1006, quoted under
**Evidence.**) settled the question this item was captured with: the hold is
being clicked through. It did not settle these three.

1. **Recommended: a retrospective review.** A fresh session with a clean context and the strongest model reads every merged diff since 2026-09-23 that touches `src/`, `tests/` outside `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/` or `README.md`, against the safety-critical standard, and files what it finds. This is the one path by which an unread merge could have put a wrong clinical value on screen.
2. **Recommended: a risk-tiered gate in `bin/docket arm`.** It arms on green when every changed path is under `docs/items/` or `subprojects/docket/`, except `arming.py` itself, so the gate cannot loosen itself. It holds everything else, and those pull requests get a genuine read, helped by a short session-written summary of what changes and what proves it. This reopens `PL-WNCT`'s 2026-09-23 hold. Its kind is unrecorded: the hold was added in the decision paragraph, not taken on a session's recommendation. The evidence is the owner's own statement above. It is a new rule in an existing check, so the generator pause holds it unless the owner lifts it for this request.
3. **Recommended, now and until 2 is decided:** keep arming item-only and docket-only pull requests as before, but read anything touching the simulator paths in 1 before arming it.

Once decided, 1 and 2 become separate items.

**Done when.** The retrospective review is recorded, and the gate decision is taken and, if tiered, built with tests in `subprojects/docket/tests/`.

**Re-confirmed 2026-09-25 against 46954a81.** `arming.py`'s `Verdict` still
gives the hold reason "it changes N paths outside docs/items, which merge on
review" for every pull request that changes anything outside the store. The
owner's merge is therefore still the only review step, and the owner's own
statement above is the reproduction. The proxy scan's counts were not re-run.

**Generator check.** A one-off, raised by the owner. No record was misread:
`arm` reads its paths correctly and answers `hold`. What failed is the human
step the hold hands off to, with the owner's merge click standing in for a
read. No head's `misread:` states a fact that would have prevented that.
