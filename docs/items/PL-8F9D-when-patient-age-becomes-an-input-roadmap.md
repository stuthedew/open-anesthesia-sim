---
id: PL-8F9D
title: When patient age becomes an input (ROADMAP planned-milestone item 30), age-adjust the MAC divisor, the 1 MAC line and the dial's 1 MAC start with Mapleson 1996's equation, MAC(age) = MAC at 40 x 10^(-0.00269 x (age - 40))
status: untriaged
added: 2026-11-14
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
