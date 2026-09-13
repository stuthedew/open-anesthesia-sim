---
id: PL-FN5F
title: Decide whether to adopt Yasuda, Targ and Eger 1989 as the authority for the nine tissue:gas coefficients, and whether to store its figures rather than Gas Man's rounding of them
status: untriaged
added: 2026-09-13
---

**Decision needed.** Whether to (a) mark Yasuda, Targ and Eger 1989 `adopted`
for the nine stored tissue:gas coefficients and re-tier them from 3 to 1, and
(b) whether to then store that paper's published figures in place of Gas Man's
rounding of them. They are separate questions and (b) changes displayed values.

**What is now established** (`PL-B9K7`, 2026-09-13). The full text is held and
read. All nine stored tissue:gas coefficients sit within 0.71 SD of its measured
means and three reproduce them to the stored precision, so the coefficients
descend from a primary human measurement rather than from a simulator's choice.
`docs/MODEL.md` "Source hierarchy" makes that tier 1, and the only reason the
files still say tier 3 is that changing them is not a session's call.

**What (a) costs and buys.** It costs nothing numerical: the stored values do
not move. It buys an honest tier - the current one understates what is known -
and it retires the `provenance_gap` sentences in all three agent files, which
say no primary measurement is adopted for the coefficients. The one caution is
that the *blood:gas* values stay tier 3 and unadopted: this paper measured none,
its Table 2 tissue:blood figures being calculated from published age-adjusted
blood:gas. So the file would carry an adopted primary source for the tissue
coefficients beside an unadopted tier-3 one for blood:gas, and the note has to
be explicit or a reader will over-read it.

**What (b) costs.** Four of the nine differ from the published figures, and
three of those move a displayed time constant:

| | stored | Yasuda | tau now | tau adopted | change |
| --- | ---: | ---: | ---: | ---: | ---: |
| sevoflurane vessel-rich | 1.1 | 1.15 | 160 s | 168 s | +4.5% |
| isoflurane muscle | 4.5 | 4.40 | 7615 s | 7446 s | -2.2% |
| isoflurane fat | 70.0 | 64.2 | 156154 s | 143215 s | -8.3% |
| desflurane fat | 13.0 | 12.0 | 89762 s | 82857 s | -7.7% |

Every pinned reference state in `tests/reference/` is computed at the current
coefficients, so (b) means recomputing them - which is the work, not a
side effect. It would also break the cross-agent property `docs/MODEL.md`
"v0.2.0" rests on: today all twelve coefficients carry one reference
implementation's identical rounding, so every agent shares the same error, which
is what a MAC-normalized comparison needs. Adopting the published figures for
nine of twelve while three blood:gas values stay Gas Man's would end that.

**Recommendation: (a) yes, (b) no.** Take the tier, leave the values. The tier
correction is free and makes the files truthful; the value change costs a
reference-state recomputation, breaks the shared-error property, and buys
accuracy the model's own lumped three-compartment structure cannot use - the
vessel-rich group is one compartment standing for brain, heart, liver, kidney
and viscera, so 1.15 against 1.1 on a brain measurement is inside the error the
lumping already carries.

**Related.** `PL-D6LX` closed on the reasoning that the stored set is Gas Man's
and Yasuda was not adopted. This is the evidence that reopens the second half of
that, and the project owner took the original decision on 2026-09-03.

**Done when.** The owner has answered (a) and (b); the agent files and
`docs/MODEL.md` record the answer and its reasoning; and if (b) is yes, the
reference states are recomputed rather than the values changed under them.
