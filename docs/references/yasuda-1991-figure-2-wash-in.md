# Yasuda et al. 1991, Figure 2: the F_A/F_I curve during administration

This note records the early wash-in values read from Figure 2 of the two
Yasuda et al. 1991 papers, so that no later session has to read the figures
again. The papers are held in the private corpus, and their citations are in
`docs/references/README.md` § "Yasuda et al. 1991 — the two human kinetics
papers". Only facts cross into this repository: values, their units, and
where they sit. Neither figure is reproduced.

The values are used as reference values in
`tests/reference/test_published_wash_in_and_elimination.py`
(`PUBLISHED_WASH_IN_TIME_COURSE`). They are not stored model parameters.

Route and depth: the private corpus, read on 2026-10-18 for `PL-R0NL`. The
*Anesth Analg* paper's methods were read through its text layer, page 317, and
its Figure 2 from the page image of page 320. The *Anesthesiology* paper has no
text layer, so its methods were read from the page image of page 490 and its
Figure 2 from the page image of page 493.

## What the figures show

| Paper | Figure | Printed page | Cohort | Curves plotted |
| --- | --- | --- | --- | --- |
| *Anesth Analg* 1991;72:316-24 | 2 | 320 | 7 healthy men, 23 ± 3 yr, 72 ± 9 kg | N2O, sevoflurane, isoflurane, and desflurane and halothane from the other study |
| *Anesthesiology* 1991;74:489-98 | 2 | 493 | 8 volunteers | N2O, desflurane, isoflurane, halothane |

Each figure plots F_A/F_I, the end-tidal over the inspired fraction, as mean ±
SD against minutes of administration from 0 to 30. Each SD is drawn as a bar on
one side of the marker only.

The *Anesth Analg* figure's desflurane and halothane curves are not that
study's data. They come from the *Anesthesiology* study and were "normalized"
to the *Anesth Analg* isoflurane cohort (*Anesth Analg* page 320). So
desflurane is read from the *Anesthesiology* figure, which plots its own
cohort's measurements.

## The protocol behind the curves

These facts are stated in both papers' methods (*Anesth Analg* page 317,
*Anesthesiology* page 490):

- The potent agents were given together from one cylinder, as a square wave,
  through a non-rebreathing circuit, for 30 minutes. The cylinders held 1.0%
  sevoflurane and 0.6% isoflurane, or 2.0% desflurane, 0.4% isoflurane and
  0.2% halothane, each in 35% oxygen and 65% nitrous oxide.
- The volunteers had breathed 70% nitrous oxide for the 30 minutes before, and
  65% nitrous oxide carried on as basal anesthesia, with midazolam, fentanyl
  and vecuronium. Ventilation was controlled to an end-tidal CO2 of 5.5% to
  6.5%.
- End-tidal gas was sampled at the tracheal tube from the first five breaths
  and then at 0.75, 1, 1.5, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25 and 29 minutes.
  The *Anesthesiology* paper puts about 50 ml of tubing between that port and
  the non-rebreathing valve, and samples inspired gas at the valve.

So the inspired fraction was the cylinder's from the first breath. The
shipped simulator's circuit fills at its own time constant instead, which is
why the test drives the model with F_I held at the airway.

## How the values were read

Both papers survive in the corpus as 300 dpi bilevel scans, and neither page
has a text layer for the figure. The figure pages were extracted with
`pdfimages` and read by a script, in four steps:

1. **Axes.** A straight line was fitted to each axis. The scans are sheared:
   on the *Anesthesiology* page the y-axis leans 0.82 degrees from vertical
   and the x-axis 0.21 degrees from horizontal, and on the *Anesth Analg* page
   0.36 and 0.06 degrees. So a point is read by projecting it to each axis
   along the other axis's direction, not along the pixel grid.
2. **Ticks.** Each tick mark's centre was found on its axis. Values between
   ticks are interpolated linearly between the two nearest ticks, which
   absorbs the scans' uneven tick spacing of up to 3 pixels.
3. **Markers.** Each marker's centre was found by matching a template of its
   shape: a filled disc for sevoflurane and desflurane, and a hollow square for
   isoflurane.
4. **Error bars.** Each bar was followed outward from the marker to its first
   cap, and the SD is the distance from the marker's centre to the cap's
   centre.

Every marker then sits within 0.1 minute of a protocol sample time, except the
7.5-minute points, which sit at 7.40 to 7.48. The last point of every curve
sits at 30.0 minutes, although the protocol's last sample was at 29.

**The reading error is about 0.006 in a mean.** The 30-minute points read this
way can be compared with the values the papers' text states:

| Cohort | Read from Figure 2 | Stated in the text |
| --- | --- | --- |
| Sevoflurane, *Anesth Analg* | 0.846, SD 0.021 | 0.850 ± 0.018 |
| Isoflurane, *Anesth Analg* | 0.727, SD 0.032 | 0.733 ± 0.027 |
| Desflurane, *Anesthesiology* | 0.899, bar hidden | 0.90 ± 0.01 |
| Isoflurane, *Anesthesiology* | 0.731, SD 0.028 | 0.73 ± 0.03 |

A bar is hidden when it is shorter than the marker's radius, which is about
0.011 in F_A/F_I on the *Anesthesiology* figure.

## Values read

F_A/F_I, mean and SD. "SD read at" is the sample time whose bar gave the SD.
At 1 minute, three cohorts' bars are lost among overlapping marks near the
axis. There the SD is the cohort's next readable bar, a stand-in and not a
reading.

**Sevoflurane, *Anesth Analg* Figure 2, page 320.**

| Minutes | Mean | SD | SD read at |
| --- | --- | --- | --- |
| 1 | 0.563 | 0.047 | 2 min |
| 2 | 0.641 | 0.047 | 2 min |
| 3 | 0.683 | 0.034 | 3 min |
| 5 | 0.733 | 0.034 | 5 min |
| 7.5 | 0.760 | 0.031 | 7.5 min |
| 10 | 0.791 | 0.028 | 10 min |
| 12.5 | 0.801 | 0.029 | 12.5 min |
| 15 | 0.814 | 0.025 | 15 min |
| 20 | 0.829 | 0.024 | 20 min |
| 25 | 0.839 | 0.024 | 25 min |

**Isoflurane, *Anesth Analg* Figure 2, page 320.**

| Minutes | Mean | SD | SD read at |
| --- | --- | --- | --- |
| 1 | 0.436 | 0.048 | 2 min |
| 2 | 0.495 | 0.048 | 2 min |
| 3 | 0.529 | 0.040 | 3 min |
| 5 | 0.579 | 0.040 | 5 min |
| 7.5 | 0.616 | 0.041 | 7.5 min |
| 10 | 0.651 | 0.038 | 10 min |
| 12.5 | 0.664 | 0.037 | 12.5 min |
| 15 | 0.682 | 0.034 | 15 min |
| 20 | 0.701 | 0.035 | 20 min |
| 25 | 0.718 | 0.034 | 25 min |

**Desflurane, *Anesthesiology* Figure 2, page 493.** This figure plots no point
at 1.5 or 2 minutes. The 20-minute bar is hidden, so that point is not used.

| Minutes | Mean | SD | SD read at |
| --- | --- | --- | --- |
| 1 | 0.580 | 0.019 | 3 min |
| 3 | 0.731 | 0.019 | 3 min |
| 5 | 0.792 | 0.019 | 5 min |
| 7.5 | 0.832 | 0.019 | 7.5 min |
| 10 | 0.840 | 0.020 | 10 min |
| 12.5 | 0.872 | 0.020 | 12.5 min |
| 15 | 0.880 | 0.020 | 15 min |
| 20 | 0.899 | hidden | not used |
| 25 | 0.900 | 0.020 | 25 min |

**Isoflurane, *Anesthesiology* Figure 2, page 493.** This figure plots no point
at 1.5 or 2 minutes.

| Minutes | Mean | SD | SD read at |
| --- | --- | --- | --- |
| 1 | 0.414 | 0.027 | 1 min |
| 3 | 0.520 | 0.028 | 3 min |
| 5 | 0.569 | 0.032 | 5 min |
| 7.5 | 0.621 | 0.028 | 7.5 min |
| 10 | 0.641 | 0.041 | 10 min |
| 12.5 | 0.662 | 0.028 | 12.5 min |
| 15 | 0.682 | 0.028 | 15 min |
| 20 | 0.708 | 0.032 | 20 min |
| 25 | 0.724 | 0.027 | 25 min |

## What was not taken

- The points before 1 minute. Each figure crowds the first-breath and
  0.75-minute markers against the y-axis, so which sample time a marker
  belongs to cannot be read reliably.
- The nitrous oxide and halothane curves, which the simulator does not model.
- The *Anesth Analg* figure's normalized desflurane curve, for the reason
  above.
- The 30-minute points, because the text states those values.
