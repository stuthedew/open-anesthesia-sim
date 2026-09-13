---
id: PL-L7JB
title: docs/MODEL.md names the mass-balance tolerances MASS_BALANCE_ABSOLUTE_TOLERANCE and MASS_BALANCE_RELATIVE_TOLERANCE, but core/ calls them AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L and AGENT_ACCOUNTING_RELATIVE_TOLERANCE, so a reader grepping the documented name finds nothing
priority: P2
effort: S
status: done
classes: docs, defect
feature: core-domain-language
touches: docs/MODEL.md, src/anesthesia_sim/core/agent_simulation_validation.py, tests/unit/test_agent_simulation_validation.py
added: 2026-09-06
closed: 2026-09-13
verify: python3 tools/doc_check.py check && python3 -c "import re,pathlib; doc=pathlib.Path('docs/MODEL.md').read_text(); code=''.join(p.read_text() for d in ('src','tests') for p in pathlib.Path(d).rglob('*.py')); names=set(re.findall(r'(?:MASS_BALANCE|AGENT_ACCOUNTING)_[A-Z_]+', doc)); raise SystemExit(0 if names and all(n in code for n in names) else 1)"
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

**The `verify:` command specifies the outcome rather than the direction.** It
asserts that every `MASS_BALANCE_*` or `AGENT_ACCOUNTING_*` identifier
`docs/MODEL.md` names resolves somewhere in `src/` or `tests/`, which is the
property a reader greps for, and it holds whichever way the naming is settled.
Run 2026-09-06 before the work: it exits 1, naming `MASS_BALANCE_ABSOLUTE_TOLERANCE`
and `MASS_BALANCE_RELATIVE_TOLERANCE` as the two that resolve nowhere, while
`MASS_BALANCE_RELATIVE_GATE` and `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` both
resolve.


**Closed 2026-09-13, in the doc direction, and the direction was already
decided.** `PL-MS54` is the same defect filed earlier from the other end, and
its `verify:` command fixes the outcome — `docs/MODEL.md` must name
`AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` and must not name
`MASS_BALANCE_ABSOLUTE_TOLERANCE` — so the open question this brief left ("decide
which before editing") had been answered by an open item rather than being open.
Both are closed by the same edit and no code moved. `MINIMUM_RELATIVE_SCALE_L`
was added to the block on `PL-MS54`'s suggestion: the prose beneath already
described the 1e-15 L floor without naming it. `MASS_BALANCE_RELATIVE_GATE`
stays, being the real identifier in `tests/reference/test_multi_agent.py` and
`tests/reference/test_sevo_patient.py`.
