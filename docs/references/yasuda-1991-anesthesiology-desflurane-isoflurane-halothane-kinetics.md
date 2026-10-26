# Yasuda et al. 1991, *Anesthesiology*: desflurane, isoflurane and halothane kinetics in volunteers

This note records the values and methods facts this repository takes from one
paper, with the page each sits on, so that no later session has to read the
paper again for them. The paper is held in the private corpus. Only facts and
short quotations cross into this repository. No table or figure is reproduced.

> Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
> Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in
> humans.* Anesthesiology 1991;74(3):489-98. PMID
> [2001028](https://pubmed.ncbi.nlm.nih.gov/2001028/), DOI
> [10.1097/00000542-199103000-00017](https://doi.org/10.1097/00000542-199103000-00017).

`docs/references/README.md` § "Yasuda et al. 1991 — the two human kinetics
papers" carries this citation and the companion *Anesth Analg* paper's.

Route and depth: the private corpus. The paper is a scan with no text layer, so
it was read as page images. Printed pages 489, 490 and 491 were read on
2026-10-26 for `PL-4QCJ`, and every fact below that cites them was checked
against them that day. Pages 492, 494 and 497 were read as page images on
2026-09-13. The facts below that cite those pages are as `PL-4QCJ` recorded
them then, and were not read again.

## The study

These facts are stated in the methods on page 490.

- **Subjects.** Eight healthy male volunteers, aged 25 ± 5 yr, weighing
  76 ± 7 kg, 182 ± 4 cm tall (mean ± SD).
- **What they breathed.** One cylinder held 2.0% desflurane, 0.4% isoflurane
  and 0.2% halothane, balance 35% oxygen and 65% nitrous oxide. It was given
  for 30 minutes through a non-rebreathing circuit. Before it, the volunteers
  breathed 70% nitrous oxide for 30 minutes.
- **Basal anesthesia.** 65% nitrous oxide with midazolam, fentanyl and
  vecuronium, for the first 150 minutes of elimination. Ventilation was
  controlled to an end-tidal CO2 of 5.5% to 6.5%.
- **Sampling.** End-tidal gas from the first five breaths, then at 0.75, 1,
  1.5, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25 and 29 minutes of administration.
  During elimination, from the first five breaths, then at the same early times
  and onward to 1,400 minutes, and each morning for 5 to 7 days.
- **The end of administration.** "Precisely at 30 min, administration of the
  volatile anesthetics was discontinued, and the breathing circuit was
  exchanged with a fresh inspiratory and expiratory circuit." So the inspired fraction of each potent agent during
  elimination was zero or near it. The paper does not state that fraction.

## The apparatus

Page 490 states each of these.

- **The end-tidal port and its dead space.** "End-tidal gas was sampled from a
  port at the tracheal tube. A small (about 50-ml) dead space composed of
  corrugated Teflon tubing was interposed between this sampling site and the
  connection to the nonrebreathing valve. The dead space served to protect the
  end-tidal sample from contamination with inspired gas."
- **The inspired sample.** "Inspired gas was collected from a port on the
  nonrebreathing valve just before the valve assembly."
- **The mixed expired sample.** The expiratory limb was corrugated Teflon
  tubing leading to a 1-l aluminium mixing chamber, which mixed alveolar and
  dead-space gas and had a port for the mixed expired fraction F_M. The
  chamber's output went to a spirometer.

## Values taken

| Quantity | Desflurane | Isoflurane | Where |
| --- | --- | --- | --- |
| F_A/F_I at 30 min of administration, mean ± SD | 0.90 ± 0.01 | 0.73 ± 0.03 | Abstract, page 489 |
| F_A/F_A0 after 5 min of elimination, mean ± SD | 0.14 ± 0.02 | 0.22 ± 0.02 | Abstract, page 489 |
| Recovery, the volume recovered per volume taken up, mean ± SD | 105 ± 25% | 102 ± 13% | Abstract, page 489 |

All values are stated in the text, n = 8. None was read from a figure.

Two halothane values from the same abstract are used too: an F_A/F_A0 after
5 min of elimination of 0.25 ± 0.02, and a recovery of 64 ± 9% (page 489).

**What the ratios mean.** F_A is the end-tidal fraction and F_I the inspired
fraction. F_A0 is "the alveolar concentration of anesthetic found immediately
before administration was discontinued" (page 491). The protocol lists no
sample at 30 minutes: its last sample during administration was at 29
minutes. So the "30 min" ratio is most likely the 29-minute sample, although
the paper does not say so.

**Where they are used.** The four F_A ratios are reference values in
`tests/reference/test_published_wash_in_and_elimination.py`. The recovery
values are cited in `docs/MODEL.md`, with halothane's 64 ± 9% as the same
method detecting an agent that is metabolized. Halothane's 0.25 is in
`docs/MODEL.md` § "Desflurane's residual, and why the parameter file was not
changed", as the top of the range of published five-minute ratios that an
explanation of desflurane's residual has to fit. None is a stored model
parameter, so the
adoption rules of `docs/MODEL.md` § "Source hierarchy" do not apply to them.

## How the alveolar fraction of ventilation was derived

- **Page 491.** F_M during the first 3 minutes was estimated from
  F_M = f_A × F_A + f_D × F_I, where f_A and f_D are the fractions of
  ventilation from the alveoli and from the dead space. f_A and f_D were
  averaged from the 10-, 15- and 20-minute samples, using the same formula.
- **Page 492, recorded 2026-09-13.** Alveolar ventilation is V_A = f_A × V_E,
  in the total-body-clearance method.
- **Page 494, recorded 2026-09-13.** The pulmonary elimination clearances and
  the total body clearances.

`docs/MODEL.md` § "Desflurane's residual, and why the parameter file was not
changed" rests on the apparatus facts above. Its conclusion is that the 50 ml
of tubing is a series dead space, which reduces alveolar ventilation, and
cannot carry desflurane's residual.

## Recorded elsewhere, and not repeated here

`docs/references/README.md` § "Yasuda et al. 1991 — the two human kinetics
papers" says where each of these is recorded, with its pages:

- the five-compartment fits (Tables 1 to 5), the fat-group blood flows of
  Table 5 (page 496) and the method behind them;
- each agent's hepatic rate constant k20 (Table 3, page 495);
- the F_A/F_I curve of Figure 2 (page 493), in
  `docs/references/yasuda-1991-figure-2-wash-in.md`.

## What was not taken

- The nitrous oxide values, and halothane's F_A/F_I at 30 min (0.58 ± 0.04),
  because the simulator models neither agent and no argument in this
  repository uses them.
- The gas chromatography and its calibration (pages 490 to 491), which nothing
  in this repository depends on.
