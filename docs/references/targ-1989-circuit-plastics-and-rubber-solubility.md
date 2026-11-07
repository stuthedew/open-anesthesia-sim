# Targ, Yasuda & Eger 1989: anesthetic solubility in a circuit's plastics and rubber

This note gives each fact this repository takes from one paper, with its page.

> Targ AG, Yasuda N, Eger EI 2nd. *Solubility of I-653, sevoflurane,
> isoflurane, and halothane in plastics and rubber composing a conventional
> anesthetic circuit.* Anesth Analg 1989;69(2):218-25. PMID
> [2764290](https://pubmed.ncbi.nlm.nih.gov/2764290/). PubMed gives no DOI.

I-653 is the code name desflurane carried before it had its name.

This is the **circuit** paper. Its companion has the same authors in another
order, and its title ends "in human tissues": Yasuda, Targ & Eger, *Anesth
Analg* 1989;69(3):370-3, PMID 2774233. That paper is the source of the tissue
coefficients that each agent's data file records, and `docs/MODEL.md`
§ "v0.2.0: isoflurane and desflurane" checks the stored coefficients against
it.

Route and depth: the project owner's own copy, kept outside this repository
(the private corpus), through the paper's text layer, printed
pages 218 to 222 and the reference list on page 224. It was first read in full
on 2026-09-13, and the facts below were checked against the text layer again
on 2026-10-26 for `PL-N701`.

## What was measured

- **The circuit** (page 220): three corrugated polyethylene tubes, a
  polypropylene Y-piece and elbow, a soda lime absorber with its inspiratory
  and expiratory valves, fresh soda lime with 15% water, a rubber bellows in a
  ventilator, and "a latex reservoir bag ... attached at the Y-piece elbow to
  simulate the patient's lungs". The ventilator was set to 500 ml at 25
  breaths per minute to circulate the gas.
- **Wash-in and washout** (page 220): one test at each flow. Wash-in at 0.5, 1
  and 2 L/min for 60 minutes, and washout at 1, 3 and 5 L/min for 120 minutes,
  of all four agents together from one tank, in 30% oxygen with nitrogen.
  Samples were taken from the expiratory limb, just past the expiratory valve.
- **Partition coefficients** (Table 1, page 220): each plastic or rubber
  component's coefficient against gas, after 6 to 9 weeks' equilibration.

## Values and facts taken

| Fact | Value | Where |
| --- | --- | --- |
| The assembled system's volume, by water filling | 9860 ml | Methods, page 220 |
| The order of the components' partition coefficients | halothane > isoflurane > sevoflurane > desflurane, from 7.5 min to 9 weeks | Results, page 220 |
| The "ideal" wash-in and washout line drawn against the data | % change = 100[1 − e^(−(V̇/Vs)t)], with V̇ the inflow and Vs the system volume | Figures 3 and 5, desflurane's wash-in and washout, pages 221 and 222 |
| The authors' reading for desflurane | absorption "by circuit components or soda lime should not hinder induction of or recovery from anesthesia" | Abstract, page 218 |
| The authors' reference 10 | Yasuda N, Targ AG, Eger EI 2nd, *Anesthesiology* 1988;69:A615, a conference abstract reporting the same tissue measurements as the companion tissue paper | References, page 224 |
| Each plastic or rubber component's partition coefficient against gas | not repeated here | Table 1, page 220 |

## Where the repository uses them

No fact from this paper is adopted as the authority for a stored value, as
`docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a
value" defines adoption.

- **The 9860 ml volume** is recorded in the reference circle system's data
  file (`src/anesthesia_sim/data/machines/reference_circle_system.json`) and
  in `docs/MODEL.md` beside the circuit volume. The measured system included
  the reservoir bag that stood in for the lungs, so the volume is an upper
  limit on the circuit's volume and cannot replace it (`PL-QBKQ`).
- **The desflurane reading and the ideal line.** From them, `docs/MODEL.md`
  § "Desflurane's residual, and why the parameter file was not changed" rules
  out circuit-wall absorption as a cause of desflurane's residual (`PL-XWCY`).
  The residual is that the simulator's desflurane washes out faster than it
  did in the volunteers of Yasuda et al. 1991.
- **Table 1's coefficients and their order** support the entry on the inert
  circuit in `docs/MODEL.md` § "Known limitations", which gives the
  coefficients. The model treats the circuit as absorbing no agent, which is
  most nearly true for desflurane and least true for halothane (`PL-LS3H`).
- **Reference 10.** Each agent's data file records that the 1988 abstract is
  a preliminary report of the 1989 tissue paper
  (`src/anesthesia_sim/data/agents/`, `PL-8GJ6`).

## What was not taken

- The coefficients for the mask plate, nasal airway, flask plug and stopcock
  grease, which are not parts of the circuit this model describes.
- The partition coefficients' approach to equilibrium (Figures 1 and 2), and
  the soda lime results for sevoflurane. The model has no absorber chemistry.
- The wash-in and washout curves' individual points.
