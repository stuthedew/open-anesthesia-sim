---
id: PL-GL5X
title: Load Factory Preferences needs shipped defaults to be a restorable artifact, but today's display defaults are Final constants in app/formatting.py with no factory state to return to
priority: P2
effort: M
status: blocked
classes: feature
blocked-by: PL-SSQW
feature: preferences-store
touches: src/anesthesia_sim/data/, tests/unit
added: 2026-09-16
---

**Problem.** Load Factory Preferences needs shipped defaults to be a restorable artifact, but today's display defaults are Final constants in app/formatting.py with no factory state to return to

**What Blender's fourth menu entry needs.** "Load Factory Preferences"
restores a known factory state. Today this project's display defaults are
`Final` constants in `app/formatting.py` — `AGENT_VOLUME_DISPLAY_DECIMALS`,
`FLOW_DISPLAY_DECIMALS` and the rest — so there is no artifact to restore
*from*; a factory reset would have to reach into module state and re-derive
what the code already hardcodes.

**The pattern already exists in this repository.** `PL-KXTL` ships the three
default Workspaces "as validated versioned JSON beside the other shipped
parameter files" under `src/anesthesia_sim/data/`, loading "through the same
path a learner's own Workspaces do". Shipped default *preferences* want
exactly that treatment, and for the same reason: a default that loads by the
reader's own path is a default whose behaviour is tested by the reader's own
tests.

**The constraint that keeps it honest.** `CLAUDE.md` requires agent/model
parameters in validated, versioned data files and no executable equations in
data files, so a preference whose value is *derived* — display precision, per
`PL-0S0V` — stays a derivation in code with the data file carrying only what
the derivation is fed. The line is the same one `tools/doc_check.py` sits on:
the file states the inputs, the code states the rule.

**Why it matters, and what is uniquely this item's.** Most of the surrounding
ground is already owed elsewhere, and this item is worth keeping only for the
part that is not. `ROADMAP.md` v0.6.0 `Required scope` item 11 already obliges
`PL-WV9K` to distinguish shipped defaults from the learner's own and to define
"reset", and `PL-KXTL` already ships defaults through the reader's own load
path. Three mechanisms nobody owns, all of them on the preferences side:

1. **Reset is replace, not merge.** A reset that restores only the keys present
   in the shipped artifact leaves reader-set keys standing underneath a label
   saying the application is factory-fresh — `CLAUDE.md`'s stale-state failure
   verbatim, and the more likely implementation of the two.
2. **Every settable key has a factory value, checked.** Decidable by reading the
   settable set against the shipped artifact, recurring, and deterministic — so
   a `make check` script under `tools/` rather than a rule anyone has to
   remember, on `CLAUDE.md`'s deterministic-tooling standing approval. Without
   it, a key added later has no factory value and a reset silently leaves it
   alone.
3. **A scope-limited reset says what it did not reset.** This is the price of
   the two-scope architecture `PL-MQHN` settled: Load Factory Preferences
   deliberately leaves Workspaces standing, so the reader is left in a state
   they will read as fully reset when it is not. `docs/interface-provenance.md`
   records that Blender has no mode-awareness doctrine to borrow, so this one is
   ours to design.

The factory artifact also needs its own `schema_version`, on the same terms as
every other shipped data file.

**Blocked on `PL-SSQW`**, which decides the file location, the atomic write and
the older/newer/invalid schema policy for the Workspace file. A preferences
section inherits all three or deliberately diverges from them, and either way it
cannot be settled first. `PL-MQHN` settled the store question it depended on:
one file, two sections, two reset operations.

**Done when.** Shipped default preferences exist as a validated, versioned
artifact under `src/anesthesia_sim/data/` carrying its own `schema_version` and
loading through the reader's own path; reset replaces rather than merges, under
test; a `tools/` check run by `make check` fails when a settable key has no
factory value; and a scope-limited reset names what it left standing.
