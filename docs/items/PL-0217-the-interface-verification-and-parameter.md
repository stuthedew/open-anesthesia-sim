---
id: PL-0217
title: The interface, verification and parameter documents still mix British and US spelling in their own prose (modelled, vapour, litre), though PL-XF89 settled the tree on US spelling and PL-SRXT moved docs/MODEL.md to it
status: untriaged
feature: prose-quality
touches: docs/INTERFACE.md, docs/VERIFICATION.md, docs/PARAMETERS.md
added: 2026-11-22
---

**Problem.** The interface, verification and parameter documents still mix British and US spelling in their own prose (modelled, vapour, litre), though PL-XF89 settled the tree on US spelling and PL-SRXT moved docs/MODEL.md to it

**Found 2026-11-22**, closing `PL-SRXT` (US spelling in `docs/MODEL.md`), whose scope was that one document. Whole-word `grep -o -i -w` counts on the branch that closed it: `docs/INTERFACE.md` has modelled 41, vapour 37, litre or litres 15 and millilitre or millilitres 51; `docs/VERIFICATION.md` 5, 5, 6 and 7; `docs/PARAMETERS.md` 2, 12, 13 and 2. `PL-SRXT` left them because three other branches were sorting those documents at the time.

**Why it matters.** Mixed spelling in one document makes it look unedited, and a reader may wonder whether "modelled" and "modeled" mark two different things.

**Done when.** The own prose of `docs/INTERFACE.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md` uses US spelling: modeled, vapor, liter, milliliter, behavior. Text quoted from the interface, from a source or from a code name stays as written there, as `PL-SRXT` did. A label the screen shows with British spelling, such as "mL vapour", stays inside its quotation until `PL-KXRB` (the interface's own labels) changes the screen and its quotations together. A heading changes only with every citation of it.

**Generator check.** One-off: the remainder of `PL-SRXT`, split out by document. No head's `misread:` states the fact.
