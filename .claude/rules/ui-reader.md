---
paths:
  - "/src/anesthesia_sim/app/**"
---

# Who reads this screen

**An anesthesia clinician.** The teaching target is the resident
(`docs/consultant-brief.md`), so the floor of assumed knowledge is what a
first-year resident already has: MAC, MAC-awake and the endpoint difference
between them, what a tissue compartment is, what a partition coefficient does,
why a vessel-rich group fills before fat. The owner has ruled on this twice —
"the audience is an anesthesia provider, not a lay reader" (2026-09-05), and
again on 2026-09-08 — and both times the finding was that the screen still
explains those terms.

**So do not explain the domain on screen.** Explaining fundamentals to a
specialist is not caution, it is talking down to the reader, and it costs the
thing the chart is for: a panel that has to be read before the plot can be seen
is a worse teaching instrument than a clean one, however correct each sentence
in it is. `PL-6580` (strip the concentration chart's explanatory prose) is the
item that says so; `PL-B89V` is why this file exists.

## What the safety standard asks for here, and what discharges it

`CLAUDE.md`'s clinical-output standard is resident and is not restated here.
What is worth stating is the form it takes in this interface, because writing a
paragraph is the wrong reading of it and the most available one.

Traceability, model identity, units and the modelled/measured line are
discharged by **labels, units, named reference values and axis titles** — not
by sentences. The pattern is already in the source: `_mac_reference_text` says
"1 MAC sevoflurane = 2.0%" and `_mac_awake_reference_text` names the fraction,
divisor and band. Those are the standard met in the form it asks for. The
italic paragraph beside each of them is the tutorial, and it is the thing being
removed.

When you find yourself writing a sentence to satisfy the standard, the
question is which label, unit, axis title or reference value would carry it
instead. If none can, the statement belongs in `docs/MODEL.md`, which already
holds the full form of every one — §§ "MAC multiples as a display unit",
"MAC-awake as a chart reference", "F_A/F_I as a displayed ratio", "Minimum
displayed outputs", "Displayed precision".

## Standing text and conditional text are different categories

**Standing** text renders on every run regardless of state: section titles,
legend rows, axis titles, reference values, the educational-use disclaimer.
This is the budget under pressure, and it is where prose accumulates unseen,
because each addition is small and nothing sums them.

**Conditional** text fires only when its condition holds — a refused setting, a
run halted at the supported length, traces off the top of the axis, no
compartment selected. It is doing safety work at the moment a reader needs it,
it costs nothing when the condition is false, and a sentence there is
appropriate. Do not trade one for the other: moving a warning into standing
chrome so it is "always visible" makes it invisible.

## Before adding any standing text to `app/`

1. Would a trained anesthesia clinician already know this? Then it does not go
   on screen at all.
2. Can a label, unit, axis title or reference value carry it? Then use that.
3. Is it a caveat about what the *model* does that this reader could not infer?
   Then `docs/MODEL.md`, and a label pointing at the quantity it qualifies.
4. Only if it fails all three does it earn a sentence — and it is conditional
   text, tied to the state it warns about, unless it cannot be.

Do not add a paragraph and leave the trimming to a later review. Seven of them
reached the screen that way between 2026-09-03 and 2026-09-04, each defensible
alone.
