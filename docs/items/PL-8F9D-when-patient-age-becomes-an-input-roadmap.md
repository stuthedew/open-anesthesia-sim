---
id: PL-8F9D
title: When patient age becomes an input (ROADMAP planned-milestone item 30), age-adjust the MAC divisor, the 1 MAC line and the dial's 1 MAC start with Mapleson 1996's equation, MAC(age) = MAC at 40 x 10^(-0.00269 x (age - 40))
priority: P1
effort: M
status: blocked
classes: feature, safety
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/app/formatting.py, docs/MODEL.md, docs/INTERFACE.md
blocked-by: v0.8.0
deferred-from: v0.7.0 - not live: checked 2026-11-22, the tree has no patient age input, so no user can set an age and see a MAC that ignores it; the work waits on PL-LBVN and on planned-milestone item 30
added: 2026-11-14
payoff: once a user can set the patient age, every MAC figure on screen is the MAC for that age rather than for a 40-year-old
---

**Problem.** When patient age becomes an input (ROADMAP planned-milestone item 30), age-adjust the MAC divisor, the 1 MAC line and the dial's 1 MAC start with Mapleson 1996's equation, MAC(age) = MAC at 40 x 10^(-0.00269 x (age - 40))

**Asked for by the project owner** (2026-11-14, on `#2155`): "Lets get a
source for the age. Gold standard. Do research MAC is age adjusted when used
and will be a feature of the app at some point (change age)".

**The source, read 2026-11-14.** Mapleson WW, Effect of age on MAC in humans:
a meta-analysis, Br J Anaesth 1996;76(2):179-185, PMID 8777094,
https://doi.org/10.1093/bja/76.2.179, read from its PubMed abstract. For age
over 1 year, "MAC = a x 10^(bx) where x = difference in age (in years) from 40,
b = -0.00269 (95% confidence limits (CL) -0.0030, -0.0024) and a = MAC at age
40 yr": isoflurane 1.17%, sevoflurane 1.80%, desflurane 6.6%, "with 95% CL of
approximately +/- 7% (+/- 10% for desflurane)". The slope is about 6% per
decade and is the same for every agent. Nickalls RWD, Mapleson WW, Age-related
iso-MAC charts for isoflurane, sevoflurane and desflurane in man, Br J Anaesth
2003;91(2):170-174, PMID 12878613, https://doi.org/10.1093/bja/aeg132, read in
full from the private reference corpus, restates the equation as its Equation
1 and gives in its Table 1 the MAC at 1, 40 and 80 years: isoflurane 1.49,
1.17, 0.91; sevoflurane 2.29, 1.80, 1.40; desflurane 8.3, 6.6, 5.1. Its Table 1
gives the 95% CL as 6% of MAC at 40 for isoflurane and sevoflurane and 10% for
desflurane, "up to 1% greater" at 1 and 80 years. It also notes that later MAC
data of Fragen and Dunn, Nakahara and colleagues, and Eger agree with
Mapleson's.

**What it needs first.** The stored MAC must be an age-40 value for this
equation to apply to it. The stored 2.0%, 1.2% and 6.0% are De Wolf et al.
2012's ageless adult values, 11.1% above, 2.6% above and 9.1% below
Mapleson's age-40 values. `PL-LBVN` holds that decision. With an age input, the
divisor, the 1 MAC line, the dial's starting position and the MAC-awake band
all follow the patient's age, and the interface must show the age the MAC is
for.

**Checked 2026-11-22.** The tree has no patient age. A search of `src/anesthesia_sim/` for an age finds only docstrings that say the model has none, in `app/formatting.py` and `app/bookmarks.py`. `PL-LBVN` stores Mapleson's age-40 values as `mac_at_age_40_percent` in the three agent files. Its `core/mac.py` `mac_for_patient` is the one function that builds a run's MAC. It takes the patient but uses nothing from it: it returns the agent's MAC at age 40 with the age from `MAC_STORED_AT_AGE_YEARS` in `core/parameters.py`, because the reference adult has no age. This item's work is to make that function read the patient's age and apply Mapleson's equation. The compared chart already refuses runs whose MAC or age differ, so two patients of different ages cannot share one 1 MAC line unnoticed (`app/chart_frame.py`'s `assemble_chart_frame`).

**Why it matters.** MAC falls by about 6% per decade of age (Mapleson 1996, above). Once a user can set the patient's age, every MAC multiple, the 1 MAC line and the dial's 1 MAC start must use the MAC for that age. Otherwise each MAC figure on screen is wrong for the patient shown. The owner asked for age-adjusted MAC as a core feature (project owner, 2026-11-14, recorded in `PL-LBVN`).

**What it waits on.** The item waits on an age input, which is planned-milestone item 30 in the roadmap's Beyond row. No release schedules item 30, and what v0.8.0 holds is the owner's pick when it is scoped, so the item is blocked on v0.8.0 as well. A session that scopes v0.8.0 without item 30 moves that blocker on.

**What is already built.** `PL-LBVN` stored the age-40 values and added the one function that builds a run's MAC (closed 2026-11-22).

**Done when.** With an age input, the one function that builds a run's MAC applies Mapleson's equation. A test checks it at 1, 40 and 80 years for each agent against values worked out from the equation, which agree with Nickalls and Mapleson 2003's Table 1. The MAC-awake band, the 1 MAC line, the dial's start and every MAC multiple follow the patient's age. The interface shows the age each 1 MAC is for, and `docs/MODEL.md` and `docs/INTERFACE.md` describe the divisor as the MAC for the patient's age. `PatientMac` (`core/mac.py`) refuses an age outside the range the age input accepts. Today it refuses only an age of zero or less, which was enough while every run's age is 40, and Mapleson's equation is stated for ages of 1 year and more.

**Generator check.** This is work the owner asked for, not a defect, so no fact was misread.
