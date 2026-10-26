# Yasuda et al. 1991, *Anesth Analg*: sevoflurane and isoflurane kinetics in volunteers

This note records the values this repository takes from one paper, with the
page each sits on, so that no later session has to read the paper again for
them. The paper is held in the private corpus. Only facts cross into this
repository: values, their units, what was measured and in whom, and where they
sit. No table is reproduced.

> Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
> Peterson NA. *Comparison of kinetics of sevoflurane and isoflurane in
> humans.* Anesth Analg 1991;72(3):316-24. PMID
> [1994760](https://pubmed.ncbi.nlm.nih.gov/1994760/), DOI
> [10.1213/00000539-199103000-00007](https://doi.org/10.1213/00000539-199103000-00007).

`docs/references/README.md` § "Yasuda et al. 1991 — the two human kinetics
papers" carries this citation and the companion *Anesthesiology* paper's.

Route and depth: the private corpus, through the paper's text layer, printed
pages 316 to 319 and 322 and the reference list on page 324. Read on
2026-10-26 for `PL-Z3V5`. Each value below was checked against that text on
that day.

## The study

These facts are stated in the methods on page 317.

- **Subjects.** Seven healthy male volunteers, aged 23 ± 3 yr, weighing
  72 ± 9 kg, 182 ± 7 cm tall (mean ± SD).
- **What they breathed.** One cylinder held 1.0% sevoflurane and 0.6%
  isoflurane, balance 35% oxygen and 65% nitrous oxide. It was given as a
  square wave for 30 minutes through a non-rebreathing circuit. Before it, the
  volunteers breathed 70% nitrous oxide for 30 minutes.
- **Basal anesthesia.** 65% nitrous oxide with midazolam, fentanyl and
  vecuronium, for the first 150 minutes of elimination. Ventilation was
  controlled to an end-tidal CO2 of 5.5% to 6.5%.
- **Sampling.** End-tidal gas from the first five breaths, then at 0.75, 1,
  1.5, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25 and 29 minutes of administration.
  During elimination, from the first five breaths, then at 0.75, 1, 1.5, 2, 3,
  5 minutes and onward to 1400 minutes, and each morning for 6 to 7 days.
- **The end of administration.** At exactly 30 minutes the potent agents were
  stopped and the circuit was exchanged for a fresh inspiratory and expiratory
  circuit. So the inspired fraction of each potent agent during
  elimination was zero or near it. The paper does not state that fraction.

## Values taken

| Quantity | Sevoflurane | Isoflurane | Where |
| --- | --- | --- | --- |
| F_A/F_I at 30 min of administration, mean ± SD | 0.850 ± 0.018 | 0.733 ± 0.027 | Abstract, page 316 |
| F_A/F_A0 after 5 min of elimination, mean ± SD | 0.157 ± 0.020 | 0.223 ± 0.024 | Abstract, page 316 |
| Recovery, the volume recovered per volume taken up, mean ± SD | 101 ± 7% | 101 ± 6% | Abstract, page 316, and Table 6, page 322 |

All six values are stated in the text, n = 7. None was read from a figure.

**What the ratios mean.** F_A is the end-tidal fraction and F_I the inspired
fraction. F_A0 is "the alveolar concentration of anesthetic found immediately
before discontinuing administration" (page 318), which the abstract calls "the
last FA during administration". The protocol lists no sample at 30 minutes:
its last sample during administration was at 29 minutes. So the "30 min" ratio
is most likely the 29-minute sample, although the paper does not say so.

**Where they are used.** The four ratios are reference values in
`tests/reference/test_published_wash_in_and_elimination.py`, which compares
the simulator's wash-in and elimination with them. The recovery values are
cited in that module's docstring and in `docs/MODEL.md`, to show that
metabolism is negligible over five minutes of elimination. None is a stored
model
parameters, so the adoption rules of `docs/MODEL.md` § "Source hierarchy" do
not apply to them.

## A methods fact that other readings rest on

The paper did not measure partition coefficients. Its blood-flow and volume
estimates multiply "the tissue/blood partition coefficient (which we
determined previously)" by a fitted rate constant, and divide a volume by "the
tissue/gas partition coefficient" (page 319). Both cite its reference 3
(page 324): Yasuda N, Targ AG, Eger EI 2nd, the 1989 measurement of these
agents' solubility in human tissues. That is why the 1989 paper, and not this
one, is the source of the tissue coefficients this project stores.

## Recorded elsewhere, and not repeated here

`docs/references/README.md` § "Yasuda et al. 1991 — the two human kinetics
papers" says where each of these is recorded, with its pages:

- the five-compartment fits (Tables 1 to 5), the fat-group blood flows of
  Table 5 (page 322) and the method behind them;
- the elimination sampling schedule and each agent's hepatic rate constant k20;
- the F_A/F_I curve of Figure 2 (page 320), in
  `docs/references/yasuda-1991-figure-2-wash-in.md`.

## What was not taken

- The nitrous oxide values (F_A/F_I at 30 min of 0.986 ± 0.003, page 316),
  because the simulator does not model nitrous oxide.
- The desflurane and halothane curves in Figures 2 and 3. They are the
  *Anesthesiology* study's data, normalized to this study's isoflurane cohort
  (page 320), so they are not this paper's measurements.
- Table 6's total uptake and elimination volumes and the normalized recovery
  (page 322). Only the recovery percentages are used.
