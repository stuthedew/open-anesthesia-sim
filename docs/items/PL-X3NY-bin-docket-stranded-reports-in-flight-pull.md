---
id: PL-X3NY
title: bin/docket stranded reports in-flight pull-request work and abandoned-branch work identically because it reasons from refs alone, where the GitHub API can classify the two - so the reader re-derives every session what one API read would settle
status: untriaged
added: 2026-09-19
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
