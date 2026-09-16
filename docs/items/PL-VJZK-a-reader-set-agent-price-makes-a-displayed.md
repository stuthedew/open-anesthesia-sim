---
id: PL-VJZK
title: A reader-set agent price makes a displayed economic value's provenance partly the reader's, so the stored price needs its currency and the date it was set, and the display must not read as an authoritative figure
status: untriaged
feature: preferences-store
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
