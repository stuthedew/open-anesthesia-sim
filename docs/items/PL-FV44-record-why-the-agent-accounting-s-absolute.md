---
id: PL-FV44
title: Record why the agent accounting's absolute tolerance is 1e-12 L, which no item, comment or commit message states
priority: P1
effort: S
status: done
classes: defect, safety
feature: floating-point-domain
touches: src/anesthesia_sim/core/rounding.py, docs/VERIFICATION.md
deferred-from: v0.7.0 - continues PL-GJ1W (every rounding bound stated in one place), a frozen entry this gate deferred, and is worked with it. Hazard not live, checked 2026-11-22 at d4e8200c: the 1 picolitre limit governs only while a run has handled less than a millilitre of agent gas, and the largest unaccounted amount in the 3600 s runs (1.1e-12 L) passed on the relative limit, so no displayed value depends on the missing reason
added: 2026-11-21
closed: 2026-11-22
pr: 2221
payoff: The limit that decides when a step is refused for unaccounted agent has a stated reason, so a later change to it can be judged against that reason rather than guessed at.
verify: grep -qF 'so the fixed limit can only admit an error, never' docs/VERIFICATION.md
---

**Problem.** `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` in `src/anesthesia_sim/core/rounding.py` is `1e-12` L, and no record says why. The value is already in commit `875ba0850` ("Build v0.1.0 sevo patient simulation", 2026-08-22), which `git log -S'1e-12' --reverse -- src` lists first. Its docstring cited the largest unaccounted amount in a 3600 s run as if that explained it, but the measurement was made on 2026-09-06, after the value was chosen.

**Why it matters.** The tolerance decides when a step is refused for unaccounted agent. `.claude/rules/sources-and-docstrings.md` asks that the reason for a chosen value come from a record, and that an item be filed where the trace finds none.

**What it changes.** Derive the limit from the rounding of the arithmetic it bounds, as `PL-GJ1W` (each comparison picks its own tolerance) does for the relative limit, or state in the docstring that it is a chosen floor and what it was checked against. `docs/VERIFICATION.md` § "Selected method (as implemented)" gives 1.1e-12 L as the largest unaccounted amount in the 3600 s runs of 2026-11-21, which passed on the relative limit.

**Found in.** `PL-MH9J`'s rewording of the code's prose, 2026-11-21.

**Done when.** The docstring gives a reason that a record or a derivation holds.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n -A8 'AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L: Final' src/anesthesia_sim/core/rounding.py`
printed the value `1e-12` and a docstring that says what the limit does and
what the 3600 s runs measured, and gives no reason for the value. The constant
was already `1e-12`, in `core/agent_simulation_validation.py`, at the Gate 3
freeze (`0947408`).

**Generator check.** The fact is how far a computed amount can be from the
exact one, and so what a limit on it proves. `PL-GJ1W` (every rounding bound
in one place) states it and is still open, so this is one more instance under
that head and not a re-entry.

**Done 2026-11-22.** `git log -S'1e-12' -- src` found no reason for the value,
so the docstring now says it is a fixed allowance from v0.1.0 with no recorded
reason, gives the one derivation that holds (it equals the relative limit
applied to 1 mL, so it decides only while less than 1 mL has been handled), and
names what it was checked against. `docs/VERIFICATION.md` § "Selected method
(as implemented)" said the fixed limit "catches a gross error early". A step
passes on either limit, so the fixed limit can only admit an error, and that
sentence is corrected. Files checked: `docs/VERIFICATION.md`, `docs/MODEL.md`,
`docs/INTERFACE.md`, `docs/PARAMETERS.md`, `docs/ARCHITECTURE.md` and
`README.md`, searched for "picolitre", "absolute limit" and "fixed limit".

**Blind review, 2026-11-22.** Both passes named one finding: the first draft
said the limit lets a run pass while too little agent has been handled for the
relative limit to admit its rounding. A run of each shipped agent's default
system for 300 s (`AgentUptakeSystem.for_agent`, reading `relative_error` at
each step) gave a largest relative residual of 3.8e-14 for sevoflurane, 4.0e-14
for isoflurane and 2.4e-14 for desflurane, and each had handled 1 mL by step 1
or 2. So no recorded run needs the absolute limit, and the docstring now says
that instead.
