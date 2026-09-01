---
id: PL-L9JS
title: "Eight open items carry a verify: command that passes without their work, so docket verify would accept a branch that did nothing"
status: untriaged
added: 2026-09-01
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
