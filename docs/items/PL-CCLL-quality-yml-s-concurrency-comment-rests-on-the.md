---
id: PL-CCLL
title: quality.yml's concurrency comment rests on the repository's visibility, which flipped twice in a day
status: done
priority: P2
effort: S
classes: docs, infra
feature: ci-cost
touches: .github/workflows/quality.yml
verify: python3 tools/doc_check.py check && ! grep -q 'This repository is \*\*private\*\*' .github/workflows/quality.yml
added: 2026-09-06
closed: 2026-09-06
---

**Problem.** `.github/workflows/quality.yml`'s `concurrency` comment justified
`cancel-in-progress` partly by what a superseded run *bills*, and that premise
depends on the repository's visibility - a GitHub setting no file in this tree
can read. It has now been wrong in both directions inside two days:

| When | The comment said | The truth |
| --- | --- | --- |
| before 2026-09-05 | public, standard runners free | private, minutes billed |
| 2026-09-05, `PL-SSQX` | private, minutes billed | correct at the time |
| 2026-09-06 | private, minutes billed | **public**, runners free |

The project owner made the repository public on 2026-09-06, hours after
`PL-SSQX` corrected the sentence in the other direction.

**Why it matters.** The failure is not the wrong word; it is that a comment
explaining a design decision was resting on a fact that lives outside the tree
and changes without any commit. Fixing the word again would leave the same
sentence one settings change from being wrong a fourth time, and nothing would
catch it - `PL-SSQX` was found by a session that happened to be measuring CI
cost, and this one by the owner saying so in conversation.

**Approach, and why it is not a check.** A tool could read the repository's
visibility from the API and compare it against a claim in the file. It should
not: `tools/` is standard-library-only and must answer offline, the answer
changes about once in a project's life, and `CLAUDE.md`'s gate for building a
check is that the work recurs. The right fix is to stop the argument depending
on the fact.

`cancel-in-progress` is worth having for the **runner slot** - a superseded run
holds one and the push that matters queues behind it - and that is true whether
or not minutes are billed. So the reasoning now rests on the slot alone, and
the billing position is stated once, dated, as a fact about today rather than a
premise the argument needs. The same paragraph records both flips, so the next
reader meets the history rather than a third confident assertion.

**Done when.** The comment's argument for `cancel-in-progress` holds under
either visibility, and the current position is stated once and dated rather
than woven through the reasoning.

**Closed 2026-09-06, in the session that found it.** Found by the project owner
saying they had made the repository public, one turn after this session had
merged `PL-SSQX`'s correction in the opposite direction. `P2` and `docs`/
`infra` on the same reasoning as `PL-SSQX`: nothing computes a wrong number,
but a stated premise of a design decision is false, and that is what stops a
later reader trusting the rest of the paragraph.

Source for the billing half: GitHub Docs, *Billing and usage* - standard
GitHub-hosted runners are free and unlimited on public repositories, and larger
runners are not. Read via search results rather than fetched, because
`docs.github.com` is blocked by this container's egress proxy.

**Why the repository is public, recorded on the owner's approval (2026-09-06):
to stop the Actions billing, not as a publication decision.** In their words:
"I made it public before I wanted to so i wouldn't get billed for minutes", and
"I'm not doing the human pass yet, because I'm not trying to advertise."

It is worth a line because it is the fact a later session is most likely to
invert. Three readings it forecloses:

- That the visibility is provisional and something here wants it back. Nothing
  in CI does; free standard runners are strictly better than the allowance, and
  the concurrency argument above no longer depends on either.
- That `PL-XYRN`'s human-facing pass is overdue. It is deliberately not being
  run, and a session finding a public repository with no `README.md` should
  read that as a decision rather than a gap. `PL-N092` stays `ready` because it
  is genuinely workable and standalone, not because it is being asked for.
- That this session's minute-saving work was the answer to the cost problem. It
  was not: folding a job to reclaim a rounded-up minute (`PL-D551`, `PL-9HDH`)
  and scoping the verify replay (`PL-SDHR`) were worth doing, and the owner
  removed the bill outright by changing one setting. What those items still buy
  is wall clock - 152 s to 59 s per run, measured 2026-09-06 - and runner slots
  when several sessions push at once, which is the argument this comment now
  rests on.
