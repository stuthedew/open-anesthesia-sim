---
id: PL-GDB0
title: Three times in one session a rule true only of the currently implemented model or mechanism was written into ROADMAP.md or docs/MODEL.md as a permanent rule about the project, each needing its own correction commit
status: untriaged
added: 2026-09-16
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
