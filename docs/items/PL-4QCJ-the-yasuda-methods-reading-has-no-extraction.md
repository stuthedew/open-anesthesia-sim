---
id: PL-4QCJ
title: The Yasuda methods reading has no extraction note in docs/references/, so the facts PL-RFLN's conclusion rests on live only as prose in docs/MODEL.md
priority: P2
effort: M
status: blocked
classes: docs
feature: provenance
touches: docs/references, docs/MODEL.md
blocked-by: PL-Z3V5
added: 2026-09-13
---

**Problem.** The Yasuda methods reading has no extraction note in docs/references/, so the facts PL-RFLN's conclusion rests on live only as prose in docs/MODEL.md

**Where this came from.** `PL-XJ5P` (adopt the private reference corpus as the
route) merged as `#531` while `PL-RFLN` was in flight, and it established a new
obligation: "Reading a source from the corpus therefore owes an extraction note
in this directory." The Yasuda methods reading is the first reading that falls
under it and predates it by hours.

**What is unrecorded, and what rests on it.** The facts the reading produced
live only as prose in `docs/MODEL.md` § "Desflurane's residual, and why the
parameter file was not changed" and in the briefs of `PL-RFLN`, `PL-ZDWL` and
`PL-03ZG`:

- about **50 ml** of corrugated Teflon between the tracheal end-tidal sampling
  port and the connection to the nonrebreathing valve, stated to protect the
  end-tidal sample from contamination with inspired gas;
- the end-tidal port sited **at the tracheal tube**, with mixed expired gas
  sampled **separately** from a 1-l aluminium mixing chamber on the expiratory
  limb and reported as `F_M`;
- a nonrebreathing circuit, **exchanged for a fresh inspiratory and expiratory
  one at exactly 30 min**, so the potent agents' inspired fraction during
  elimination is zero by construction;
- minute ventilation measured and the alveolar fraction **derived** from
  `F_M = f_A x F_A + f_D x F_I`, averaged over the 10-, 15- and 20-minute
  samples;
- all three potent agents given simultaneously from one cylinder (2.0%
  desflurane, 0.4% isoflurane, 0.2% halothane, balance 35% O2 / 65% N2O), with
  65% nitrous oxide continued through the first 150 min of elimination.

`PL-RFLN`'s whole conclusion — that the published apparatus's dead space is an
alveolar-ventilation decrement and cannot carry desflurane's residual — rests
on the first two. None carries a page locator.

**Why it matters.** This is exactly the failure `PL-XJ5P` names: without a
note, the corpus is consulted once per *session* rather than once per *source*.
It has already happened twice for these two papers. `PL-ZDWL` is about to open
them a third time, and it is the natural session to write the note from, since
it will have the PDFs attached.

**Blocked on.** `PL-Z3V5`, which decides what an extraction note contains and
writes the first worked example. `docs/references/README.md` says so
explicitly: "What a note contains, and the first worked example, are
`PL-Z3V5`'s and are deliberately not fixed here." Do not invent the format
here. `PL-Z3V5` was stranded on `origin/claude/vibrant-curie-0x11e4` when this
was written; `PL-ZGK2` has since recovered it into the store, and
`bin/docket check` now reports it as ready to promote (corrected at triage,
2026-09-13). Only the format decision is outstanding.

**Also worth doing in the same pass.** `docs/MODEL.md` says of these two papers
that "neither is in PubMed Central, and neither is held in this repository".
Still true, and now incomplete: they *are* in the private companion corpus, and
a reader of the specification has no way to learn that from the sentence. One
clause pointing at `docs/references/README.md` § "Where owner-supplied full
texts live now" closes it.

**Done when.** The Yasuda methods facts above carry page locators in an
extraction note under `docs/references/`, in whatever shape `PL-Z3V5` settles,
and `docs/MODEL.md`'s "not held in `docs/references/`" sentence points a reader
at where they now are.

## Page locators now available, 2026-09-13

The *Anesthesiology* paper is now corpus holding
`yasuda-1991-kinetics-of-desflurane-isoflurane-and-halothane-in-humans.pdf` and
was read at full text as page images. The facts this item lists can now carry
locators, which was the gap:

- **p. 490**, § Materials and Methods - the end-tidal port, the dead space and
  its purpose, verbatim: "End-tidal gas was sampled from a port at the tracheal
  tube. A small (about 50-ml) dead space composed of corrugated Teflon tubing
  was interposed between this sampling site and the connection to the
  nonrebreathing valve. The dead space served to protect the end-tidal sample
  from contamination with inspired gas. Inspired gas was collected from a port
  on the nonrebreathing valve just before the valve assembly." Also on the same
  page: the 1-l aluminium mixing chamber on the expiratory limb supplying `F_M`;
  the circuit "exchanged with a fresh inspiratory and expiratory circuit" at
  precisely 30 min; ventilation controlled to normocapnea at end-tidal CO2
  5.5-6.5%; the cylinder mixture; and the subjects, eight healthy males aged
  25 +/- 5 yr, 76 +/- 7 kg, 182 +/- 4 cm.
- **p. 491** - the `F_M = f_A x F_A + f_D x F_I` formula and the 10-, 15- and
  20-min averaging.
- **p. 492** - `V_A = f_A x V_E`, in the total-body-clearance method.
- **p. 494** - pulmonary elimination clearances and total body clearances.
- **p. 497, Table 6** - recovery: desflurane 105 +/- 25%, isoflurane
  102 +/- 13%, halothane 64 +/- 9%.

**`PL-RFLN`'s foundation is now verified at the source rather than transcribed.**
The 50 ml figure and the port siting its conclusion rests on were read from the
paper directly and match what the earlier session recorded.

This does not unblock the item: `PL-Z3V5` still decides what an extraction note
contains, and the locators above are raw material for one rather than the note
itself.
## Triaged 2026-09-13

The dependency on `PL-Z3V5` (decide what a `docs/references/` extraction note
contains) is now declared in `blocked-by` with `status: blocked`, which is the
half `bin/docket next` reads, rather than stated only in the prose above.
`docs/references/README.md` forbids inventing the format here, so this is a
blocker rather than an overstated relationship. `PL-YPWT` is the item that
asked for that disposition and closes with it.
