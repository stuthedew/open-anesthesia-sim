---
id: PL-L7JB
title: docs/MODEL.md names the mass-balance tolerances MASS_BALANCE_ABSOLUTE_TOLERANCE and MASS_BALANCE_RELATIVE_TOLERANCE, but core/ calls them AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L and AGENT_ACCOUNTING_RELATIVE_TOLERANCE, so a reader grepping the documented name finds nothing
status: untriaged
added: 2026-09-06
---

**Problem.** `docs/MODEL.md` § "Mass-balance identity" states the run-time halt
thresholds in a `text` block as `MASS_BALANCE_ABSOLUTE_TOLERANCE = 1e-12 L` and
`MASS_BALANCE_RELATIVE_TOLERANCE = 1e-9`, immediately after saying "as
implemented in `core/agent_simulation_validation.py`". The constants in that
module are `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` and
`AGENT_ACCOUNTING_RELATIVE_TOLERANCE`. Neither documented name exists anywhere
in the tree.

**Why it matters.** The values agree, so nothing is numerically wrong today.
What is wrong is traceability, which `CLAUDE.md`'s safety-critical standard
asks for by name: a reader checking whether the shipped tolerance is the
documented one greps the documented identifier and gets no hits, and the two
names can drift apart silently because nothing ties them. It also cost this
session a re-read to establish that the doc block and the code were the same
two constants under different names.

**Noticed while closing `PL-4GN8`,** which added a third name to the same
section - `MASS_BALANCE_RELATIVE_GATE`, in `tests/reference/mass_balance_gate.py`.
That one is written to match its constant exactly, which is what makes the
older two visibly the odd ones out.

**Where.** `docs/MODEL.md` § "Mass-balance identity", the `text` block after
"The run-time halt thresholds"; `src/anesthesia_sim/core/agent_simulation_validation.py`.

**Done when.** The documented identifiers and the code identifiers are the
same strings, whichever way that is settled - renaming the doc's block is the
cheap direction and touches no code, renaming the constants is the direction
that makes `docs/MODEL.md` read as the specification it is. Decide which before
editing; `tests/unit/test_agent_simulation_validation.py` restates both
constants and would follow either.
