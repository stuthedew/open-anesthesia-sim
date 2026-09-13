---
id: PL-B667
title: MODEL.md's required invariants say derived fractions stay finite and nonnegative, but core/ enforces the upper bound of 1 in five places and the list never states it
priority: P2
effort: S
status: ready
classes: docs
feature: core-domain-language
touches: docs/MODEL.md
added: 2026-09-13
verify: python3 tools/doc_check.py check && grep -qF 'derived partial-pressure-equivalent fractions remain finite and within 0 through 1' docs/MODEL.md
---

**Problem.** MODEL.md's required invariants say derived fractions stay finite and nonnegative, but core/ enforces the upper bound of 1 in five places and the list never states it

`docs/MODEL.md` § "Required invariants" is the authoritative list of what the
implementation must preserve. Its line on concentrations reads:

> derived concentration fractions remain finite and nonnegative;

That is the lower bound and nothing else. The code enforces both bounds, in
five places:

| Where | Form |
| --- | --- |
| `core/validation.py` `require_concentration_fraction` | `not 0.0 <= value <= 1.0` raises |
| `AlveolarCompartment.__post_init__` | `agent_amount_l > gas_volume_l` raises |
| `VenousBloodCompartment.__post_init__` | `agent_amount_l > capacity_l` raises |
| `TissueGroup.__post_init__` | `agent_amount_l > capacity_l` raises |
| `BreathingCircuit.set_agent_amount` / `set_circuit_volume` | `> circuit_volume_l` raises |

The first is the load-bearing one. `AgentUptakeSystem._write_state` writes every
solved step back through the validated setters, so the upper bound is checked on
**every step's output**, and its docstring already states the reason in exactly
the terms this list should use: "an exact solution of the equations cannot leave
the physical range, so a value that does is evidence the run is no longer
trustworthy rather than a number to display."

**Why it matters.** This is not a wording nit. § "Concentrations"
does say fractions run "from 0 through 1", but that is a statement about
*representation* — what the number means — where this list is the statement of
what the implementation *must preserve*. A reader checking the code against the
spec finds a guard the spec does not ask for, which is the shape of a guard
somebody deletes as over-engineering. It is also the direction of divergence
that matters: the spec currently under-promises what the code guarantees, so
nothing in `make check` can catch the day the guarantee is dropped.

`PL-FZ6T` is about to build checks that hold `core/` to `docs/MODEL.md`, which
is the reason to settle this now rather than later.

**Proposed fix, and it is one line.** Change the invariant to name both bounds —
"derived partial-pressure-equivalent fractions remain finite and within 0 through
1" — and, if a second line is wanted, state that a step producing a value outside
it is refused and rolled back rather than displayed, which the "a simulation step
that cannot be completed" invariant below already half-says.

**What was checked and found adequate, so this item is not about it.** The
runtime enforcement itself needs nothing added. The three per-compartment closed
forms (`TissueGroup.advance`, `VenousBloodCompartment.advance`,
`BreathingCircuit.advance_fresh_gas`) write `agent_amount_l` directly rather than
through the guarded setter, but each computes a convex combination of two
in-range values, so the result is in range by construction. And the bound is not
close: the highest fraction any supported run reaches is the vaporizer dial
maximum, 0.18 for desflurane, so operating states sit about 5x below it. A test
sweeping the supported domain for a bound violation would be a check that cannot
fail, which `CLAUDE.md` says to retire rather than build.

**Done when.** `docs/MODEL.md` § "Required invariants" states both bounds on
the derived fraction, `make check` passes, and no other statement in the
document contradicts it. No code changes: the guarantee already holds, and this
item is the spec catching up to it.

**Where.** `docs/MODEL.md` § "Required invariants", one line.

**Work it with `PL-FZ6T`, on one branch** (project owner, 2026-09-13). `PL-FZ6T`
builds the checks that hold `core/` to `docs/MODEL.md`, and this invariant line
is what one of those checks would read - so writing the sentence and writing the
check that enforces it belong in the same pass. Alone this is a one-line docs
commit with nothing behind it, which is how a spec line comes to be wrong again.

Not a `blocked-by` edge, deliberately: neither item needs the other to start,
and declaring one would take this out of `bin/docket next` for the wrong reason.
It is a pairing note, and `PL-FZ6T`'s brief carries the matching one.

**Classed `docs`, and the two classes it is not are both deliberate.**

Not `defect`: the invariant line is not *wrong*, it is *incomplete*. "Derived
concentration fractions remain finite and nonnegative" is a true statement that
omits a second guarantee. That is `PL-212V`'s shape - a Symbols table with no
row for the stored coefficient - and `PL-212V` and `PL-H46J` are both classed
`docs` alone. `defect` in this queue marks a statement that is false, as in
`PL-KBJT`, whose citation named a function that does not exist. Following the
precedent matters beyond tidiness here: `defect` is one of the classes
`ROADMAP.md`'s debt gate reads, so mis-classing an omission as a defect makes
it debt, and Gate 1's disposition rule then owes it an answer it should never
have been asked. `tools/doc_check.py`'s check caught exactly that.

Not `safety`: the invariant it corrects *is* a safety invariant, but the reader
the current wording misleads is a developer auditing `core/` against the spec,
not a clinician reading a displayed value - and `docket check` pins `safety` to
P1, a band that has to keep meaning "a clinician could be misled".

**It is not Gate 1's, and needs no disposition there.** `feature:
core-domain-language` puts it in the `v0.4.x` track, "the code is the model",
with `PL-FZ6T` and `PL-9SH6`; `ROADMAP.md`'s row for that track records that it
"freezes no gate and takes no section of its own" (project owner, 2026-09-05).
