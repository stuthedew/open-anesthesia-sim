---
id: PL-ZQ35
title: The README freeze's path glob does not say whether it reaches subprojects/docket/README.md
priority: P2
effort: S
status: done
classes: defect, docs
feature: project-introduction
touches: .claude/rules/readme-hold.md
added: 2026-09-05
closed: 2026-09-05
pr: 350
verify: python3 tools/doc_check.py check && grep -qF 'subprojects/docket/README.md' .claude/rules/readme-hold.md && grep -qF '"/README.md"' .claude/rules/readme-hold.md
---

**Problem.** `.claude/rules/readme-hold.md` (`PL-QTN6`) declares
`paths: ["README.md"]`. The repository holds three files by that name:

- `README.md`, the project's front door, which is what the freeze is about —
  its prose names `PL-RM83` (decide what `README.md` is for) and `PL-N092`
  (rewrite it as a human-readable introduction), and `PL-QTN6`'s `touches`
  lists only the root path.
- `subprojects/docket/README.md`, the queue tool's format and command
  reference, which `CLAUDE.md` routes every session to for the item format.
- `docs/references/README.md`, the reference-library index. Found while
  fixing this item; the brief above was written naming only the first two.

A bare `README.md` glob is ambiguous about whether it matches at depth, so it
is unclear whether opening the docket reference loads a freeze written about a
different document with a different purpose and a different owner decision
behind it.

**Why it matters.** It fails in both directions and both are silent. If the
glob matches at depth, a session editing the docket reference — apparatus work,
which `CLAUDE.md` holds to "working reliably and staying streamlined" rather
than to the front door's single voice — is told to stop by a rule whose stated
reason does not apply to it, and the honest response to a rule that does not
fit is to reason around it, which is how a freeze that *should* bind gets
reasoned around next. If it does not match, that is correct today but rests on
a matcher detail nobody wrote down, so it can change under a harness update
without anyone noticing.

Observed 2026-09-05 while closing `PL-ZBRB`: that item documented its new
advisory in `subprojects/docket/README.md`, and settling whether the freeze
applied took reading `PL-QTN6`'s brief and `touches` rather than the rule.
The rule is the thing that loads; the item is not.

**Where.** `.claude/rules/readme-hold.md` — the `paths:` list and one
sentence of scope.

**Approach.** Anchor the glob to the file the freeze means (`/README.md`, or
whatever this harness's matcher spells the repository root), and say in one
line that the docket subproject's own README is not covered and why. Both
halves matter: the glob decides what loads, the sentence decides what a reader
does when it loads on the wrong file.

Worth checking the same question against the other rules in `.claude/rules/`
while there — `expert-review.md`, `core-domain.md` and `apparatus-standard.md`
all carry `paths:` and none has been tested against a name that repeats in the
tree.

**Done when.** The freeze's `paths:` matches the root `README.md` and not
`subprojects/docket/README.md`, and the rule says which of the two it governs
without a reader having to open `PL-QTN6` to find out. It is deleted whole when
the owner lifts the freeze, so this must not make it harder to delete.
