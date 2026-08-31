---
id: PL-H7XN
title: CLAUDE.md keeps every rule resident whether or not a session needs it, which reduces adherence to the ones it does
priority: P2
effort: M
status: done
classes: session-cost, infra
not-delegable: the test is that no rule was lost, that each one still fires at the moment it is needed, and that the safety-critical standard still loads in every session. That is a reading of the file against the routing test below, not a command. Anything decidable here is being built into `doc_check.py` by this item rather than checked by a worker.
feature: worker-instructions
touches: CLAUDE.md, .claude/rules, .claude/skills/docket/SKILL.md, tools/doc_check.py
added: 2026-08-30
closed: 2026-08-31
pr: 116
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

**The routing decision, worked out 2026-08-31 and recorded so the pass can be
executed without re-deriving it.** Line counts measured against `CLAUDE.md` at
640 lines, after the behavior-change rule landed.

| Section | Lines | Disposition |
| --- | --- | --- |
| Working with the project owner | 156 | Resident, less the ~50-line closing-block spec |
| Architecture and development discipline | 13 | Resident, whole |
| Session and tool-use efficiency | 59 | ~20 resident; ~20 owner-facing lines leave |
| Prefer deterministic tooling | 49 | ~15 resident; worked examples leave |
| The queue, and how the project owner works | 281 | ~90 resident; ~170 to the skill |
| Safety-critical clinical-output standard | 33 | Resident, untouched |
| Proactive expert review | 45 | ~10 resident; the rest path-scoped |

The seven judgments behind that table, in the order they have to be made:

  1. **The closing-block spec moves for coherence, not for context.** `CLAUDE.md`
     declares `.claude/rules/instruction-writing.md` the authority on reply
     shape and then spends fifty lines specifying reply shape. That is the
     documented conflicting-instructions hazard, and consolidating removes it.
     But an unscoped rules file loads at launch, so **this saves no resident
     context and must not be reported as if it did.**
  2. **Architecture and development discipline does not split.** Thirteen
     lines, and the rule keeping simulation code independent of Flet has to
     fire before a first *write* under `src/`. Path-scoped rules trigger on
     reads, so scoping it would open a hole for exactly the session that
     creates a new file without reading a neighbour first.
  3. **The model-capability and `opusplan` paragraphs instruct the owner, not
     the session** — a session cannot switch its own model. Twenty lines
     charged to every session that direct nobody in it. They should leave
     `CLAUDE.md`; where they land is open. Not `docs/worker.md`, which is
     addressed to worker agents rather than the owner — a short maintainer
     note under `docs/` is the recommendation, and the choice is the one
     genuinely open question in this pass.
  4. **Deterministic tooling stays resident but compresses.** It fires while
     *deciding* whether to build a mechanism, which is before any path is
     touched, so it cannot be path-scoped. Keep the four-tier rule and "do not
     script the judgment"; the worked examples are illustration.
  5. **The queue splits on whether the trigger is also the skill's trigger.**
     Resident: the two modes, capture, the behavior-change and routing rule,
     naming the work after the item, commit-and-push, capture-intent in short
     form, compounding friction, the division of labour, and the pointer to
     the skill — a session does all of these without ever having reason to
     load `docket`. To the skill, whose own trigger is the moment each fires:
     workflow-before-product, where an item's work happens, pairing a finding
     with the item it completes, `P0` hotfixes, not starting an `L` from a
     queue entry, clearing recorded debt, an idea arriving mid-task, closing
     the loop back to the roadmap, answering "what next" from the roadmap
     down, design-before-items, offering the release, pasting the tag
     commands, reporting gate progress, and concurrency being ruled out rather
     than certified.
  6. **Two of them are not moves at all.** "Prefer finishing a feature to
     advancing several" describes what `docket next` already ranks, so the
     prose is enforced and one line survives. "Never write an item id bare in
     a reply" restates `instruction-writing.md` rule 7, which already requires
     a plain-language gloss at first use; fold its specifics into rule 7
     rather than keeping both, since two statements of one rule is the
     hazard named in judgment 1.
  7. **`Proactive expert review` is the one place a mistake here is unsafe.**
     The two-standards paragraph stays resident: it decides where effort goes,
     before any file is read. The `core/` "reads like the domain" bar scopes
     cleanly to `src/anesthesia_sim/core/**`, and the domain list to `src/**`
     and `docs/**`. But the principles that are safety-adjacent — false
     precision, modeled versus measured, misleading plots — **move into the
     safety-critical section and stay resident**, never into a path-scoped
     file. A safety rule that fails to load is the failure this whole item
     exists to prevent, and it is the one outcome no amount of context saving
     would justify.

Execute in that dependency order: rules files first, then `CLAUDE.md`, then
the skill, then the `doc_check.py` reporter, since each later step's content
is decided by the earlier one.

**Done when.** Every section remaining in `CLAUDE.md` can name why a session
needs it before it would look anything up; everything else has moved to a
skill, a path-scoped rule, or a check, with no rule lost; the safety-critical
standard is resident and untouched; the commit-subject id rule is resident;
the behavior-change rule routes rather than appends; `doc_check.py` reports
the resident line total; and a cold session still reaches every rule by the
route that fires when it needs it.


**Worked 2026-08-31.** Executed in the dependency order above. Resident
instruction lines went 684 to 482 (`CLAUDE.md` 640 to 364); the rest is
path-scoped, in the skill, or addressed to the owner rather than to a session.

The table's projections held for five of seven sections. Two ran over and were
compressed against the routing test rather than against the number: `Prefer
deterministic tooling` kept its worked examples on the first pass, and `The
queue` kept the rationale paragraphs behind rules whose statements were two
lines each.

**Judgment 1 needed a destination the table did not name.** `PL-DGM4` recorded
that `.claude/rules/instruction-writing.md` stays project-free so a user-scope
copy carries the same statement, and the closing-block spec is roughly a fifth
project-specific — `bin/docket show`, filing a queue item, release offers.
Splitting one rule across two files would have recreated the hazard judgment 1
exists to remove, so the spec went in whole as rule 14, written project-free,
and the queue-flavoured instances went to the skill's close-out and `Always`
sections. The gloss rule is rule 7, which meant amending the `SCOPE` preamble:
rules 1-9 apply only to step-by-step procedures, and a gloss that applied only
there would have lost the rule.

**Judgment 3, the one open question, took the item's own recommendation.**
`docs/maintainer.md`, addressed to the owner. `docs/MODEL.md` was too close a
name to reuse for anything about model *choice*.

**Judgment 7 was widened by one file.** `expert-review.md` is scoped to
`tests/**` as well as `src/**` and `docs/**`: the verification-versus-validation
principle and the reference-case principles apply while writing a test, and a
session editing only `tests/` would otherwise not see them.

One principle was reclassified out of the path-scoped file after re-reading it:
"consult the source rather than memory, before forming the recommendation"
covers how the project is run as much as what it builds — testing strategy,
release process, delegation design — so it can fire in a session that opens no
matching file, and it is resident.

`PL-921W` (the formatter target applies to `tools/`, which must run under bare
`python3`) was found while adding the reporter and is captured: `ruff format`
at `py314` rewrote a parenthesized multi-type `except` into PEP 758's
unparenthesized form, which the 3.11 that runs `make check`'s `python3
tools/doc_check.py check` cannot parse. Worked around here by naming the tuple,
with a regression test at the 3.11 floor; the general guard is that item.
