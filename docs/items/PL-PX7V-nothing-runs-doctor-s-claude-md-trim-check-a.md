---
id: PL-PX7V
title: Nothing runs /doctor's CLAUDE.md trim check, a deterministic carrier this project's own tooling doctrine would prefer
priority: P3
effort: S
status: done
classes: session-cost, docs
touches: docs/items/
added: 2026-09-16
closed: 2026-09-16
pr: 631
verify: grep -qF 'Run, 2026-09-16, and it returned nothing' docs/items/PL-PX7V-nothing-runs-doctor-s-claude-md-trim-check-a.md
---

**Problem.** Claude Code v2.1.206 added a trim check to `/doctor`: it "proposes
trims for a checked-in CLAUDE.md: it cuts content Claude can derive from the
codebase, such as directory layouts, dependency lists, and architecture
overviews, and keeps pitfalls, rationale, and conventions that differ from tool
defaults" ([memory](https://code.claude.com/docs/en/memory)). The container runs
2.1.273, so it is available and has never been run here.

This is disposition 1 under `CLAUDE.md` § "A behavior change takes effect in the
session that asks for it" — a deterministic instrument answering a question
this project currently answers by hand, once per pass, at full context.

**What it does not settle.** Its heuristic is "derivable from the codebase",
which is not this project's test. `docs/resident-instructions.md` tests
*adherence* and routes by *when a rule fires*; almost nothing resident here is
derivable from the tree, so the trim check may return little. That is a result
worth having either way: a near-empty answer is evidence the resident set is
already at the floor its own standard allows, which is exactly the claim
`docs/resident-instructions.md` § "Reductions considered and refused" makes and
has never had an independent instrument agree with.

**Also unused.** The `InstructionsLoaded` hook logs which instruction files
loaded, when, and why. `tools/doc_check.py` infers the same set by reading
`paths:` frontmatter. The hook would confirm the inference against what the
harness actually did, which is the one part of `measure_resident` that is a
model of the harness rather than an observation of it.

**Do not run `/doctor` and act on it in the same pass.** Its proposals are
input to the routing test in `docs/resident-instructions.md`, not a verdict.

## Run, 2026-09-16, and it returned nothing to cut

**The result this item was filed to get.** Every checked-in instruction file
scanned against the trim check's own cut categories — directory and file
layouts, tech-stack and dependency lists, standard build/test/lint commands,
API signatures copied from source, architecture tours, generic best practices.
**Zero hits in all eleven files** (`CLAUDE.md` and the ten `.claude/rules/`
files). No file trips the large-memory warning floor either: `CLAUDE.md` is the
largest at 34,251 characters against a 40,000 floor.

That is the outcome this item predicted, and it is now measured rather than
asserted: `docs/resident-instructions.md` § "Reductions considered and refused"
is right that the resident set is at the floor its own standard allows.

**The one candidate, examined and rejected.** § "Architecture and development
discipline" holds eight invariants, and `tools/import_boundary_check.py` now
confines twelve packages that bear on three of them — `PySide6` and `pyqtgraph`
out of `core/` (the UI-independence rule), `time` and `datetime` out of `core/`
(the wall-clock rule), `random`, `secrets` and `uuid` out of `core/` (part of
the determinism rule) — with the 100% coverage gate carrying "add or update
tests with every core behavior change".

Retiring those bullets is nonetheless **wrong**, on this project's own test
(`PL-NJTZ`): a rule is retired when its failure mode is caught
deterministically, and an import check catches the *import*, not the coupling.
Wall-clock time handed into `core/` as a parameter, or a UI concept modelled
into a core dataclass, passes every boundary and violates both rules. The
ledger already names this shape — "a rule whose evidence has gone stale while
its other triggers have no carrier stays put" — and cutting only the caught
clause would be rewriting rather than routing.

Path-scoping that same section was separately considered and refused on the
record ("a trigger that usually fires is the wrong trade for eight lines"), so
neither disposition is open. The section stays whole.

**What did not get answered, and why.** `/doctor`'s other checks — install
health, unused skills and plugins, MCP servers, local-memory dedup, version
currency, permission posture, denied-command allowlisting — all read
machine-local state. This ran in an ephemeral cloud container: `numStartups` 0,
one transcript file (its own session), no user settings file, no local memory
files, no plugins, no user-scope MCP servers. Those checks describe the
container and transfer nothing. Only the CLAUDE.md checks read checked-in files
and therefore mean anything from here.

**So the standing answer for this project:** run `/doctor` from a local
checkout when the question is the machine, and expect the trim half to keep
returning nothing here until someone adds derivable content. The
`InstructionsLoaded` hook this item also named is still unused and still worth
having — it would confirm `measure_resident`'s `paths:`-frontmatter inference
against what the harness actually loaded — but it is a separate mechanism and
is not carried by this close-out.
