---
id: PL-WWDT
title: The expert-review standard is path-scoped, so it does not load when the approach is being decided - the design round it matters most in
priority: P2
effort: S
status: done
classes: defect, docs
feature: worker-instructions
milestone: v0.4.0
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/sources-and-docstrings.md, docs/resident-instructions.md
added: 2026-09-05
closed: 2026-09-05
pr: 350
verify: python3 tools/doc_check.py check && ! grep -q '^paths:' .claude/rules/expert-review.md && grep -qF 'sources-and-docstrings.md' CLAUDE.md
---

**Problem.** `.claude/rules/expert-review.md` carries the fields this project's
review reaches across and the design principles that follow from them, behind
`paths: ["src/**", "docs/**", "tests/**"]`. A path-scoped rule fires when a
session **reads** a matching file. A design round — the project owner
describing a feature and asking which approach to take — is a reply, and a
reply is not preceded by a read. So in the exchange where the approach is
actually chosen, the file that says what to judge an approach against may never
load at all.

It loads there today only by accident: `docs/**` matches `docs/items/**`, so
reading an item file pulls it in. That is incidental rather than designed, it
fires on queue work that has nothing to do with the simulator, and it stops the
moment a design round happens without an item being opened.

**Why it matters.** The project owner named this directly (2026-09-05): "I
absolutely want expert standard to apply in design round as well. That's
equally if not more critical because I'm relying on you to help me decide on
best approach to implementation of my ideas for features."

That is the higher-consequence half. `CLAUDE.md` § "Proactive expert review"
already ranks "irreversible architectural problems" above code style, and an
approach chosen without the human-factors, clinical-visualisation, validation
or medical-education lens is exactly that: the cost lands later and cannot be
refactored away. Code review catches a defect after it is written and cheaply;
a design round is the only moment the alternative is still free.

`docs/resident-instructions.md` already states the governing constraint in its
own words — a path-scoped rule "cannot carry a rule that must fire before a
first write, or before any file is opened at all. Most of what is resident here
is of exactly that shape: it governs how a session **receives a request,
decides an approach, or writes a reply**". Its "What stays resident" section
then has a group for receiving a request and a group for writing a reply, and
**none for deciding an approach** — which is the one this file governs. The
routing pass (`PL-JK0M`) simply did not have a group to put it in.

The same section's refusals point the same way: path-scoping the architecture
invariants was refused because "in practice it would fire — almost every
session touching the simulator reads a matching file first. *'Almost' is the
objection*." The expert-review trigger is weaker than that in a design round,
not stronger.

**Where.** `.claude/rules/expert-review.md`; `CLAUDE.md` § "Proactive expert
review and domain best practices", its closing pointer sentence;
`docs/resident-instructions.md`, which needs the new group recorded.

**Approach.** Split the file by *moment*, not by tree, which is the question
`CLAUDE.md`'s four dispositions are answered against.

- The intro, the field list and the design principles govern deciding an
  approach, which no read precedes. They lose `paths:` and become resident
  (~3.1 KB, taking the resident total from 38845 to about 41900).
- "A reference implementation is not a source" and "What a docstring and an
  error message owe a reader" fire with a file open, and stay path-scoped in
  a rule of their own, with anchored globs.

The resident half must carry its own scope in its opening lines rather than
three sentences away. `PL-6SBB` is the precedent: the apparatus standard was
resident, a session applied it to `src/`, and it quoted the right file. Making
the specialist standard resident creates the mirror hazard — over-investing in
the apparatus, which `CLAUDE.md` calls the most common way this project wastes
a session — unless the file says on sight which tree it governs.

Not duplication: the list moves rather than being copied. `CLAUDE.md`'s closing
pointer becomes a statement that the rule is resident and why, so two documents
never state the field list at once.

**Alternative considered and refused.** Leaving the list path-scoped and adding
a resident directive to read it when an approach is being decided. Cheaper by
about 2.9 KB, and rejected on the same ground `docs/resident-instructions.md`
rejects a skill for `instruction-writing.md`: it is "invoked when the model
judges it relevant, which is the same recognition act the rules already
require, with a load failure added". The owner said "absolutely", which asks
for delivery rather than likelihood.

**Done when.** A session that has opened no file in `src/`, `tests/` or `docs/`
still has the field list and the design principles when it proposes an
approach; the resident half names the tree it governs in its opening lines; the
code-and-provenance half still loads only on the paths it applies to; and
`docs/resident-instructions.md` records the new group and the measured cost.
