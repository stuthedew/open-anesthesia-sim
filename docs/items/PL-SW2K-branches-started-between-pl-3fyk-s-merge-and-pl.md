---
id: PL-SW2K
title: Branches started between PL-3FYK's merge and PL-0TD9's write start mode's old empty start commit onto a tree already carrying claims.py, so claims.holdings reads them as claiming nothing; re-pointing CUTOVER_MARKER at a file PL-0TD9 creates would close the window
status: done
feature: claim-record
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py
added: 2026-09-24
closed: 2026-09-24
verify: grep -q 'CUTOVER_MARKER = "subprojects/docket/src/docket/claiming.py"' subprojects/docket/src/docket/claims.py
---

**Problem.** Branches started between PL-3FYK's merge and PL-0TD9's write start mode's old empty start commit onto a tree already carrying claims.py, so claims.holdings reads them as claiming nothing; re-pointing CUTOVER_MARKER at a file PL-0TD9 creates would close the window

`claims.CUTOVER_MARKER` is `claims.py` itself, so every commit on a branch forked after `PL-3FYK` merges counts as made after claims were recorded, and its leading ids claim nothing. But `bin/docket claim` arrives only with `PL-0TD9`; until then start mode still tells a session to push an empty start commit (`PL-3FYK: start` is one), which carries no `Claim:` trailer. A branch started that way and still unlanded when `PL-N162` switches `flight` onto `claims.holdings` holds nothing it is working. `PL-J9S0`'s check fails such a branch once it lands, which is the designed catch for a forgetful session, but only where the check runs.

**Decision for the project owner**, because it reopens the design round's ratified choice of marker (`PL-MB2W` § "Migration": a claim commit is legacy when its own tree lacks `subprojects/docket/src/docket/claims.py`).

**Recommended: re-point `CUTOVER_MARKER` in `PL-0TD9` at a file that lands with the `claim` command**, so "legacy" means "made before a session could write a trailer" and the window closes exactly, for one constant and its test. The alternative is to accept the window: it runs from `PL-3FYK`'s merge to `PL-0TD9`'s, and closes itself as those branches land or claim.

**Answered 2026-09-24: yes** (project owner, 2026-09-24, ratified, over accepting the window until `PL-0TD9` lands). It rides `PL-0TD9`'s pull request, because the marker has to first appear in the same change as the `claim` command; `PL-0TD9`'s brief carries the instruction.
