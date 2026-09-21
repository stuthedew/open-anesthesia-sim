---
id: PL-7T5R
title: ROADMAP.md's live sections still call it the score architecture, twelve days after PL-ZX12 retired the term, so a session reading v0.5.0's scope hands the retired metaphor back to the project owner
priority: P3
effort: S
status: ready
classes: docs
feature: core-domain-language
touches: ROADMAP.md
added: 2026-09-20
payoff: stops every session that reads v0.5.0's scope handing the project owner back a metaphor they retired twelve days ago
verify: ! awk '/^## Completed: v0\.5\.0 - the case you can branch/,/^## v0\.6\.0/' ROADMAP.md | grep -qiE 'score architecture'
---

**Problem.** ROADMAP.md's live sections still call it the score architecture, twelve days after PL-ZX12 retired the term, so a session reading v0.5.0's scope hands the retired metaphor back to the project owner

**Why it matters.** `PL-ZX12` retired the word on 2026-09-08 (project owner) and
closed in v0.4.16 (`pr: 512`): "'score' is a metaphor a domain reader has to be
taught, in the package that should read like the domain". The code carried it
out — `RunScore` appears nowhere in `src/` or `tests/`, and
`core/run_definition.py:16-23` records the retirement and joins the two words up
for a reader arriving from older documents. That docstring names its own scope:
the term survives in "`docs/releases/` and `ROADMAP.md`'s **completed rows**",
which are historical records of the vocabulary of the day and are correct as
they stand.

The live sections were not swept, and they are the ones a session reads to do
current work. Measured 2026-09-20, `grep -niE 'score architecture' ROADMAP.md`
gives eight hits, and the split is clean:

- **Sanctioned, leave them** — lines 63, 64 (§ "Versioning decision", the
  v0.4.0 and v0.4.1 completed rows) and 1396 (§ "Completed: v0.4.0").
- **Live drift** — lines 372 and 375 (§ "The plan", the timeline rows, 375
  being v0.5.0's own row), and 2017, 2035 and 4168 (§ "v0.5.0 — the case you
  can branch", two of them inside the Goal paragraph that states what the
  milestone is for).

Two looser uses sit in the same live section and want the same judgment rather
than the same command: "now evaluates the run's *score* at the instants it
plots" and "the *score* evaluation, no toolkit in" (section-relative lines 551
and 1114).

**Two occurrences must be left exactly as they are**, and a blanket sweep over
the section would wrongly take them: the Gate 1 entry for `PL-ZX12` itself,
which has to name `RunScore` to describe the rename, and `PL-DZFJ`'s entry,
which quotes the older gate text it exists to correct. That is why the `verify:`
pins the phrase rather than the word.

**How it was found, which is the argument for fixing it rather than filing and
forgetting.** On 2026-09-20 a session was asked what v0.5.0's major feature
would be without forking. It read § "v0.5.0 — the case you can branch" § Goal,
took "the score architecture" straight out of line 2035, and put the retired
word in front of the project owner, who caught it. The drift is not inert: the
live sections are what sessions quote from, so every session answering a
question about the current milestone reproduces the term the owner retired. A
stale word in a completed row is a record; the same word in the Goal of an
unshipped milestone is a live assertion, which is the line
`.claude/rules/citation-drift.md` already draws.

**Where.** `ROADMAP.md` lines 372, 375, 2017, 2035, 4168, and the two looser
uses inside § "v0.5.0". Not `docs/releases/`, not the completed rows, and not
`core/run_definition.py`, whose bridging note is the thing that makes the older
documents readable and stays.

**Done when.** The live sections of `ROADMAP.md` — § "The plan"'s timeline rows
and § "v0.5.0 — the case you can branch" — name the run-definition architecture
in the plain terms `PL-ZX12` chose, the two occurrences that must quote the old
name are left intact and the reason is stated where a later sweep will see it,
and the completed rows and `docs/releases/` are untouched.
