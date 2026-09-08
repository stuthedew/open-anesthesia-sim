---
id: PL-5K5C
title: Record the model's sea-level assumption and the vaporizer-class dependence of the delivered-concentration dial
priority: P1
effort: M
status: done
classes: docs, science
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-06
closed: 2026-09-07
pr: 458
verify: python3 tools/doc_check.py check && grep -q '760 mmHg' docs/MODEL.md && grep -q 'variable-bypass' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Assumptions" says only *"pressure is
constant"*. It does not say what the constant is. Every concentration in this
model is a fraction of one atmosphere — the symbol table, the readouts, the MAC
divisor, the tolerance in percentage points of one atmosphere — so the constant
is 760 mmHg and the model is sea-level-only, but that is inferred from the
units rather than stated. Two further things follow from it and are recorded
nowhere:

1. **The delivered-concentration control is a vaporizer dial**, and
   `app/controller.py`'s `ControlInput.DELIVERED` docstring says so. What that
   dial means in partial pressure — the quantity that produces the anesthetic
   effect — is device-class dependent away from 760 mmHg, and the two classes
   this project's three agents are drawn from behave in opposite directions.
2. **The identity holds at sea level for both classes**, which is why nothing
   in the model is wrong today. That is worth writing down as much as the
   limitation is, so a later reader does not "fix" a model that is correct.

**Why it matters.** Not a defect: no equation, parameter or displayed value is
wrong at 760 mmHg, and this item proposes no change to any of them. It is a
statement-of-applicability gap, and `CLAUDE.md` treats those as safety-critical
rather than tidy — a reader in Denver (about 630 mmHg) or Mexico City (about
585 mmHg) who sets 6% desflurane in this simulator and 6% on a real Tec 6 gets
two different anesthetics, and the simulator currently says nothing that would
warn them. It also puts a number on the "Known limitations" list that is
already there in spirit: `ROADMAP.md`'s v0.2.0 milestone explicitly excluded
"vaporizer-specific delivery-device physics (e.g. desflurane's heated,
pressurized vaporizer requirement)", and the exclusion never reached the model
specification.

**The physics, with sources, so the wording can be written without re-deriving
it.**

*Variable bypass* (sevoflurane, isoflurane here — Dräger Vapor 2000, Sevotec 5,
Isotec 5, Penlon Sigma Delta). Fresh gas is split between a bypass channel and
a chamber whose effluent is saturated at the agent's SVP, which depends on
temperature and not on ambient pressure. As ambient pressure falls the output
in volumes percent rises, and the delivered *partial pressure* is approximately
preserved, so the dial needs no altitude correction. Boumphrey & Marshall give
it as `%₁ = %cal × P_cal/P₁` with a worked example (isoflurane dialled 2% at
101.3 kPa delivers 4.05% at 50 kPa, both 2.026 kPa partial pressure).

*Gas–vapour blender* (desflurane, Tec 6/Tec 6 Plus). Desflurane is held at
about 39 °C, giving a vapour pressure of about 1460 mmHg, and pure vapour is
injected into the fresh gas stream; a differential pressure transducer holds
the vapour-circuit pressure equal to the fresh-gas-circuit pressure, so the two
flows stay in a fixed *ratio* set by the dial. Output is therefore a constant
volumes percent and the delivered partial pressure falls with ambient pressure.
Datex-Ohmeda states it directly: *"Decreased atmospheric pressure, with
altitude, does not significantly affect the concentration of agent delivered
(V/V), but decreases the partial pressure of the agent in the ratio of the
atmospheric pressure to the calibrated pressure of 760 mm Hg. To compensate for
the reduction of vapor pressure output at altitude, the rotary valve must be
advanced to maintain the required agent partial pressure."*

**One caveat that must not be lost if a number is ever stored.** The `1/P`
form above is the dilute-vapour limit of the flow-splitting physics
(`F ≈ k·SVP/(P − SVP)`, which reduces to `k·SVP/P` only when `SVP ≪ P`).
Isoflurane's SVP is about 240 mmHg at 20 °C, which is not small against 760,
so the exact splitting-ratio treatment predicts a larger rise in volumes
percent than `%cal × P_cal/P₁` gives, and a delivered partial pressure that
overshoots rather than holds. The direction and the device-class contrast are
not in doubt; the magnitude of the variable-bypass compensation is
approximate. Any implementation should derive it from the agent's SVP rather
than from the `1/P` shortcut, and this item's prose should say "approximately
preserved", never "unchanged".

**Where.** `docs/MODEL.md` § "Assumptions" (the `pressure is constant` line)
and § "Known limitations". Possibly also § "Delivery-limit and MAC parameters",
where `max_delivered_concentration_percent` already names each agent's real
device and is the one place the two vaporizer classes are implicitly both
present.

**Sources.**

- Datex-Ohmeda. *Tec 6 Plus Vaporizer* specification sheet, AN3307-A/1100,
  © 2000 Datex-Ohmeda Division, Instrumentarium Corp. Manufacturer statement,
  quoted above; also gives the 1–18% concentration range and a nomogram of dial
  setting against required output in mmHg at sea level, 1000 m and 2000 m.
  Supplied by the project owner 2026-09-06, read in full.
- Weiskopf RB, Sampson D, Moore MA. The desflurane (Tec 6) vaporizer: design,
  design considerations and performance evaluation. *Br J Anaesth*.
  1994;72(4):474–9. DOI [10.1093/bja/72.4.474](https://doi.org/10.1093/bja/72.4.474).
  PMID [8155456](https://pubmed.ncbi.nlm.nih.gov/8155456/). Primary. Source of
  the 39 °C / ~1460 mmHg figures and of the ±15% accuracy in oxygen. Retrieved
  from PubMed (metadata and abstract) and read in full from a PDF supplied by
  the project owner 2026-09-06.
- Andrews JJ, Johnston RV. The new Tec6 desflurane vaporizer. *Anesth Analg*.
  1993;76(6):1338–41. DOI
  [10.1213/00000539-199376060-00027](https://doi.org/10.1213/00000539-199376060-00027).
  PMID [8498675](https://pubmed.ncbi.nlm.nih.gov/8498675/). Primary; the
  flow-ratio mechanism — *"The pressure in the vapor circuit is electronically
  regulated to equal the pressure in the fresh gas circuit… vaporizer output is
  constant because the amount of flow through each circuit is proportional."*
  Retrieved from PubMed, abstract only.
- James MF, White JF. Anesthetic considerations at moderate altitude. *Anesth
  Analg*. 1984;63(12):1097–105. PMID
  [6239572](https://pubmed.ncbi.nlm.nih.gov/6239572/). Primary; the general
  case for reasoning in partial pressures rather than percentages at altitude,
  and it proposes MAPP in place of MAC for exactly this reason. Predates
  desflurane. Retrieved from PubMed, abstract only.
- Boumphrey S, Marshall N. Understanding vaporizers. *Contin Educ Anaesth Crit
  Care Pain*. 2011;11(6):199–203. Secondary synthesis (tier 2 under
  `docs/MODEL.md` § "Source hierarchy") — usable as the shape of the
  explanation, never as the authority for a stored number. Its § "Altitude"
  carries both classes side by side and is the source of the worked example
  above, subject to the caveat. Supplied by the project owner 2026-09-06, read
  in full.

**Done when.** `docs/MODEL.md` states that the model is specified at one
atmosphere and that this is what makes the delivered fraction and the delivered
partial pressure interchangeable; and its "Known limitations" records that
ambient pressure is not modelled, that the dial-to-partial-pressure
relationship is vaporizer-class dependent, and which class each of the three
shipped agents is drawn from — with the caveat above intact and no stored
numeric correction factor.
