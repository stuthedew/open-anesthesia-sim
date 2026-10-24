---
id: PL-YH6Z
title: The wash-in hover prints the crossing column's F_A/F_I above 1 under the label 'Wash-in F_A/F_I', a value app/wash_in.py classes as elimination and refuses to show as wash-in
status: untriaged
feature: replay-findings
added: 2026-10-24
---

**Problem.** The wash-in hover prints the crossing column's F_A/F_I above 1 under the label 'Wash-in F_A/F_I', a value app/wash_in.py classes as elimination and refuses to show as wash-in

**Evidence.** All three panel reviewers and both generalist runs raised this on `#578`, and the blind checker reproduced it at that merge: a default sevoflurane run with the vaporizer shut at 600 s hovers its terminus dot as "Wash-in F_A/F_I ... 1.03", while `read_wash_in` returns elimination for the same state. On `origin/main` on 2026-10-24, `format_wash_in_hover` in `app/chart_frame.py` still prints `format_wash_in_ratio(stretch.ratios[index])` with no wash-in test visible in the function. It was not re-run on `main`.

**Why it matters.** `docs/MODEL.md` § "F_A/F_I as a displayed ratio" and rule 2 of `app/wash_in.py` say a quotient above 1 is not a wash-in fraction. The crossing column is drawn only so the line meets the reference, and the hover turns it into a printed number that teaches a wash-in past completion, at the dot a reader is most likely to point at.

**Done when.** The behaviour is reproduced on `main`, and the hover either withholds the number for a column that `read_wash_in` classes as elimination or labels it as the reference crossing. A regression test hovers the terminus column.
