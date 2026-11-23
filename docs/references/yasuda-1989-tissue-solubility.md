# Yasuda, Targ & Eger 1989: anesthetic solubility in human tissues

This note gives each fact this repository takes from one paper, with its page.

> Yasuda N, Targ AG, Eger EI 2nd. *Solubility of I-653, sevoflurane,
> isoflurane, and halothane in human tissues.* Anesth Analg
> 1989;69(3):370-3. PMID [2774233](https://pubmed.ncbi.nlm.nih.gov/2774233/).

I-653 is the code name desflurane carried before it had its name. The
companion circuit paper, with the same authors in another order, has its own
note, `targ-1989-circuit-plastics-and-rubber-solubility.md`.

Route and depth: the private corpus, through the paper's text layer, printed
pages 370 to 373, read in full on 2026-11-23 for `PL-S5JJ`. The abstract was
read earlier on PubMed, on 2026-11-22, for `PL-5C1H`.

## The study

Tissues were taken at autopsy, within 48 hours of death, from 14 patients
whose mean age was 65.8 ± 14.4 years. Not every tissue came from every
patient, so each tissue has its own n, from 6 for brain to 10 for liver and
kidney (page 371, Table 1). Patients who died of infection or of a disease
that might alter tissue composition, such as congestive heart failure, were
excluded (page 370). Each tissue was homogenized in saline, equilibrated at
37 °C, and analysed by gas chromatography. The tissue:gas coefficient was then
found by mass balance (pages 370 and 371).

The tissue:blood coefficients are not measured. The paper calculates them "by
dividing the tissue/gas partition coefficient by the published values for the
blood/gas coefficients adjusted for age" (page 372).

## Values and facts taken

| Fact | Value | Where |
| --- | --- | --- |
| Tissue:gas means for brain, muscle and fat, with their SDs | recorded in `docs/PARAMETERS.md` § "Where the tissue:gas coefficients come from" | Table 1, page 371 |
| Tissue:gas means for all six tissues, and tissue:blood means for all six | transcribed in `tests/reference/test_parameter_source_figures.py`, beside `test_yasudas_full_tables_recover_the_blood_gas_ranges_printed` | Tables 1 and 2, page 371 |
| How Table 2 was computed | Table 1 divided by an age-adjusted published blood:gas coefficient | Methods, page 372 |
| The only correlation with age | muscle:gas and muscle:blood rose with age | Results and Figure 2, pages 372 and 373 |

## Where the repository uses them

- **The nine tissue:gas coefficients**, vessel-rich, muscle and fat for three
  agents, take this paper as their adopted authority at tier 1.
  `docs/PARAMETERS.md` § "v0.2.0: isoflurane and desflurane" compares each
  stored value with its mean.
- **The blood:gas values that Table 1 over Table 2 recovers** are compared
  with the stored blood:gas coefficients in the same section. The columns do
  not agree: the four organ columns recover nearly one value for each agent,
  and the muscle and fat columns recover more, by more than the tables'
  rounding explains. So the tables establish no single blood:gas value for
  this cohort. The paper is not the authority for any blood:gas value,
  because it measured none.

- **The brain:blood means for all four agents**, from Table 2, are quoted in
  `docs/VERIFICATION.md` beside this paper's citation. Those for desflurane,
  isoflurane and sevoflurane support leaving desflurane's vessel-rich
  coefficient unchanged, and halothane's is quoted only to complete the list.
  No stored or displayed value is computed from them. They were checked
  against the full text on 2026-11-23.

## What was not taken

- **Halothane's values as stored values**, because the simulator has no
  halothane agent. Its brain:blood mean is quoted, as above.
- **The heart, liver and kidney tissue:gas values as stored values**, because
  the model's vessel-rich group uses the brain value. They are used only to
  recover the blood:gas values above.
- **The paper's comparison with earlier studies** (page 373), which bears on no
  stored value.
