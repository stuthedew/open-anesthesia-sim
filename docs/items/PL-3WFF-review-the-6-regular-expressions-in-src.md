---
id: PL-3WFF
title: Review the 6 regular expressions in src/anesthesia_sim/ that tools/regex_baseline.py lets stand without a reason, and replace each one a parser or string method does better or write its reason beside it
status: untriaged
feature: regex-review
added: 2026-11-03
---

**Problem.** Review the 6 regular expressions in src/anesthesia_sim/ that tools/regex_baseline.py lets stand without a reason, and replace each one a parser or string method does better or write its reason beside it

`PL-7JYV` stops a session before it writes a regular expression with no
written reason, and lets the calls the tree already held stand in
`tools/regex_baseline.py`. Six of those are under `src/`, one module-level
`re.compile` in each of these files:

- `src/anesthesia_sim/app/agent_cost.py`
- `src/anesthesia_sim/app/currency_code.py`
- `src/anesthesia_sim/app/preferences.py`
- `src/anesthesia_sim/app/view_registry.py`
- `src/anesthesia_sim/layout/run_identity.py`
- `src/anesthesia_sim/layout/tree.py`

**Why it matters.** These are the simulator's own, held to the specialist
standard, and a pattern that reads a format it does not parse holds only until
the first case it was not written for. None of the six had a recorded reason.

**Approach.** For each pattern, ask the questions `tools/regex_check.py`'s
`GUIDANCE` prints: what it must recognise, whether a module or the standard
library already reads that format, and whether a string method does it. Then
replace it, with a test of text it must accept and text it must refuse, or keep
it with a `# regex:` comment giving the reason. Either way, lower or delete its
entry in `tools/regex_baseline.py` in the same commit.

**Done when.** No entry under `src/` is left in `tools/regex_baseline.py`.
