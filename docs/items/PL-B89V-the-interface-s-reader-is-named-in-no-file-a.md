---
id: PL-B89V
title: The interface's reader is named in no file a session loads, so every session writing app/ writes for a lay reader by default
priority: P1
effort: S
status: done
classes: ux
feature: teachable-case
milestone: v0.4.11
touches: .claude/rules/ui-reader.md
added: 2026-09-08
closed: 2026-09-08
pr: 472
verify: python3 tools/rules_paths_check.py && grep -q 'anesthesia' .claude/rules/ui-reader.md
---

**Problem.** The screen carries seven standing explanatory paragraphs, 1,868
characters of italic tutorial text, above two charts. `PL-6580` (strip the
concentration chart's explanatory prose) was filed on 2026-09-05 recording the
owner's ruling — "the audience is an anesthesia provider, not a lay reader" —
and is still `P2 / ready`. The prose was never removed; nothing added it back.

The question this item answers is the second one the owner asked: why sessions
keep writing it. They are never told who reads it.

The audience appears in exactly two files in the tree:

- `docs/consultant-brief.md:27`, "The audience is anesthesia residents" — a
  paste-able brief for an outside reviewer, loaded by no session;
- `PL-6580`'s own **Why it matters**, invisible unless that item is picked.

Neither reaches a session editing `app/simulation_view.py`. What *does* reach
it is `CLAUDE.md`'s safety-critical clinical-output standard, resident in every
session, requiring that model limitations be made visible and that a modelled
quantity never read as a measured one. Every one of the seven paragraphs is a
locally correct discharge of that requirement. Each is true; each is defensible
alone; the sum is a panel a reader has to get through before reaching the plot.

That is the mechanism, and it is not a lapse: the standard that produces the
prose is resident and the constraint that would bound it is nowhere. A session
writing "MAC-awake is the population concentration at which half of patients
respond to command — a different endpoint from MAC, which is immobility to
incision" is explaining first-year knowledge to a specialist, and has nothing
in context telling it so.

**Why it matters.** The owner has now made the same finding twice, three days
apart, about the same screen. A ruling that reaches no session is re-litigated
every time it is noticed, and in between, sessions keep producing exactly the
output it rules against — correctly, by the only standard they can see. Fixing
the seven paragraphs without fixing this fixes one screen; the next panel is
written by a session with the same context, and comes out the same way. This is
also the cheapest of the three items here: one path-scoped file, no resident
context, no product code touched, and it lands before either of the other two
so that the strip work is done by sessions that know why.

**Why a path-scoped rule is the right disposition.** `CLAUDE.md`'s routing test
asks at what moment a session needs the rule. The moment is editing a file
under `src/anesthesia_sim/app/`, which is always preceded by a read of a
matching file — so disposition 3 fires exactly on time and costs no resident
context. `.claude/rules/ui-color.md` already carries that glob and is the
model: it states what the tool decides, and what it leaves to the person.

Prose alone does not hold, which is the argument `ui-color.md` opens with about
contrast claims. `PL-QS9H` (measure the interface's standing explanatory text)
is the check half, and this item does not wait on it.

**Scope.** New `.claude/rules/ui-reader.md`, `paths: /src/anesthesia_sim/app/**`.
It states who reads the screen, what that reader already knows, and where the
statement a paragraph would have made belongs instead — `docs/MODEL.md`, which
already carries the full form of every one of the seven. It draws the line the
safety standard actually requires: traceability is discharged by labels, units,
named reference values and model identity, not by tutorial sentences, and the
transient banners that fire on a condition are a different category and stay.

**Done when.**
- `.claude/rules/ui-reader.md` exists and `tools/rules_paths_check.py` accepts
  its glob.
- It names the reader, and says what that reader does not need explained.
- It does not restate the safety-critical standard, which is resident already;
  it says where that standard is discharged in this interface.
