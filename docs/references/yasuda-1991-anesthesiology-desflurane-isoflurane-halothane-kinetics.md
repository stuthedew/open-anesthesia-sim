# Yasuda et al. 1991, *Anesthesiology*: desflurane, isoflurane and halothane kinetics in volunteers

This note gives the values and the facts about methods that this repository
takes from one paper, with their pages. None of them is a stored model
parameter: they are values the simulator is tested against, and facts that
`docs/MODEL.md` reasons from. No table or figure is reproduced, and the
repository holds no copy of the paper: read it through the PMID or DOI below.

> Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
> Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in
> humans.* Anesthesiology 1991;74(3):489-98. PMID
> [2001028](https://pubmed.ncbi.nlm.nih.gov/2001028/), DOI
> [10.1097/00000542-199103000-00017](https://doi.org/10.1097/00000542-199103000-00017).

Route and depth: the project owner's own copy, kept outside this repository
(the private corpus). The paper is a scan with no text layer, so it was read as
page images. Printed pages 489, 490 and 491 were read on 2026-10-26 for
`PL-4QCJ`, and every fact below that cites them was checked against them that
day. Pages 492, 494 and 497 were first read on 2026-09-13, and were read again
on 2026-11-11, when every fact below that cites them was checked against them
(`PL-56DQ`).

## Values recorded from the paper

**What the ratios mean.** F_A is the end-tidal fraction and F_I the inspired
fraction. F_A0 is "the alveolar concentration of anesthetic found immediately
before administration was discontinued" (page 491). The last sample during
administration was at 29 minutes (§ "The study"). So the "30 min" ratio is
most likely the 29-minute sample, although the paper does not say so.

| Quantity | Desflurane | Isoflurane | Halothane | Where |
| --- | --- | --- | --- | --- |
| F_A/F_I at 30 min of administration, mean ± SD | 0.90 ± 0.01 | 0.73 ± 0.03 | not taken | Abstract, page 489 |
| F_A/F_A0 after 5 min of elimination, mean ± SD | 0.14 ± 0.02 | 0.22 ± 0.02 | 0.25 ± 0.02 | Abstract, page 489 |
| Recovery, the volume recovered per volume taken up, mean ± SD | 105 ± 25% | 102 ± 13% | 64 ± 9% | Abstract, page 489; Table 6, page 497 |

All values are stated in the text, n = 8. None was read from a figure.

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

## How the paper derived alveolar ventilation, and its clearances

- **Page 491.** F_M during the first 3 minutes was estimated from
  F_M = f_A × F_A + f_D × F_I, where f_A and f_D are the fractions of
  ventilation from the alveoli and from the dead space. f_A and f_D were
  averaged from the 10-, 15- and 20-minute samples, using the same formula.
- **Page 492.** Total body clearance is the dose delivered to the alveoli,
  F_I × V_A × 30 min, divided by the area under the alveolar concentration
  curves of administration and elimination. Alveolar ventilation in that dose
  is V_A = f_A × V_E.
- **Page 494.** The pulmonary elimination clearances, defined as V_1 × k_10,
  were 4.11 ± 0.45 l/min for desflurane, 3.94 ± 0.34 l/min for isoflurane and
  3.94 ± 0.33 l/min for halothane, and did not differ among the three agents.
  The total body clearances were 4.6 ± 0.9 l/min for desflurane,
  4.8 ± 0.5 l/min for halothane and 4.0 ± 0.5 l/min for isoflurane. Those of
  desflurane and halothane were significantly greater than that of
  isoflurane. The page prints the last two spreads as "0.51/min", which reads
  as 0.5 l/min with the space before the unit lost. Each value is the mean
  of the eight volunteers. The text does not say what the spread after it
  is. The abstract and Table 6 give their values as mean ± SD.

## Where this repository uses these facts

- **The four desflurane and isoflurane ratios.** The simulator's results are
  tested against them.
- **The recovery values.** `docs/MODEL.md` cites them, and cites halothane's
  64 ± 9% as evidence that the same method detects an agent that is metabolized.
- **Halothane's 0.25, and the apparatus facts.** `docs/MODEL.md`
  § "Desflurane's residual, and why the parameter file was not changed" uses
  both. Desflurane's residual is the gap that remains when the breathing circuit
  is removed from the comparison. The simulator's desflurane then washes out
  faster than the volunteers' did, and its five-minute ratio falls below the
  published 0.14. Halothane's 0.25 is the top of the range of published
  five-minute ratios that an explanation of that gap has to fit. From the
  apparatus facts, that section concludes that the 50 ml of tubing is a series
  dead space, which reduces alveolar ventilation, and cannot explain
  desflurane's residual.
- **The ventilation derivation and the clearances.** The same section of
  `docs/MODEL.md` uses the page 491 formula and the page 492 definition to
  show that f_A is the alveolar fraction of total minute ventilation, and that
  it already excludes the 50 ml of tubing. It uses the page 494 pulmonary
  elimination clearances as a consistency check on the model's alveolar
  ventilation of 4.0 L/min, and does not adopt them as that ventilation.

## Other facts from this paper, and where they are recorded

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
