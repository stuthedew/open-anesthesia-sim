---
id: PL-H588
title: expert-review.md's src/** and tests/** also match subprojects/docket/, so the simulator's specialist standard loads on the apparatus
status: dropped
added: 2026-09-05
closed: 2026-09-05
reason: Overtaken by PL-WWDT, which removed the globs entirely. The project owner
  required the expert-review standard to reach a design round, so the file lost its
  `paths:` and is now resident; there is no `src/**` or `tests/**` left to reach
  `subprojects/docket/`. The risk this item named - the specialist standard applied
  to the apparatus - is now larger rather than smaller, since the file loads
  everywhere, and is held instead by the scope paragraph in its opening lines, which
  is the mitigation `PL-6SBB` prescribes. Its `docs/**` half is moot for the same
  reason. Reopen if that paragraph proves insufficient in practice.
---

**Problem.** `.claude/rules/expert-review.md` declares `paths: ["src/**",
"docs/**", "tests/**"]` and states its own scope in prose: "It loads when a
session reads the simulator, its tests, or its documentation, which is where
they apply." Its globs are wider than that sentence, in two separate ways.

- **At depth.** An unanchored glob in this harness matches the same name at
  any depth (measured; see the table below). `subprojects/docket/src/` and
  `subprojects/docket/tests/` both exist, so reading
  `subprojects/docket/src/docket/cli.py` loads the specialist standard onto
  the queue tool.
- **At the root, no depth needed.** `docs/**` matches `docs/worker.md`, which
  `.claude/rules/apparatus-standard.md` claims by name, and `docs/items/**`,
  the queue. This half is live regardless of how the matcher treats depth.

**Why it matters.** `CLAUDE.md` § "Two standards, deliberately unequal" splits
the tree so that the apparatus is held to "working reliably and staying
streamlined" and the simulator to the specialist standard, and it is explicit
that the split is the point: "Nothing in it reaches the simulator, and it is
kept out of this file so that it cannot." `PL-6SBB` is what the leak cost in
that direction — a session applied the apparatus bar to `src/`, correctly
quoting a sentence whose scope was three sentences away.

This is the same leak running the other way, and it is unguarded because only
one direction was fixed. A session on `subprojects/docket/` now loads both
rules at once: one says polish it to what a top-tier specialist would
recognize and "proactively surface important domain-specific concerns", the
other says "it is scaffolding, not product; nobody evaluating this project
will read it. Polishing it past sufficient is the most common way this project
wastes a session." `CLAUDE.md` resolves a tie ("where the two standards compete
for a session, the simulator wins") — which resolves it the wrong way here,
because on apparatus paths the simulator's standard is the one that should not
have loaded.

**Where.** `.claude/rules/expert-review.md` — the `paths:` list, and the scope
sentence in the opening paragraph.

**Approach.** Anchor the three globs to the repository root: `/src/**`,
`/tests/**`, `/docs/**`. Measured against this harness on 2026-09-05, with
probe rules and throwaway target files at both the root and
`subprojects/docket/`:

| `paths:` entry | root | `subprojects/docket/…` |
| --- | --- | --- |
| `"zzp.md"` (bare file) | fires | fires |
| `"/zzp.md"` | fires | does not fire |
| `"./zzp.md"` | does not fire | does not fire |
| `"zzdir/**"` (bare directory) | fires | fires |
| `"/zzdir/**"` | fires | does not fire |

The third row is the trap and the reason to copy a spelling rather than invent
one: `./` is the natural way to write "here" and it matches nothing at all, so
a rule spelled that way is silently never delivered.

Anchoring does not settle the `docs/**` half, which is a scope question rather
than a glob question: `docs/worker.md` is claimed by `apparatus-standard.md`
and matched by this rule, and `CLAUDE.md` names neither `docs/items/` nor
`docs/releases/` on either side of the split. Decide what `docs/**` is meant to
reach — most likely the documentation a reader of the simulator needs
(`docs/MODEL.md`, `docs/ARCHITECTURE.md`, `docs/references/`) rather than the
queue and the worker instructions — and enumerate it, rather than leaving a
directory glob to answer a question `CLAUDE.md` did not.

`PL-LLWN` is the class fix and the check; this item is the one instance that is
live today.

**Done when.** Reading a file under `subprojects/docket/` does not load
`expert-review.md`, reading `src/anesthesia_sim/` and `tests/` still does, and
the rule's `paths:` and its scope sentence describe the same set of files —
including an answer for which of `docs/` it means.
