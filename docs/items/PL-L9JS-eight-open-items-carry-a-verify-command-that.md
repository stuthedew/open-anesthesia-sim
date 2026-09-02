---
id: PL-L9JS
title: "Eight open items carry a verify: command that passes without their work, so docket verify would accept a branch that did nothing"
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: docs/items
added: 2026-09-01
not-delegable: the command that would prove this is `bin/docket check` itself, which cannot be a `verify:` command because `docket check` runs every open item's `verify:` command - it would recurse. What is left is eight judgments about what would prove each item done, which no command makes.
---
**Problem.** Found by running `PL-3CBS`'s new check against the store on
2026-09-01. Of 29 open items carrying a `verify:` command, 8 pass on a tree
where their work plainly does not exist:

| Item | Command | Why it passes anyway |
| --- | --- | --- |
| PL-2HTF, PL-4YY1, PL-KQKM, PL-MS54, PL-XH1D | `python3 tools/doc_check.py check` | Whole-project doc check; passes whenever the docs are internally consistent. Four of the five are about docs being *wrong* in ways `doc_check` does not decide, and `PL-XH1D` wants a `CONTRIBUTING.md` that does not exist. |
| PL-M58K | `uv run pytest .../test_roadmap.py -q && bin/docket wave` | Both halves pass today; neither mentions `GATE_SUBSECTION`. |
| PL-TH7P | `uv run pytest subprojects/docket/tests -k duplicate` | Matches pre-existing duplicate-id tests. |
| PL-WB0X | `uv run pytest -k simulation_view` | Passes on the 1082-line view the item exists to split. |

**Why it matters.** `verify:` is not documentation. `docket verify` runs it as
the primary evidence that delegated work was actually done, so for these eight
a worker who changed something inside `touches` and did none of the work would
get `ACCEPT`. The remaining checks in `verify_item` are scope checks - diff
inside `touches`, no suppression added, no assertion removed - and none of them
looks at whether the commissioned behavior exists. That is the delegation gate
open, not merely an untidy field.

It is also the failure the `docket` skill already names: "All six commands that
ever existed here were wrong in the same two ways and none had been executed."
The rule adopted in response was to run the command before recording it. These
eight predate or escaped that rule, and a command that passes before the work
is the one shape running it once would not catch - it has to be run and seen to
*fail*.

Five of the eight share one command, which `PL-3CBS`'s advisory reports as
proving nothing with certainty: a command recorded against several open items
cannot be evidence for any one of them.

**Where.** The eight item files above. `subprojects/docket/README.md`'s
"An open item whose own command already passes" documents how they were found;
the `docket` skill's "The `verify:` command, and running it before writing it
down" is the rule they fail.

**Done when.** Each of the eight either carries a command that fails on a tree
without its work and passes with it, or records in `not-delegable:` why no such
command exists. `bin/docket check`'s landed advisory then names only items
whose work has genuinely landed.

**Note on scope.** This is eight small edits to item files, not code. It needs
each item's work understood well enough to say what would prove it done, so it
is a grooming pass rather than a delegable batch - and per the skill it is
cheapest done as each item is started, not in one campaign away from the work.
Triage should weigh that against the delegation gate being open in the meantime.

**Triaged 2026-09-01.** P2, `defect`/`infra`, `dev-tooling`. One correction to
the table above, from `bin/docket check` on this branch: the advisory named
nine, not eight, and the ninth - `PL-3CBS` - was the one genuine "work landed"
case rather than a ninth bad command. It is closed in this change, so the
advisory now names exactly the eight above.

Left out of v0.2.8's frozen list: the machinery at fault is `docket verify`,
the delegation gate, which that release's goal does not name. The list is
`the merge path, the release script, the queue's ranking, the session-start
digest, the type-check and lint gates, and the instructions a session reads`,
and delegation is none of them.

**Why no `verify:` command.** Recorded in `not-delegable:` above and worth the
sentence: the natural proof is that `docket check`'s landed advisory names none
of the nine, but a command that runs `docket check` is run *by* `docket check`,
so it recurses without bound. That is a live constraint on what any item about
the store's own commands may record, not a quirk of this one.

**Paired with `PL-71P4` on 2026-09-02.** This item is the repair half and
scopes itself to the nine item files; `PL-71P4` (make a `verify:` command that
passes before its work an error rather than an advisory) is the preventive half.
Repairing without preventing does not converge: `PL-6P9Y` joined this set
between 2026-09-01 and 2026-09-02 without anybody touching it, when `PL-Q2BJ`
(#144) added a test whose name matched its `-k out_of_scope` selector, flipping
the command from exit 5 to exit 0. Fourteen open items still carry `-k`
selectors and are latent members of the same set, so the nine can be worked to
zero and be non-zero again from work that did nothing wrong. `PL-71P4` carries
the evidence and a sequencing note arguing this item should go first.

The count in the table above is eight; the advisory named nine on 2026-09-02,
the ninth being `PL-6P9Y`. Checked on that date: none of the nine is landed
work - all nine are non-discriminating commands, so the table's conclusion holds
for the larger set.
