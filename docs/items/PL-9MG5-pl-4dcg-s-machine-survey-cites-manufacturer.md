---
id: PL-9MG5
title: PL-4DCG's machine survey cites manufacturer manuals the reference corpus does not hold, so every machine value it recorded is owner-attested rather than checkable
priority: P2
effort: S
status: ready
classes: docs
feature: anesthesia-machine
touches: docs/references/README.md
added: 2026-09-20
payoff: stops the first machine profile stalling on five manuals nobody committed to needing, while keeping the per-profile source check that makes its values checkable rather than owner-attested
verify: grep -qF 'is requested one at a time, as the profile that needs it is built' docs/references/README.md
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

**Re-scoped 2026-09-20, and moved into the `anesthesia-machine` feature.** The
project owner read this item's **Done when.** as a bulk acquisition standing
between them and a machine framework they had asked for, and said so:

> *"I wanted a modular anesthesia machine framework with machine-specific
> config files. Something simple: circuit volume, max fresh gas flow. What I
> wanted NOW was MOSTLY JUST THE FRAMEWORK... The gate now wants a fully
> fleshed-out system with all the machines on the market and multiple manuals -
> not what I intended."*

**The rule that follows, recorded as the owner stated it.** A machine's
operator or technical manual is sought **one at a time, as the profile that
needs it is built** — never as a bulk acquisition ahead of the milestone. Five
manuals for five machines nobody has committed to building is work nobody
asked for, and the item that demanded them was reading
`docs/machine-survey.md`'s eight-machine table as a build list. That reading is
now closed off at source: `PL-6WNZ` (the survey's table framed as a map of
variation, not a list to implement) landed 2026-09-20 and states the same rule
in `docs/machine-survey.md` and `docs/machine-abstraction.md`.

**The finding underneath is untouched and must not be lost.** Every machine
value `PL-4DCG` recorded is still *owner-attested rather than checkable*: the
survey cites manuals the corpus does not hold, `PL-4DCG`'s own `not-delegable:`
line sets the standard as "whether each recorded value matches the manual
revision it cites", and `docs/machine-abstraction.md` § "Question 4" requires a
profile's values to carry a source or a `provenance_gap` entry. None of that
changes. What changes is **when the debt is discharged: per profile, at the
moment that profile is built**, not in bulk now. A profile whose numbers have
no held source is a profile that cannot be added — which is the survey's own
admission rule ("an unknown apparatus volume is a machine that cannot be added
yet"), and it makes the discharge automatic rather than something this item has
to schedule.

**What this item now delivers.** The rule written down where the next session
requesting a source will read it, plus the request route. Neither needs a
manual to exist.

**Done when.** `docs/references/README.md` § "Where owner-supplied full texts
live now" records that a machine manual **is requested one at a time, as the
profile that needs it is built**, and states how a session asks for one when it
needs it: what to name (manufacturer, model, *and* revision — a manual is
revised without changing its title, so "the Perseus manual" is not
reproducible), what the corpus needs alongside the file (`PL-5NR5`'s two
measured constraints — a browser upload caps at 25 MB so a few-hundred-page
manual arrives by command line, and a per-folder catalogue of chapters and page
ranges so a later session opens one section rather than the volume), and that
reading it then owes an extraction note under `PL-Z3V5`'s convention.

**Explicitly not this item, and this is the re-scope.** Obtaining any manual.
Indexing any manual. Naming Perseus A500, Zeus IE or any other model as a
document to fetch. The previous **Done when.** — README entries for the held
manuals plus at least one worked extraction note — is withdrawn; it cannot be
met without the acquisition, and the acquisition is the thing the owner
refused. The extraction-note convention is exercised by the four papers
`PL-5NR5` added, not by a manual nobody needs yet.

**What would reopen the acquisition.** A machine profile actually being built
whose fields need a manual. At that moment the request is made for **that one
machine**, under the route this item writes down, and the check `PL-4DCG`'s
`not-delegable:` line asks for runs against a held page for that machine's
values alone. Nothing about the finding weakens in the meantime; it simply has
no bill to pay until a profile is on the table.
