---
id: PL-VJZK
title: A reader-set agent price makes a displayed economic value's provenance partly the reader's, so the stored price needs its currency and the date it was set, and the display must not read as an authoritative figure
priority: P1
effort: M
status: done
classes: safety, anticipated
feature: preferences-store
touches: docs/MODEL.md, ROADMAP.md, docs/references/README.md, docs/items/PL-1P15-show-what-the-delivered-agent-cost-in-money-at.md, docs/items/PL-93B3-keep-a-reader-s-preferences-the-agent-price-and.md, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - deferred to Gate 3 on beat 3's terms (PL-DB64, project owner, 2026-09-27, ratified, over keeping it on the list): work planned-milestone item 28 would create, waiting on PL-B396; safety, but not live at 19af95d - nothing in src/ stores or displays a price, a currency or a cost
added: 2026-09-16
closed: 2026-10-26
pr: 1869
payoff: docs/MODEL.md states what a stored price carries and how a cost display shows that the price is the reader's, before any price is built
verify: grep -q 'A cost at the reader.s price' docs/MODEL.md && grep -q 'ISO 4217' docs/MODEL.md
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

**Scheduled in v0.7.0, 2026-10-25.** `PL-LF0P` scoped v0.7.0 with planned-milestone item 28, agent cost, inside it (project owner, 2026-10-25, ratified, over leaving item 28 unscheduled and deferring this item to Gate 4). `PL-YRLM` closed with that answer. This item is in `ROADMAP.md` § "v0.7.0 - the schematic" → "Required scope", so v0.7.0 clears it itself.

**It no longer waits on `PL-B396`.** This item is a specification in
`docs/MODEL.md`, and `PL-1P15`, which builds the price, waits on it.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): the `docs/MODEL.md` half is still to do, and the rest is narrower.** `docs/MODEL.md` says nothing yet about a price, its currency or its provenance. The `ROADMAP.md` half of **Done when** is met in substance: entry 9 of v0.7.0's Required scope states the requirement, where the session building the readout reads it, though it does not mention the modelled consumption figure. The shipped-default-or-reader's distinction has nothing to tell apart while v0.7.0 ships no price (entry 11). So what is left is the `docs/MODEL.md` text: a stored price carries its value, currency and date set, and a cost display shows the price as the reader's, the price and date it was computed at, and the modelled consumption figure beside it. The paragraph "Blocked on the unit, and gated by the roadmap beyond that" no longer applies: the item is `ready`, as the 2026-10-25 paragraphs say.

**Outcome, 2026-10-26.** `docs/MODEL.md` § "A cost at the reader's price"
is the specification. A stored price records its agent, a bottle price, the
bottle's volume in millilitres of liquid, an ISO 4217 currency code, and the
date on which the price applied. With no shipped price, the record has no
field for who set it, and the section says what changes if a release ships
one. Two choices were made here rather than put to the project owner, because
each had one clearly better option:

- **The price is taken per bottle** (over a price per millilitre, which
  `PL-1P15`'s brief left to this item). Institutions buy by the bottle, and
  Gas Man's Set Cost takes the bottle volume and the bottle cost (Workbook,
  printed p. 15). The derived price per millilitre is shown, so the entry
  mistakes the per-bottle form allows show on screen, except a swap of two
  close numbers, which the section names.
- **The date is the date on which the price applied, not the date it was
  typed in** (over the brief's "the date the reader set it"). The second blind
  review pass found that the brief's date measures nothing about staleness.
  Re-entering an old quote would stamp it with today's date. The entry offers
  the day of entry, for the reader to change.

The hazard table gained two rows, each declaring `no test yet (`PL-1P15`)`.
`tools/doc_check.py` then fails once `PL-1P15` closes without naming their
tests. The commissioned `verify:` command, `grep -qi 'currency'`, matched any
mention of the word. It is replaced by a check for the subsection's heading
and for "ISO 4217", which fails on `main` at `adc93274` and passes here.
