---
id: PL-1KTV
title: docket.toml counts .github as the workflow lane but apparatus-standard.md's paths do not, so 500 lines of workflow comments sit under the simulator's standard by default
status: untriaged
added: 2026-09-06
---

**Problem.** Two path lists in this repository answer two different questions
about `.github/`, and they disagree.

- `docket.toml`'s `workflow_paths` lists `.github`, so an item touching a
  workflow file is ranked in the **workflow lane** by `bin/docket next`.
- `.claude/rules/apparatus-standard.md`'s `paths:` frontmatter lists
  `/subprojects/docket/**`, `/tools/**`, `/.claude/**` and `/docs/worker.md` —
  **not** `.github`. `CLAUDE.md`'s own naming of the apparatus half agrees with
  the rule file and not with `docket.toml`.

So a session that opens `.github/workflows/quality.yml` (269 lines, nearly all
comment) or `pr-title.yml` gets neither the apparatus bar nor any statement
that the simulator's specialist bar is the one that applies. It falls through
to the resident default, which is the specialist standard.

**Why it matters.** `CLAUDE.md` is explicit that the split is load-bearing and
that mis-scoping it has already cost something: `PL-6SBB` records a session
applying the apparatus bar to `src/` from a sentence whose scope sat three
sentences away. This is the mirror gap — a part of the tree the lane logic
treats as apparatus, and the review-standard logic does not place at all. It is
the *safe* direction to be wrong in (the higher bar wins by default, so nothing
under-invests), which is why this is a consistency question rather than a
defect, and why it was captured rather than fixed.

**Not the same finding as `PL-WGXJ`.** That item argues the apparatus is
structurally exempt from the expert-review standard and so has no review bar at
all — a question about what the apparatus bar *says*. This is a question about
which paths it *covers*, and the two answers are independent: `PL-WGXJ` could
be resolved either way and `.github` would still be missing from the list.

**The decision this needs.** Whether `.github/` is apparatus:

- **If yes**, add `/.github/**` to `apparatus-standard.md`'s `paths:` and to
  `CLAUDE.md`'s naming of the apparatus half, so all three lists agree.
  `tools/rules_paths_check.py` already holds every `paths:` entry to a leading
  `/` and to resolving against the tree, so the addition is checked.
- **If no**, `docket.toml`'s `workflow_paths` is the outlier and the lane
  boundary is wider than the standard boundary on purpose — which is
  defensible, since a lane is about who can hold a change and a standard is
  about how good it has to be. Then say so in one sentence where the next
  session will read it, because the two lists looking like the same list is the
  trap.

Note that these two lists cannot simply be merged even if the answer is "yes":
`workflow_paths` also carries `Makefile`, `docket.toml`, `docs/items` and three
named test files, which are lane facts and not standard facts.

**Where.** `docket.toml`'s `workflow_paths`;
`.claude/rules/apparatus-standard.md`'s `paths:` frontmatter; `CLAUDE.md`
§ "Proactive expert review and domain best practices", the paragraph naming the
two path sets.

**Found.** While working `PL-KPP1` in `.github/workflows/pr-title.yml` and
checking which standard governed the comment being written.

**Done when.** The three lists agree about `.github/`, or the one that
deliberately differs says in a sentence why.
