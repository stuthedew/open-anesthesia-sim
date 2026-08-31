---
id: PL-H7XN
title: CLAUDE.md keeps every rule resident whether or not a session needs it, which reduces adherence to the ones it does
priority: P2
effort: M
status: ready
classes: session-cost, infra
not-delegable: the test is that no rule was lost, that each one still fires at the moment it is needed, and that the safety-critical standard still loads in every session. That is a reading of the file against the routing test below, not a command. Anything decidable here is being built into `doc_check.py` by this item rather than checked by a worker.
feature: worker-instructions
touches: CLAUDE.md, .claude/rules, .claude/skills/docket/SKILL.md, tools/doc_check.py
added: 2026-08-30
---

**Problem.** The whole of this project's working agreement with its agents is
one file that loads in full at launch. Measured 2026-08-31: `CLAUDE.md` is 630
lines and 7,310 words — it was 547 lines when this item was filed thirty hours
earlier. Claude Code's memory documentation targets under 200 lines per file
and ties that number to adherence rather than to token cost: longer files
"consume more context and reduce adherence", and file size is the first thing
its troubleshooting section names when instructions are not being followed.
Every rule in the file is therefore slightly less likely to be followed than
it would be alongside fewer of them, and the safety-critical standard is one
of the rules paying that tax.

**Why it matters.** The file is the working agreement in full, the
safety-critical standard included, and a rule that is present but not followed
is worse than one that is absent — the absence would at least be noticed. Size
is only the symptom of that. The cause is that nothing was ever routed: a rule
that matters only when closing out an item and a rule a session could violate
in its first tool call sit in the same file and are paid for identically, in
every session, forever. Nothing in the file's history ever asked *when* a rule
is needed — only whether it was true, which everything in it is.

**Why this item no longer carries a line target** (project owner, 2026-08-31).
It previously set one: 547 against a documented 200, with "under 300 with the
safety standard resident" as the honest goal. That framing was wrong twice
over. A size target can be met without touching the cause — moving the
271-line queue section into `.claude/rules/queue.md` with no `paths:`
frontmatter halves the file and changes resident context by exactly zero,
since rules without `paths:` load at launch with the same priority as
`.claude/CLAUDE.md`. And a target you have to warn people not to optimize for,
as the previous version of this item did, is the wrong target: it invites
deleting content to hit a number, which is the one outcome this work must not
produce.

**A one-time trim is already known not to hold.** PL-034 (trim `CLAUDE.md`'s
punch-list section of what the skill restates) shipped in v0.2.3 and did
exactly that. That section is now 271 lines — the largest in the file — while
`.claude/skills/docket/SKILL.md` carries 469 lines of the same workflows. The
trim was done, and it regrew, because nothing changed about what happens when
the next rule is written.

**The test, replacing the number: at what moment does a session need this
rule, and what is the cheapest thing that delivers it then?** Four
dispositions, cheapest first:

  1. **A check or a script.** The strongest form of streamlining is not
     relocating prose but deleting it because something deterministic now
     enforces it. A rule wired into `make check` or a hook costs zero resident
     context and never fails to fire. This is the file's own "prefer
     deterministic tooling" section applied to the file itself.
  2. **A skill, loaded on demand.** The documentation's own routing rule is a
     content test, not a size one: an entry that "is a multi-step procedure or
     only matters for one part of the codebase" belongs in a skill or a
     path-scoped rule. Skills load only when invoked or judged relevant. The
     previous version of this item considered only `.claude/rules/` and missed
     this entirely, which is the gap that matters most — the largest section
     in the file is a multi-step procedure whose skill already exists.
  3. **A path-scoped rule.** Genuinely deferred: a `.claude/rules/*.md` with
     `paths:` frontmatter loads when a session reads a matching file. The
     `core/` "reads like the domain" bar is the clean case
     (`paths: src/anesthesia_sim/core/**`), as are the data-file rules.
  4. **Resident in `CLAUDE.md`.** Only what a session could violate *before*
     it would think to look anything up.

The file already states that fourth test — "these rules stay here because a
session acts on them before it would have any reason to load the skill". It
has simply been applied generously enough to justify 271 lines. The work is to
apply it strictly, with the three cheaper dispositions available as somewhere
for the displaced rules to go.

**What pins a rule resident, made concrete.** Two examples fix the boundary in
both directions. The safety-critical clinical-output standard must never be
the rule that failed to load, and it cannot be path-scoped without a session
that opens no matching file also seeing no standard — so it stays, and it is
the reason the resident file can never shrink to nothing. Less obviously, the
requirement that every commit subject lead with the item id is now load-bearing
for tooling and not merely a convention: PL-KWC1 (docket flight reads ids from
branch names only, so every harness-named branch is invisible) recovers
in-flight state by parsing commit subjects, so a session that commits without
the id makes its own work invisible to every other session's `docket next`.
A session commits without necessarily ever invoking the docket skill. That
rule is therefore resident, and the routing pass must not move it on the
grounds that it looks like queue bookkeeping.

**The growth mechanism is the durable half of this item.** The rule that a
behavior change takes effect in the session that asks for it guarantees the
file grows, and there is nothing that ever shortens it — this item's own
"why it matters", still true. Two changes, both small, both what make the
routing pass hold:

  - the behavior-change rule says **route it**, not **edit `CLAUDE.md`**, so a
    new rule is classified on arrival by the four dispositions above rather
    than appended by default;
  - `tools/doc_check.py` reports resident instruction lines — `CLAUDE.md` plus
    every unscoped `.claude/rules/*.md` — and says so when the total grows, so
    growth forces the routing question instead of passing silently. Reporting,
    not thresholding: the tool decides what the files on disk can decide and
    leaves the judgment, the way `stranded` reports rather than decides.

**Do not confuse this with tidying.** The file is long because it says useful
things. Nothing here is a licence to delete a rule for being wordy: every rule
either stays resident, moves somewhere that loads it when it is needed, or is
replaced by a check that enforces it. A rule that ends up in none of those four
places has been lost, and losing one is a worse outcome than the file staying
630 lines.

**Done when.** Every section remaining in `CLAUDE.md` can name why a session
needs it before it would look anything up; everything else has moved to a
skill, a path-scoped rule, or a check, with no rule lost; the safety-critical
standard is resident and untouched; the commit-subject id rule is resident;
the behavior-change rule routes rather than appends; `doc_check.py` reports
the resident line total; and a cold session still reaches every rule by the
route that fires when it needs it.
