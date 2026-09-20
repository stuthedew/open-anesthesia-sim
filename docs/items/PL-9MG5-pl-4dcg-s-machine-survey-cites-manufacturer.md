---
id: PL-9MG5
title: PL-4DCG's machine survey cites manufacturer manuals the reference corpus does not hold, so every machine value it recorded is owner-attested rather than checkable
priority: P2
effort: S
status: ready
classes: docs
feature: provenance
touches: docs/references/README.md
added: 2026-09-20
payoff: makes the machine values PL-4DCG recorded checkable against a held page instead of owner-attested, before the abstraction PL-FG9D just landed carries them into a displayed number
verify: grep -qiE 'Perseus|Zeus IE|anesthesia machine manual' docs/references/README.md
---

**Problem.** PL-4DCG's machine survey cites manufacturer manuals the reference corpus does not hold, so every machine value it recorded is owner-attested rather than checkable

**Where this came from.** The session that ran `PL-4DCG` (survey the anesthesia
machines in current clinical use for the variables that change a simulated
result) closed with two outstanding asks recorded in its handover, and was then
archived. One of them - decide the fresh gas flow rationale - is safe, because
`PL-NM7X` carries it as a `P1` `ready` item at the top of the queue. The other,
*add the machine manuals to `open-anesthesia-sim-references`*, was in no item at
all and existed only in that archived session's summary. This is `PL-H1JD`'s
failure arriving for real: a session's outstanding requests live in
`post_turn_summary.needs_action`, which archiving deletes silently. Filed on the
project owner's instruction, 2026-09-20.

**Why it matters.** `PL-4DCG`'s own `not-delegable:` line states the standard it
was held to - "its correctness is whether each recorded value matches the manual
revision it cites" - and `docs/machine-abstraction.md`, which `PL-FG9D` built on
that survey, requires every value to carry "a manufacturer's operator or
technical manual, cited by document and revision". The manuals are not held, so
no later session can perform that check. Every machine value now in the tree is
therefore *owner-attested rather than checkable*, which is exactly the state
`PL-7Y27` closed three vaporizer figures in and recorded as a limitation rather
than a gap anyone could close.

The corpus is what closes it. `PL-5NR5` verified the route end to end on
2026-09-13 and `PL-XJ5P` wrote it down: `add_repo` attaches
`stuthedew/open-anesthesia-sim-references` mid-session, `git clone --depth 1`
needs no credential in the sandbox, and `.claude/rules/citing-sources.md:193-199`
carries the `poppler-utils` prerequisite and the `pdftotext -layout` reader. The
four papers added that day paid for themselves on arrival; the same applies
here, and the holdings are larger and more citation-dense than a paper.

**What the corpus needs.** The operator or technical manual, at a stated
revision, for each machine `PL-4DCG` surveyed - five models across Dräger, GE
HealthCare and Getinge, `Perseus A500` and `Zeus IE` named explicitly in the
survey's output. The revision matters more here than for a journal article: a
manual is revised without changing its title, so a value cited to "the Perseus
manual" is not reproducible, and `docs/machine-abstraction.md` already demands
document *and* revision.

**Two constraints `PL-5NR5` measured, both of which bite harder for manuals.**
A browser upload caps at 25 MB, so a large manual has to arrive by command line;
and a machine manual is typically a few hundred pages, which is the shape
`PL-5NR5` recorded as needing a per-folder catalogue of chapters and page ranges
so a session reads the one section worth opening rather than the volume.

**The split of the work, which is why this is not one act.** Supplying the files
is the project owner's - they are publisher-copyright documents a session cannot
obtain, exactly as the four papers were. Indexing them is a session's:
`docs/references/README.md` gains their entries, and reading one obliges an
extraction note under `PL-Z3V5`'s convention, so the values `PL-4DCG` recorded
become checkable against a held page rather than against a memory.

**Why it matters, stated for the gate rather than the reader.** A machine value
that no one can check is a provenance failure under `docs/MODEL.md` § "Source
hierarchy", and machine values reach displayed clinical numbers through the
abstraction `PL-FG9D` just landed.

**Done when.** `docs/references/README.md` names the held machine manuals by
manufacturer, model and revision, with the per-folder catalogue `PL-5NR5`'s two
constraints call for; and at least one extraction note exists for a value
`PL-4DCG` recorded, so the convention is exercised rather than described.
