---
id: PL-HNWX
title: SUPPORTED_SCHEMA_VERSION is one global constant across agents, patients and machines, so a machine-only schema bump drags three agent files and the patient file with it
priority: P2
effort: M
status: ready
classes: refactor
feature: machine-profile-framework
touches: src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py, docs/MODEL.md
added: 2026-09-20
payoff: a machine-only schema change stops forcing edits to three agent files and the patient file that the change has nothing to do with
verify: grep -q 'def test_a_machine_only_schema_bump_leaves_the_agent_files_loading' tests/unit/test_parameters.py
---

**Problem.** SUPPORTED_SCHEMA_VERSION is one global constant across agents, patients and machines, so a machine-only schema bump drags three agent files and the patient file with it

**Why it matters.** Migration headroom is exactly zero, in both directions, and
nothing in the tree says so.

**Verified against the source, 2026-09-20.** All six sites the audit names are
real and read as it describes:

- `src/anesthesia_sim/core/parameters.py:38` - `SUPPORTED_SCHEMA_VERSION = 2`,
  one module-level integer with no per-file or per-payload qualifier.
- `:285-293` - `_validate_schema_version`. **The audit's claim that the check is
  exact equality is TRUE**, and the line is `:289`, verbatim
  `if value != SUPPORTED_SCHEMA_VERSION:`, raising
  `f"unsupported schema_version: {value}; expected {SUPPORTED_SCHEMA_VERSION}"`
  at `:290-292`. There is no range, no lower bound, and no per-payload branch.
- `:351` - `SchemaVersion = Annotated[int, BeforeValidator(
  _validate_schema_version)]`, the single alias all three payloads use.
- `:526` (`_AgentPayload`), `:578` (`_ReferenceAdultPayload`) and `:651`
  (`_BreathingCircuitPayload`) each declare `schema_version: SchemaVersion`.
  One number, one equality test, three unrelated families of data file.

Two consequences follow, and the second is the one that will bite:

1. **A machine-only bump drags every other file with it.** Raising the constant
   to 3 for a machine schema change makes `sevoflurane.json`,
   `isoflurane.json`, `desflurane.json` and `reference_adult.json` all fail to
   load until each is edited - four files whose contents the change had nothing
   to do with, each one a cited, safety-critical data file whose diff a reviewer
   then has to read for no reason.
2. **There is no way to load a v2 profile in a v3 world.** Exact equality means
   a version is a single admissible value rather than a window, so an older
   profile is not "older", it is unloadable. Before a first bump that is
   invisible; after one it is the whole cost of the bump.

**Evidence the distinction between the families is already live.** `PL-1JDD`
(make the source tier machine-readable) bumped all four data files to 2 in one
move, to make `tier` required - a change that genuinely touched every family.
`PL-8PS6` (fresh gas flow range is a machine property) then added
`deliverable_fresh_gas_flow_range` to the machine payload alone
(`core/parameters.py:656`) as an **optional** field with no bump at all. That is
a machine-only schema change that avoided a version bump, and the shipped
profile is still at `schema_version: 2`. The optional-field route works for an
addition and does not work for a rename, a changed meaning, or a newly required
key - which is precisely the class of change the audit identifies as growing
with each machine file.

**The design already assumes this is fixable.** `docs/machine-abstraction.md:393`
lists "declares a `schema_version` the loader does not know" among the
conditions under which a profile is refused. Today "does not know" evaluates to
"is not exactly 2", for every data file in the project at once.

**Done when.**

- Each payload family declares its own supported schema version - a class
  attribute on the payload model, or a named constant per family - rather than
  sharing one module-level integer.
- The check accepts a declared **range** rather than exact equality, so a
  version below the current one can be admitted deliberately instead of
  refused by construction.
- The refusal message names which family refused and what it accepts, so a
  reader of the error can tell a machine-schema problem from an agent-schema
  one.
- A test in `tests/unit/test_parameters.py` named
  `test_a_machine_only_schema_bump_leaves_the_agent_files_loading` holds the
  property directly: with the machine family's accepted versions widened, a
  machine profile at the newer version loads while the three agent files and
  the patient file, unchanged and still declaring 2, keep loading.
- `docs/MODEL.md:2398-2399`, which records the 2026-09-07 move to
  `schema_version` 2 as a single event across "data files", says that the
  version is now per-payload-family.
- No shipped data file's `schema_version` changes in this item.

**The one design point a session should decide rather than ask about.**
Accepting a range only helps if an older file still validates against the newer
model, which means fields added after the lower bound must be optional, or the
payload must fill them. Recommendation: accept
`minimum_supported..current_supported` per family, with the minimum set to the
current version on the day this lands - so the window is width one and nothing
changes behaviour - and widen it deliberately at the first real bump, which is
where the decision about that specific field's optionality can actually be
made. Building a general upcasting layer now would be guessing at a migration
nobody has needed yet.

**Explicitly not in scope.** No bump of any data file. No migration or
upcasting of an older payload into a newer one - accepting a range is not the
same as translating between versions, and the translation is the expensive half
that should wait for a change that needs it. No loosening of
`extra="forbid"`. No change to `tier`, `adopted` or `provenance_gap`.

**What would falsify this.** That the families are ever bumped separately. The
counter-case is `PL-1JDD` itself: it moved all four files together, and if that
is how every schema change is going to go, one constant costs nothing and
splitting it is ceremony. The evidence against that reading is `PL-8PS6` - a
machine-only change that took the optional-field route, which is the cheaper
route precisely because the bump was not affordable. If the project instead
decides as policy that all data files move in lockstep by version, this item
should be dropped rather than built, and that decision recorded where the
constant is defined.
