---
id: PL-CVTG
title: Seven open items still name docs/MODEL.md in their touches or verify for sections that PL-CTXZ moved to docs/INTERFACE.md; PL-4DDW's verify greps MODEL.md for a value now in INTERFACE.md, so it fails even after a correct fix
priority: P3
effort: S
status: done
touches: docs/items/
added: 2026-11-14
closed: 2026-11-14
pr: 2160
payoff: an item's touches name the document its change edits, so a lane check sees two sessions editing docs/INTERFACE.md
verify: grep -q "verify: grep -q '0.25%' docs/INTERFACE.md" docs/items/PL-4DDW-docs-model-md-s-mac-awake-section-says-song-et.md
---

**Problem.** Seven open items still name docs/MODEL.md in their touches or verify for sections that PL-CTXZ moved to docs/INTERFACE.md; PL-4DDW's verify greps MODEL.md for a value now in INTERFACE.md, so it fails even after a correct fix

**Found 2026-11-14** in a review of the night's merges for regressions. The move of the interface sections (`PL-CTXZ`, #2109) re-pointed the prose of these items' briefs but not their `touches:` or `verify:` lines.

1. `PL-4DDW` (Song et al.'s standard deviation in the MAC-awake section): § "MAC-awake as a chart reference" is in `docs/INTERFACE.md`, and `docs/MODEL.md` holds no "0.25%", so `verify: grep -q '0.25%' docs/MODEL.md` would fail after a correct fix.
2. `PL-0P3F` (the accounting panel's 0.1 L step), `PL-NVT4` (scroll bar contrast, SC 1.4.11) and `PL-LKX7` (the 1280 px readout row): `touches:` named only `docs/MODEL.md`, whose text these items change now lives in `docs/INTERFACE.md`.
3. `PL-2NYN` (the delivered playback rate): the requirement is in both documents, so `touches:` now names both.
4. `PL-JP7P` and `PL-5C1H` (holding the numeric paragraphs of the interface and range sections to their sources): `touches:` lacked `docs/INTERFACE.md`.

`touches:` derives an item's lane and feeds `bin/docket concurrent`, so a stale path lets two sessions edit `docs/INTERFACE.md` at once without either seeing the overlap.

**Done when** each of the seven items names the document its change edits, and `PL-4DDW`'s `verify:` greps `docs/INTERFACE.md`.

**Generator check.** The cause is one move, `PL-CTXZ`, re-pointing the briefs it moved text out of but not their `touches:` and `verify:` lines. `PL-10BC` holds the same move's missed pointers in code and documents. That is two items from one finished move, not a mechanism still producing them, so it is not recorded as a generator.
