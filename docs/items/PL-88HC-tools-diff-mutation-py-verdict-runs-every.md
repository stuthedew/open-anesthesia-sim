---
id: PL-88HC
title: tools/diff_mutation.py --verdict runs every mutant of each changed function although only mutants on changed lines can refuse, so verify --self spent 36 minutes on PL-2TZT's 340-mutant batch; select the mutants of changed lines before mutmut runs
status: untriaged
added: 2026-10-24
---

**Problem.** tools/diff_mutation.py --verdict runs every mutant of each changed function although only mutants on changed lines can refuse, so verify --self spent 36 minutes on PL-2TZT's 340-mutant batch; select the mutants of changed lines before mutmut runs

**Found 2026-10-24 while building `PL-CZXN`.** `verdict` in `tools/diff_mutation.py` counts only mutants on a line the branch changed, but `run` asks mutmut for every mutant of each changed function. `#1676`'s batch changed 16 functions holding 340 mutants and took 2,190 s on four cores, while another session's tests shared them. Only three of its six survivors were on changed lines. Choosing the mutants of changed lines before the run would need each mutant's line before mutmut runs it, which `mutmut show` gives one subprocess at a time and the generated `mutants/` files give all at once. The fixed cost, about five minutes of coverage collection, would remain.
