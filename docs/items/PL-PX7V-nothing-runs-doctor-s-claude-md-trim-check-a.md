---
id: PL-PX7V
title: Nothing runs /doctor's CLAUDE.md trim check, a deterministic carrier this project's own tooling doctrine would prefer
status: untriaged
added: 2026-09-16
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
