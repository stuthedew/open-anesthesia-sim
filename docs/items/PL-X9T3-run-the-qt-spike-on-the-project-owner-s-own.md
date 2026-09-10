---
id: PL-X9T3
title: Run the Qt spike on the project owner's own machine and record frame cost, input latency and how it looks, which is the half no session here can measure
priority: P2
effort: S
status: done
classes: perf, ux
feature: teachable-case
touches: docs/WORKING_NOTES.md
not-delegable: the measurement has to run on the project owner's own hardware. `PL-2QMK` records why no session here can do it - the web container has no GPU and Flet's renderer cannot even load - and the whole point of this item is the number this container is structurally unable to produce.
verify: python3 tools/doc_check.py check && grep -qF 'Measured on real hardware' docs/WORKING_NOTES.md
added: 2026-09-08
closed: 2026-09-10
---

**Problem.** Run the Qt spike on the project owner's own machine and record frame cost, input latency and how it looks, which is the half no session here can measure

**The half no session here can do.** `PL-QXSB`'s Qt measurement is the
Python-side frame only: 0.51 ms to hand six traces and twelve readouts their new
values. Painting was unmeasurable — no GPU, a software rasteriser, an offscreen
platform plugin — and forcing a repaint gave 18-28 ms *including for an
unchanged frame*, which is an artifact rather than a figure.

**Why it matters.** It is the load-bearing half of `PL-QXSB`'s evidence. The
Python-side number already favours Qt by forty-fold, but the term it leaves out
is the one a reader actually experiences, and a decision to rewrite the
interface on half a measurement would be exactly the "recommend first, research
afterwards" `CLAUDE.md` names. It is also the item most likely to *stop* the
port cheaply, which is worth as much as the one that starts it.

**What to record**, on the owner's machine, at 1x and 300x:

1. **Frame cost** — the same three-stage split `PL-YSZN` used on Flet, so the
   numbers are comparable rather than merely favourable.
2. **Input latency** — how long a callback that is ready to run waits. That is
   what "laggy" named, and Flet's is 20-30 ms p90 after `PL-KP7H` and `PL-R2YM`.
3. **How it looks.** Whether six traces are distinguishable, whether the type
   is legible at the sizes the dashboard uses, and whether a drag feels
   immediate. No measurement substitutes for looking at it.

**Done when** the three are written into `docs/WORKING_NOTES.md` beside
`PL-QXSB`'s own measurements, so the decision reads one comparison rather than
two. **Under a heading containing the exact phrase "Measured on real
hardware"**, which is not a style rule: it is what this item's `verify:`
greps for, so the command names something only this item's own work creates.

**Why the command is not the obvious one.** It was
`grep -q 'PL-X9T3' docs/WORKING_NOTES.md`, and on 2026-09-08 `PL-55DH` wrote a
section whose *heading* cites this item - correctly, since that section is
where the spike's own measurements live and this is what will sit beside them.
That satisfied the grep while none of the work had been done. It is the same
defect `PL-X7VY` carries for `PL-XH1D`, arriving by a different route: a
command satisfied by another item's work proves nothing, and `docket verify`
would accept a branch that did none of this. Fixed here rather than filed,
because it is this item's own front matter and the repair is the command the
`docket` skill already prescribes.

## Started, 2026-09-08: the qualitative half, from the project owner

**Two observations, and the pair is more useful than either.** The first was
made before the spike had been run, about the *Flet* application after
`PL-2FM6` removed the sample store: "now that we dropped the M4 stuff, I don't
really notice a difference in performance. Maybe we don't need pyside." The
second, after running the spike: "I like it better."

**So the premise `PL-QXSB` opened on has expired.** That item was raised on
"It shouldn't be this laggy", and the lag is what every one of the seven items
before it was spent on. The owner now reports the Flet build as acceptable. A
migration argued from lag is therefore arguing from a symptom that is gone,
and re-deriving it would be the "recommend first, research afterwards"
`CLAUDE.md` names.

**What the preference is, and what it is not.** "I like it better" is real
evidence and it is the third of the three things this item asks for - whether
six traces are distinguishable, whether the type is legible, whether a drag
feels immediate. It is not the first two. Frame cost and input latency are on
the spike's own instrument panel and are still unrecorded, and this item does
not close on a preference.

**Still outstanding, and both are one look at the running window** - the
instrument panel's `median` and `p90` columns, at 1x and at 300x:

1. **`paint`** - the term `PL-QXSB` could not measure at all and the reason
   this item exists. Offscreen here it read 24-34 ms, which is a software
   rasteriser with no GPU rather than a paint cost.
2. **`timer lateness`** - `PL-X9T3`'s "how long a callback that is ready to
   run waits", against Flet's 20-30 ms p90 after `PL-KP7H` and `PL-R2YM`.
   Zero in this container because `--self-check` drives its own frames.

`advance`, `refresh` and `handoff` are worth recording at the same time, but
they are not the outstanding question: `PL-55DH` measured all three here and
the ratios travel even where the absolute figures do not.

## Closed, 2026-09-10: measured

The project owner ran the spike on their own machine and read the instrument
panel at 1x and 300x. The numbers, what they settle and what they do not are in
`docs/WORKING_NOTES.md` under "Measured on real hardware: the Qt spike's paint
cost and input latency". In short:

- **`paint` 8.04-9.21 ms median.** The container's 18-34 ms was an artifact of
  a software rasteriser with no GPU, overstating it about fourfold - which
  `PL-QXSB` predicted and is the reason this item existed.
- **`timer lateness` 0.85-2.46 ms p90**, against Flet's 20-30 ms. This is the
  axis "laggy" named.
- **The whole frame, paint included, is 19.5-27.3 ms** of a 200 ms budget -
  less than Flet's `page.update()` alone, which was its Python side only.
- **How it looks** was answered first and separately: "I like it better",
  recorded when the item was promoted.

**One reading was not taken** and is worth having if `PL-GS3R` goes to more
columns: the same panel with the `Columns` selector at 600 rather than 150. The
container puts that at about +3.5 ms of `refresh` and +0.2 ms of `handoff`, and
whether the ratio holds on real hardware is one dropdown change. It is not
needed to close this item, which asked for frame cost, input latency and how it
looks at the shipped settings.

**The machine is recorded as macOS at build `0.4.12+g7e0ff5bb`** and no
further. A model and chip would make the absolute figures reproducible; the
ratios within one machine are what the decision rests on, and they do not need
it.
