# Katoh et al. 1993, *Anesth Analg* 77: MAC-awake of sevoflurane and isoflurane by slow and fast washout

This note records the values this repository takes from one paper, with the
page each sits on, so that no later session has to read the paper again for
them. The paper is held in the private corpus. Only facts cross into this
repository: values, their units, what was measured and in whom, and where they
sit. No table is reproduced.

> Katoh T, Suguro Y, Kimura T, Ikeda K. *Cerebral awakening concentration of
> sevoflurane and isoflurane predicted during slow and fast alveolar washout.*
> Anesth Analg 1993;77(5):1012-7. PMID
> [8214700](https://pubmed.ncbi.nlm.nih.gov/8214700/), DOI
> [10.1213/00000539-199311000-00024](https://doi.org/10.1213/00000539-199311000-00024).

`docs/references/README.md` § "Katoh et al. 1993 — MAC-awake of sevoflurane
and isoflurane" carries this citation and the companion paper's.

Route and depth: the private corpus, through the paper's text layer, all six
printed pages (1012 to 1017). Equation 1 on page 1013 and Table 1 on page 1014
are missing or garbled in the text layer, so both were read from page images.
Read on 2026-10-26 for `PL-P319`. Each value below was checked against the
paper on that day.

## The study

These facts are stated in the methods on pages 1012 and 1013.

- **Patients.** 49 ASA physical status I patients of either gender, having
  elective surgery of the lower abdomen, extremities or body surface. No
  premedication, and no intravenous anesthetic at any point.
- **Groups.** 28 received sevoflurane and 21 isoflurane. Each agent's group
  was randomly split into a slow-washout and a fast-washout arm: 12 and 16 for
  sevoflurane, 12 and 9 for isoflurane (Table 1, page 1014).
- **Anesthesia.** Inhalational induction in oxygen, a laryngeal mask without
  muscle relaxants, then 50% oxygen, the agent and balance nitrogen.
- **Gas analysis.** End-tidal gas was sampled at the laryngeal end of the
  mask at 200 mL/min by an infrared analyser (Capnomac Ultima). Its 10% to 90%
  response time was 740 ms for sevoflurane and 750 ms for isoflurane.
- **Before washout.** The end-tidal concentration was held at 0.5 MAC for
  15 min after the inspired-to-end-tidal difference fell below 10%.
- **Slow washout.** The end-tidal concentration was lowered in steps of 0.1%
  sevoflurane or 0.05% isoflurane. Each step was held for 15 min after the
  inspired-to-end-tidal difference fell below 10%, and the patient was then
  asked to open their eyes. MAC-awake is the midpoint between the
  concentration that permitted the response and the one that just prevented
  it. So the determination is descending and equilibrated.
- **Fast washout.** The inspired concentration was cut to near zero. MAC-awake
  is the end-tidal concentration at first eye opening, with the command
  repeated every minute.
- **Age correction.** Each MAC-awake was divided by the patient's own
  age-adjusted MAC, from the equations below.

## Values taken

| Quantity | Sevoflurane | Isoflurane | Where |
| --- | --- | --- | --- |
| Age-adjusted MAC, percent | 2.56 − 0.0156 × age (yr) | 1.43 − 0.0061 × age (yr) | Methods, page 1013 |
| Slow-washout MAC-awake as a ratio to age-adjusted MAC, mean ± SD | 0.34 ± 0.05 | 0.31 ± 0.05 | Abstract, page 1012, and Table 1, page 1014 |
| Slow-washout MAC-awake, end-tidal percent, mean ± SD | 0.63 ± 0.11% | 0.36 ± 0.08% | Table 1, page 1014 |
| Slow-washout arm's age, yr, mean ± SD | 45.9 ± 14.0 | 45.1 ± 15.7 | Table 1, page 1014 |
| Fast-washout MAC-awake as a ratio to age-adjusted MAC, mean ± SD | 0.22 ± 0.07 | 0.22 ± 0.05 | Abstract, page 1012, and Table 1, page 1014 |
| Calculated cerebral concentration at first eye opening, fast washout, arterial = end-tidal, fraction of MAC | 0.30 ± 0.07 | 0.26 ± 0.07 | Table 1, page 1014 |
| The same, with the end-tidal value corrected for dead-space gas, fraction of MAC | 0.34 ± 0.08 | 0.30 ± 0.08 | Abstract, page 1012, and Table 3, page 1016 |

All values are stated in the text or a table. None was read from a figure. The
slow-washout arms have n = 12 each. The sevoflurane slow-washout age prints as
"45.9 ± 2 14.0", where the stray 2 is most likely a typesetting fault, so the
SD is read as 14.0.

**The age-adjusted MAC.** The paper cites its references 11 to 14 for the two
equations: Stevens et al. 1975 for isoflurane, and Katoh and Ikeda 1987,
Scheller et al. 1988 and Nakajima et al. 1993 for sevoflurane (page 1017). It
does not say how the equations were derived from those studies. At age 40
they give 1.94% sevoflurane and 1.19% isoflurane. At the slow-washout arms'
mean ages they give 1.84% and 1.15%, which matches Table 1's mean MAC-awake
percent divided by its mean ratio (0.63 / 0.34 = 1.85 and 0.36 / 0.31 = 1.16).

**The brain-uptake calculation.** The brain is one well-mixed compartment, "a
one-compartment mass transport model like those of Fukui and Smith (4) or
Lowe and Ernst (5)" (page 1013). Its equation 1 is:

$$
\frac{dP_{Brain}}{dt} = \frac{CBF \cdot \lambda_{B/G} \cdot (P_{Art} - P_{Brain})}{V_{Brain} \cdot \lambda_{T/G}}
$$

Every patient was given the same rules for the flow and the volume, and the
same coefficients (page 1013):

- cerebral blood flow is 14.3% of cardiac output, with the cardiac index
  assumed to be 3.5 L/min/m², so it scales with body surface area;
- brain volume is 21 mL/kg of body weight, so it scales with weight;
- the blood:gas coefficient is 0.63 for sevoflurane and 1.36 for isoflurane;
- the brain:gas coefficient is 1.15 for sevoflurane and 2.09 for isoflurane.

Equation 2 (page 1013) takes the arterial partial pressure to equal the
end-tidal one. Equation 3 (page 1016) corrects for end-tidal gas being about
20% dead-space gas, as $`P_{Art} = (P_{ET} - 0.2\,P_I)/0.8`$. The abstract's
cerebral figures are the equation 3 ones. Neither set differs significantly
from the slow-washout MAC-awake (page 1014 and Table 3, page 1016). The paper
gives the time to 99% blood-brain equilibration as 11.8 min for isoflurane and
14.4 min for sevoflurane (pages 1014 and 1015). It uses this to justify the
15-minute steps of slow washout.

## Where the repository uses each value

- The slow-washout ratios, 0.34 ± 0.05 and 0.31 ± 0.05, are the stored
  `mac_awake.fraction_of_mac` and its standard deviation in
  `src/anesthesia_sim/data/agents/sevoflurane.json` and `isoflurane.json`.
  They are adopted as tier 1, primary measurement, under `docs/MODEL.md`
  § "Source hierarchy: what may be cited as the authority for a value".
- The age-adjusted MAC equations are named in each file's
  `mac_awake.mac_reference_basis`, as the denominator of the stored fraction.
- `docs/MODEL.md` § "MAC-awake as a chart reference" uses the equations, the
  slow-washout percents and the brain-uptake calculation. It compares the
  drawn band with Katoh's patients and explains why the band is read against
  the vessel-rich trace. None of these is a stored value.

## What was not taken

- The fast-washout MAC-awake percents and ratios as stored values. The band
  belongs against the vessel-rich trace, and the slow-washout figure is the
  one that matches the paper's brain estimate.
- Table 2's correlations of MAC-awake with the duration of anesthesia. Fast
  washout correlated with duration and slow washout did not (page 1014). The
  model has no use for the coefficients.
- The paper's own blood:gas and brain:gas coefficients, as stored values.
  They are inputs to Katoh's calculation only, and the simulator keeps its own
  coefficients. The paper cites Strum and Eger 1987 for sevoflurane's 0.63,
  Lerman et al. 1984 for isoflurane's 1.36 and Yasuda et al. 1989 for both
  brain:gas values (page 1013). The first two do not match what the agent
  files record from those papers. `sevoflurane.json` records Strum and Eger's
  measurement as 0.686, which is 8.9% above Katoh's 0.63. `isoflurane.json`
  records Lerman's adult value, aged 20 to 40, as 1.46, which is 7.4% above
  Katoh's 1.36. The paper does not say how its two figures were taken from
  those sources. Katoh's brain:gas values, 1.15 and 2.09, are within 5% of the
  vessel-rich tissue:gas coefficients this project stores, 1.10 and 2.10.

## The companion paper

> Katoh T, Suguro Y, Ikeda T, Kazama T, Ikeda K. *Influence of age on
> awakening concentrations of sevoflurane and isoflurane.* Anesth Analg
> 1993;76(2):348-52. PMID [8424514](https://pubmed.ncbi.nlm.nih.gov/8424514/).

It is held in the private corpus as a scan with no text layer. Pages 349 and
350 were read as page images on 2026-10-26. It studied 39 ASA I patients by
slow, equilibrated washout. Its MAC ratios are not the washout paper's: for
isoflurane it divides its regression line by the group MACs of Stevens et al.
(page 350), not by the linear equation above. Nothing is taken from it, and
pages 348, 351 and 352 were not read.
