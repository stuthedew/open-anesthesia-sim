---
id: PL-1KTV
title: docket.toml counts .github as the workflow lane but apparatus-standard.md's paths do not, so 500 lines of workflow comments sit under the simulator's standard by default
priority: P3
effort: S
status: done
classes: docs
feature: worker-instructions
touches: docket.toml, .claude/rules/apparatus-standard.md, CLAUDE.md
added: 2026-09-06
closed: 2026-09-13
pr: 515
verify: python3 tools/rules_paths_check.py && grep -qF '/.github/**' .claude/rules/apparatus-standard.md
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

**Decision needed.** Whether `.github/` is apparatus:

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

**Decided 2026-09-13: yes, `.github/` is apparatus.** All the lists now agree
rather than one of them documenting an exception.

The question the brief poses is which way to resolve the disagreement, and the
answer follows from what the two halves are *for*. `CLAUDE.md` defines the
apparatus as what "exists so agent sessions can be productive". A CI workflow
is that and nothing else: `quality.yml` and `pr-title.yml` run the checks a
session runs, and no reader of the simulator ever opens them. Nothing in
`.github/` is `src/`, `tests/`, `docs/MODEL.md` or `README.md`, which is the
simulator half stated by enumeration. Declaring the lane boundary
deliberately wider than the standard boundary was the alternative, and it
would have meant writing a sentence explaining why two lists that look alike
are not - a standing cost against a one-line addition.

**The brief named two lists and there are three.**
`.claude/rules/expert-review.md` carries its own copy of the apparatus
enumeration, added when that file was made resident, and it was missing
`.github` too. Fixing only the two the brief names would have left the
disagreement intact in the file a session reads *while choosing an approach*,
which is the moment the standard actually gets applied. All three now read
`subprojects/docket/`, `tools/`, `.claude/`, `.github/`, `docs/worker.md`.

The addition is checked rather than asserted: `tools/rules_paths_check.py`
holds every `paths:` entry to a leading `/` and to resolving against the
tree, and now reports 14 globs where it reported 13.

**`docket.toml`'s `workflow_paths` is untouched**, as the brief requires: it
also carries `Makefile`, `docket.toml`, `docs/items` and three named test
files, which are lane facts rather than standard facts. The two lists agree
about `.github/` now and are still not the same list, which is the
distinction worth keeping.

`PL-WGXJ` is unaffected and remains open. It asks what the apparatus bar
*says*; this asked which paths it *covers*, and the brief was right that the
two are independent.
