---
id: PL-X3NY
title: bin/docket stranded reports in-flight pull-request work and abandoned-branch work identically because it reasons from refs alone, where the GitHub API can classify the two - so the reader re-derives every session what one API read would settle
priority: P2
effort: M
status: ready
classes: defect, infra
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-19
verify: grep -q 'def test_stranded_names_a_branch_with_a_pull_request_open_apart_from_one_behind' subprojects/docket/tests/test_cli.py && uv run pytest -q subprojects/docket/tests/test_cli.py -k stranded_names_a_branch_with_a_pull_request_open
---

**Problem.** `cmd_stranded` states its own limit deliberately, and the limit is
the whole of what a reader wants: "an item on a branch that is still being worked
is the normal case, and the command cannot tell that from an item on a branch
nobody will merge. Reporting is the whole job; deciding which of the two a branch
is remains the reader's."

That refusal is correct **for the evidence the command uses**, which is refs. It
is not correct for the evidence available. A branch with an open pull request is
in flight; a branch whose pull request merged is safe to delete; a branch with no
pull request and no commits for some interval is abandoned. GitHub answers all
three, and this project already reads that API — `docket record` recovers a `pr`
number from a merge commit. The classification is decidable; the command simply
does not have the input.

**Live example, from the session that filed this.** The 2026-09-19 digest
reported `PL-PZ8D` and `PL-TPCH` as "Filed on a branch, not yet on
origin/main" — they were on an open pull request, `#715`, behaving exactly as
intended — in the same breath as `PL-GL5P` and `PL-YFXG`, which are genuinely
behind. Nothing in the output separated them. A reader who acts on that list
either recovers work that is already in flight or learns to skim it.

**Why the obvious automation is refused, and by an incident rather than an
argument.** Auto-recovering every stranded item is the first thing anyone
proposes, and the same docstring records what it costs: "the recovery this
command hands over is a `git checkout` that overwrites the newer copy with the
older one. That is not the hazard in theory: it happened on 2026-09-05, eight
minutes after `#325` merged (`PL-KBFN`, `PL-39B7`)." An unconditional
`--recover` reproduces that class of loss on every run where a merge landed
between the fetch and the checkout. So recovery stays a decision even once
classification is automated; what changes is that the decision arrives with the
branch's state attached instead of requiring a manual lookup.

**Why the deletion half is worse, and must not be automated on git evidence.**
The dead-ends list already holds it: "Commit-containment (`git branch --merged`)
for in-flight and stranded detection — rejected: a squash merge contains none of
the branch's commits, so every squash-merged branch reads as unmerged forever."
This repository squash-merges, so git's own answer to "has this branch landed" is
wrong for every merged branch here. Deleting on that signal is destructive and
irreversible. The pull-request state is the only sound input, and even with it the
delete should be printed as a command rather than run — a branch with no pull
request may be someone's unpushed direction rather than abandoned work.

**The shape this should take.** Classify, do not act:

- **in flight** — the branch has an open pull request. Say so and say which, and
  leave it out of the recovery list entirely. This is the noise reduction that
  makes the rest readable.
- **landed** — the pull request merged. The item is already on the base or should
  be; print the branch as a deletion candidate with the exact command, and do not
  run it.
- **behind** — no pull request, or a closed unmerged one. This is the only genuine
  stranding, and the only case the current recovery advice should be offered for,
  still as a command and still after a fetch.

**Scope note for whoever takes this.** `stranded` already fetches and the
docstring explains why — every finding is a claim about what the base does not
hold. Adding a network read to a command that already makes one is not new
exposure, but `--no-fetch` exists for a checkout with no network, so the
classification needs an offline degradation that says it could not classify rather
than guessing — the floor in `.claude/rules/apparatus-standard.md` asks for
exactly that. `cmd_orphaned`, printed alongside, has the same two-category problem
for non-item files and should be considered in the same pass.

**Why this is worth doing at all, given the freeze.** It removes a recurring
per-session judgment rather than adding a mechanism: the command already runs on
every session start through the digest, and every session currently pays the same
manual lookup. It is a defect in an existing check under
`.claude/rules/apparatus-standard.md`'s floor — a partial reading handed over as
a complete one — not a new feature.

**One premise in the brief above is wrong, checked 2026-09-19.** It reads
"GitHub answers all three, and this project already reads that API - `docket
record` recovers a `pr` number from a merge commit." The first clause holds;
the second does not, and it is the one carrying the cost argument. `docket
record` reads **git**: `merged_pull_requests` in
`subprojects/docket/src/docket/vcs.py` parses merge-commit subjects on the
default branch, and no module under `subprojects/docket/src/docket/` imports
`urllib` or names `api.github` - the single `GITHUB_TOKEN` hit in `checks.py`
is prose in a docstring. The two scripts in this repository that do read the
API are `tools/pr_title_check.py` and `tools/main_ci_status.py`, and `bin/docket`
runs neither.

So the proposal is not a scope change to a command that already talks to
GitHub. It would make `bin/docket` a network client for the first time, in a
command the session-start hook runs on every session, and `CLAUDE.md` and
`docket.toml` both rest on `bin/docket` running "from a bare checkout with no
virtualenv". That is a larger change than the brief prices, and it is what
moves this item to `needs-decision` rather than `ready`.

**Why it matters.** The noise is real and is paid every session. The 2026-09-19
digest listed `PL-PZ8D` and `PL-TPCH` - on open pull request `#715`, behaving
exactly as intended - beside `PL-GL5P` and `PL-YFXG`, which are genuinely
behind, with nothing separating them. That is
`.claude/rules/apparatus-standard.md`'s floor: a partial reading handed over as
a complete one, where at the point of use the two are indistinguishable. And it
is `CLAUDE.md`'s second compounding-friction test - an advisory being routed
around - because the reader who learns to skim this list is the reader who
skims the genuine stranding in it. `PL-XLQ5` is what acting on the wrong entry
costs: a `git checkout` that overwrote a newer copy with an older one, eight
minutes after `#325` merged.

**Decision needed.** Which evidence `stranded` classifies from, given that the
API is a new dependency for `bin/docket` rather than an existing one:

1. **Read the GitHub API**, from the standard library, with an offline and
   unauthenticated degradation that says it could not classify. Answers all
   three categories. Costs `bin/docket` its no-network property in the command
   the session-start hook runs every session, and needs a token where the
   repository is private.
2. **Classify from git alone, and say so.** `merged_pull_requests` already
   identifies a branch whose work the base has taken, which separates **landed**
   from the rest - the largest and safest of the three categories, and the one
   whose recovery advice is actively harmful. **in flight** and **behind** stay
   merged into one bucket the reader still judges, labelled as such. Cheapest,
   keeps the tool offline, and removes most of the noise rather than all of it.
3. **Move the classification into a `tools/` script** that already reads the
   API, and leave `docket` reporting what refs say. Keeps the boundary that
   `bin/docket` is git-only, at the cost of a second place a session has to
   know to look.

Route 2 is the recommendation on the evidence above: it is the only one that
needs no new dependency, and the category it can decide is the one carrying
`PL-XLQ5`'s loss. Whether the residual in-flight/behind ambiguity is worth
route 1's cost is the part that needs an answer.

**Done when.** `bin/docket stranded` separates the branches it can classify
from the ones it cannot, names which evidence it used, and degrades by saying
it could not classify rather than by guessing; the recovery advice is printed
only for the category it is safe for; and `cmd_orphaned`, which has the same
two-category problem for non-item files, is either covered in the same pass or
recorded as out of scope with the reason.

**Decided 2026-09-22, at the project owner's request, by `PL-7TVT`'s
second-half session: route 1, through the command `flight` already runs.** The
premise that moved this to `needs-decision` - that the API would make
`bin/docket` a network client for the first time - stopped holding when
`PL-Q664` added `open_pull_requests_command`: the package still knows nothing
about GitHub and asks a command `docket.toml` names, and since `PL-7TVT` `flight`
asks it on every run that has a row, printing each branch's pull request by
number. So the cost route 1 was priced at is already paid, and routes 2 and 3
now buy less for more.

What to build: `bin/docket stranded` asks the same command once and splits its
branches - **pull request open** (named with its number, left out of the
recovery advice, because recovering in-flight work is `PL-XLQ5`'s overwrite),
**none open** (the recovery advice, as today), and **unasked** (no command, no
token, `--no-fetch`, or a failure: one bucket saying it could not classify,
never read as "none open"). Reuse `vcs.open_pull_requests` and
`cli._open_pull_requests` rather than a second lookup. `cmd_orphaned` takes the
same split in the same pass. The session-start digest stays offline and keeps
pointing at the command: it is resident in every session, and rule 14 already
runs `stranded` before every closing block, which is where the split is acted
on. A merged pull request needs no category of its own here: its items are on
the base, so `stranded` does not list them.

**Stress test, 2026-09-25 (PL-P0FP).** Reproduced as the simulation's V6: `stranded` hands back a capture on an open, armed pull request with a recover line. The simulation also found why classification needs more than the existing seam: `open_pull_requests_command` is docket's only forge input, only `flight` reads it, and its contract lists open pull requests only, so merged, closed-unmerged and never-opened are indistinguishable - a closed-unmerged pull request's claim blocks its item for the full 7-day lease. Now a member of PL-XBV4.
