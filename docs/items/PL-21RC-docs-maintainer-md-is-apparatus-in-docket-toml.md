---
id: PL-21RC
title: docs/maintainer.md is apparatus in docket.toml's workflow_paths but is named in none of the three places that list the apparatus set, and apparatus-standard.md's paths: glob does not load for it
status: untriaged
added: 2026-09-13
---

**Problem.** docs/maintainer.md is apparatus in docket.toml's workflow_paths but is named in none of the three places that list the apparatus set, and apparatus-standard.md's paths: glob does not load for it

**Why it matters.** Four places state which half of the tree a file belongs to,
and after `PL-GVNS` they disagree about one file:

| Where | What it names | `docs/maintainer.md` |
| --- | --- | --- |
| `docket.toml` `workflow_paths` | which lane `bin/docket next` offers an item to | present (`PL-GVNS`) |
| `CLAUDE.md:437` | which of the two standards applies | absent |
| `.claude/rules/expert-review.md:13` | the same list, restated for its own scope note | absent |
| `.claude/rules/apparatus-standard.md` `paths:` | when the lower bar actually **loads** | absent |

The fourth is the one with teeth. `apparatus-standard.md` is path-scoped, so it
loads when a session opens a matching file — and its glob list carries
`/docs/worker.md` and not its counterpart. A session editing the project owner's
own notes therefore gets no apparatus rule at all, and falls through to the
specialist standard `CLAUDE.md` reserves for the simulator. That is the same
shape as `PL-6SBB` with the sign reversed: there a session applied the apparatus
bar to `src/`; here it would apply the simulator's bar to a file that is not the
simulator's.

`docket.toml`'s own comment says `workflow_paths` is "the boundary `CLAUDE.md`'s
two standards, deliberately unequal already draws, written down so `docket next
workflow` and `docket next product` can act on it" — so the two are not
independent lists that may differ, they are one boundary written twice, and they
now differ.

**Where.** `CLAUDE.md:437`; `.claude/rules/expert-review.md:13`;
`.claude/rules/apparatus-standard.md`'s `paths:` frontmatter.

**One thing to settle rather than assume.** Whether the answer is to add the
file to all three, or to stop restating the list in prose at all. `docket.toml`
already holds it in machine-readable form and `tools/workflow_paths_check.py`
already holds *part* of it to the tree; two prose copies of a list that a config
file states exactly is the shape that drifted here in the first place, and the
same shape `docs/worker.md` refused for `gate_paths` ("Nothing here restates it,
because two copies of a prohibition are two chances for them to disagree"). A
check that holds the `paths:` glob list against `workflow_paths` is the
deterministic version and is the one worth costing.

**Found.** Closing `PL-GVNS` (2026-09-13), by the close-out documentation sweep
rather than by the work. Not fixed there: all three files are outside
`PL-GVNS`'s `touches`, two of them are resident instructions, and whether to
restate or to delete is a decision rather than a typo.

**Done when.** The four statements of the apparatus boundary agree about
`docs/maintainer.md`, and a session opening it loads
`.claude/rules/apparatus-standard.md`.
