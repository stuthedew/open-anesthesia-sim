---
id: PL-VJZK
title: A reader-set agent price makes a displayed economic value's provenance partly the reader's, so the stored price needs its currency and the date it was set, and the display must not read as an authoritative figure
priority: P2
effort: M
status: blocked
classes: safety, anticipated
blocked-by: PL-B396
feature: preferences-store
touches: docs/MODEL.md, ROADMAP.md
added: 2026-09-16
---

**Problem.** A reader-set agent price makes a displayed economic value's provenance partly the reader's, so the stored price needs its currency and the date it was set, and the display must not read as an authoritative figure

**Why this is a safety item and not a schema convenience.** The project owner
wants the price reader-settable — "want user settable price eventually so user
can simulate cost at their institutions price" — with a shipped default
"intended for user to change". That makes a displayed dollar figure the
product of a number this project did not supply, which `CLAUDE.md`'s
safety-critical standard covers directly: a clinically meaningful displayed
value must be traceable to the exact inputs and transformations that produced
it, and presentation correctness is part of safety.

**What the store therefore owes each price:** the value, its currency, the
date the reader set it, and whether it is the shipped default or the reader's
own. Gas Man is the cautionary case — its defaults are "USA bottle volume and
bottle cost as of March 5, 2008", a figure now eighteen years stale that the
program presents exactly as it presents a reader's own.

**And what the display owes:** a cost figure must read as "at the price you
set", never as an authority. A shipped default in particular must not be
silently authoritative, because the whole point of shipping it is that it is
wrong for almost every institution.

**Decided now because the alternative is a migration.** Storing a bare float
and adding currency, date and origin later means every saved preferences file
needs upgrading.

**Why it matters.** A cost figure is in scope for the safety standard not
because money is clinical but because it is a monotone transform of modelled
agent consumption: a wrong price makes a *correct* consumption number carry a
wrong conclusion, which is `CLAUDE.md`'s presentation-correctness clause exactly.
Low-flow cost is also a teaching point rather than a decoration, so the figure
will be read as the lesson's punchline.

**The half nobody has designed is the display half, and it needs a category
that does not yet exist.** `CLAUDE.md` requires modelled/internal states to be
distinguished from measured or directly observable quantities — two categories.
A reader-supplied price is **neither**: not modelled by this project, not
measured by anyone here. So a cost readout needs a third visual tier meaning
"your assumption", distinct from both, and the modelled consumption figure it
derives from must stay on screen beside it so a reader-supplied number is never
the sole carrier of a modelled quantity.

**Which store it belongs in is settled** (`PL-MQHN`, 2026-09-17): a price is a
reader preference, because a second simultaneous value for it is incoherent
rather than merely unusual. `PL-B396` already records the shipped default the
same way.

**Blocked on the unit, and gated by the roadmap beyond that.** A price per litre
of vapour and a price per millilitre of liquid are different numbers, so
`PL-B396` lands first. Beyond that the readout itself is planned-milestone
item 28, which no release names — there is no version to put in `blocked-by`,
and this item is not startable until one does.

**Done when.** `docs/MODEL.md` states what a stored price carries — value,
currency, date set, and shipped-default-or-reader's — and what a cost readout
must show: the third provenance tier, the price and date it was computed at, and
the modelled consumption figure alongside it. `ROADMAP.md` planned item 28 names
that requirement rather than leaving it to the session that builds the readout.
