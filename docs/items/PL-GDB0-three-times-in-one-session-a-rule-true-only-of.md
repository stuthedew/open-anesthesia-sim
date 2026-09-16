---
id: PL-GDB0
title: Three times in one session a rule true only of the currently implemented model or mechanism was written into ROADMAP.md or docs/MODEL.md as a permanent rule about the project, each needing its own correction commit
priority: P2
effort: S
status: done
classes: docs, infra
touches: .claude/rules/expert-review.md, docs/resident-instructions.md
added: 2026-09-16
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF 'Say what would falsify it' .claude/rules/expert-review.md
---

**Problem.** Three times in one session a rule true only of the currently implemented model or mechanism was written into ROADMAP.md or docs/MODEL.md as a permanent rule about the project, each needing its own correction commit

**The three instances, all on 2026-09-15/16, all in one session.**

| Written | The rule as recorded | Why it was wrong | Corrected by |
| --- | --- | --- | --- |
| `ROADMAP.md` item 34 | Floating panels "are a different mechanism and **are not admitted**" | The owner had asked for tiled-first with floating open later. A never in `ROADMAP.md` is what a later session cites to refuse a feature. | `PL-T86Q` |
| `PL-WLWY` brief | The minimum display belongs in "a persistent strip" | Proposed before counting what it must carry: ~20 obligations across six surfaces, two of which are charts. | `PL-WLWY` itself |
| `docs/MODEL.md` | The unconditional set **is** the delivered plus six compartment concentrations with 1 MAC | True of the inhaled model and false the moment item 13's intravenous models land, where there is no vaporizer dial and no MAC. | `PL-WLWY`, on the owner's refusal |

**The shape is the same in all three, and it is not carelessness.** Each began
with a sound argument about the thing in front of the session - the tiling
safety case, the readout floor, the inhaled model - and each recorded the
argument's *current instance* at the altitude of a permanent rule. The owner
caught all three; no check did, and no check could, because whether a sentence
is pitched at the right altitude is judgment rather than a fact about the tree.

**What makes it worth a rule rather than three corrections.** These documents
are the ones a later session cites to refuse work. A wrongly permanent sentence
does not fail loudly; it sits there being obeyed. Two of the three were caught
only because the owner happened to read the sentence, and the third only
because a count was run late.

**The candidate rule, in one line**: before writing a rule into `ROADMAP.md` or
`docs/MODEL.md`, say what would have to change for it to stop being true - a
new substance, a new toolkit, a new mechanism - and if the answer is anything
on the roadmap, record it as an instance with its condition named rather than
as the rule.

**Where it would go is the open question, and the routing test decides it.**
`.claude/rules/expert-review.md` is resident and already carries the
count-before-you-tighten discipline, which is this failure's sibling; that
argues for one line there. Against it: resident characters are paid in every
session, and `make check` reports the total precisely so growth is questioned.
A path-scoped rule on `ROADMAP.md` and `docs/MODEL.md` would fire exactly when
those files are opened, which is the moment this rule is needed - but a session
writing a *new* section may not read the file first, which is the gap
`CLAUDE.md` names for path-scoping generally.

**Done when.** The rule lands wherever the `CLAUDE.md` routing test puts it,
with the three instances above cited as the evidence, or the project owner
records that three instances is not yet enough to pay for it. Either closes
this.

**Closed 2026-09-16. The project owner chose resident**, in
`.claude/rules/expert-review.md` § "Say what would falsify it, then record the
instance rather than the rule", beside the count-first discipline it is the
sibling of. +1420 resident characters, which `make check` reports and
`docs/resident-instructions.md` records with the argument.

**Path-scoping was measured before the characters were spent, not waved off.**
Two rules already scope `docs/MODEL.md` - `citing-sources.md` and
`sources-and-docstrings.md` - and nothing scopes `ROADMAP.md`, so the cheap
version was one new path-scoped file over both, at zero resident cost. It would
have fired on all three instances: each opened the file before writing to it.

**It loses on one moment, and that moment is where two of the three happened.**
The floating refusal and the strip recommendation were *stated in a reply* -
and reached the project owner - before any file was opened. Deciding an
approach is precisely what `expert-review.md` governs and what no read
precedes, which is the same argument that made that file resident in the first
place (`PL-WWDT`). Also refused: widening `citing-sources.md` to `ROADMAP.md`,
which would drag a source-routing document into every roadmap edit.

**What would retire it.** `docs/resident-instructions.md` § "When a resident
rule is retired" governs. Nothing deterministic can replace this one - whether
a sentence sits at the right altitude is judgment, not a fact about the tree -
so the retirement condition is evidential rather than mechanical: a long enough
run of roadmap and spec writing with no instance of the failure, against three
in a single session before it.
