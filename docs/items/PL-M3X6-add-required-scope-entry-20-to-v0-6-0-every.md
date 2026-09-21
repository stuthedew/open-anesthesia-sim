---
id: PL-M3X6
title: Add Required-scope entry 20 to v0.6.0: every surface this milestone brings into existence has its appearance and its edge states decided here, rather than inherited from Qt defaults or deferred to the visual pass at v0.7.x
status: untriaged
feature: interface-areas
added: 2026-09-21
---

**Problem.** Add Required-scope entry 20 to v0.6.0: every surface this milestone brings into existence has its appearance and its edge states decided here, rather than inherited from Qt defaults or deferred to the visual pass at v0.7.x

**Decided (project owner, 2026-09-21, ratified)** - chosen over leaving the
appearance of these surfaces to the visual pass (planned-milestone item 33,
`v0.7.x`), and over pulling that whole pass forward into this milestone.

**The argument, which is the project owner's.** UI decisions about layout and
location - where a y-axis control lives, how many readout columns fit, what an
axis is scaled against - are informed by what a View looks like. Taking them
now, against a monolithic GUI, means taking them twice: once here and again
when the same surface becomes a View in an Area. What this entry adds is the
same argument pointed at the surfaces this milestone *creates* rather than the
ones it inherits.

**The gap it closes.** Required-scope entries 1-19 are all mechanism: the
layout model, the adapter, the registry, the View contract, the import
boundary, the unconditional region, the size refusal, state ownership, run
identity, the Workspace object, persistence, the default Workspaces, the
operations, keyboard reachability, the chooser, the visibility predicate, the
tests and the documents. Entry 14 says what a border drag *does*; entry 16 says
what the chooser *guarantees*. **No entry says what any of it looks like**, and
§ "Explicitly out of scope for v0.6.0" sends "the visual composition of each
surface" to item 33. So as scoped, this milestone ships its own new surfaces
looking like whatever Qt's defaults or the first commit produced, and item 33
redoes them two steps later.

The roadmap already contains the argument that makes this a gap rather than a
preference. Item 33 was moved *after* item 34 on 2026-09-16 on the ground that
item 34 "introduce[s] an area header, a workspace tab strip, a live splitter
handle and a drag affordance, **none of which exists to be styled today**".
That reasoning says the visual pass should wait for these to exist. It does not
say they should be built without a look.

**The test that defines membership: does this surface exist in the application
today?** If it does not, nothing has ever decided its appearance or its edge
states, and the decision still gets made - implicitly, by the toolkit. This is
the *new-versus-inherited* axis, and it is deliberately not the
furniture-versus-content axis: the unconditional region is content, and the two
failure states are states, yet all three qualify. A session reaching for "UI
chrome" as the label for this entry has the wrong axis and will get those three
members wrong; the term is standard (Nielsen Norman Group, "Browser and GUI
Chrome") and correctly names the *furniture* - the tab strip, the header, the
handle - which is a subset of this entry and not its definition.

**The drafted entry was reviewed and approved as written** (project owner,
2026-09-21, ratified) - the rule sentence and all seven members below, put to
them verbatim and agreed without amendment. So the `ROADMAP.md` edit is
transcription rather than a further design round: a session implementing this
writes what is in the `Done when.` section, and reopens it only on the ordinary
evidence a ratified decision admits.

**Land it with `PL-D8KW`, not separately.** Both edit `ROADMAP.md`, and this
entry inserts roughly thirty lines inside § "Required scope", which moves every
line below it - including the § "The cadence" beat-3 sentence `PL-D8KW`
repoints. Two branches editing that file in the same window is an avoidable
conflict, and a line-number citation written by the first is stale for the
second.

**Done when.** `ROADMAP.md` § "v0.6.0 - the layout is the reader's" ->
"Required scope" carries entry 20, stating the rule

> Every surface this milestone brings into existence has its appearance and its
> edge states decided here - not inherited from the toolkit, not deferred to the
> visual pass.

and naming these seven, each with a queue item behind it:

1. **The Workspace tab strip.** Where it sits, active versus inactive, how
   rename/duplicate/delete surface, and how a shipped default is distinguished
   from one the learner saved.
2. **The Area header** - whether there is one at all. If yes: height, contents,
   whether the View name and the chooser live in it. If no: where the chooser
   goes instead. Named by item 33's own move argument; specified by no entry.
3. **The splitter handle**, which v0.4.26 built inert and this milestone turns
   live: width, rest, hover, cursor, drag feedback.
4. **The corner split/join affordance.** Visible widget as in Blender, or hot
   zone; whether a drag previews the split before it commits. This is the most
   learnable-or-not interaction in the milestone - an invisible affordance
   means most learners never discover the layout is theirs.
5. **The View chooser** as a thing seen, where entry 16 specifies only what it
   guarantees.
6. **The two failure states**, which are presentation-safety rather than taste:
   an Area naming a View this build lacks (entry 4) and an Area refused a size
   (entry 8). Both are deliberate divergences from Blender, both are seen by a
   learner, and a failure state that looks plausible is the hazard
   `CLAUDE.md`'s clinical-output standard names.
7. **Where the unconditional region sits.** Entry 7 guarantees it is outside
   the layout container; nothing decides where it goes or what it looks like,
   and it is on screen in every Workspace a learner ever builds.

**The pixel budget is entry 20's too, and is the one question none of the seven
carries alone.** The tab strip, the headers and the live handles all take screen
from the chart, which is the teaching payload. `PL-Z4K6` already asks whether
seven readout columns are wanted on a 1366 px laptop, on a window carrying none
of this furniture yet. Nielsen's term for the failure is "chrome obesity"; the
project needs the number before it adds three new consumers.

**Why it matters.** The headline feature of this milestone is the
workspace/area/View system itself (project owner, 2026-09-21). A session that
reads entries 1-19 builds it correctly and it looks like an unstyled toolkit
demo, which is not the release this milestone is for.

