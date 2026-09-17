---
id: PL-LH18
title: Every main UI element is built to become a Blender-style area-type widget, and app/ has no rule saying so
priority: P2
effort: S
status: done
classes: docs
feature: interface-areas
milestone: v0.4.26
added: 2026-09-16
closed: 2026-09-16
pr: 618
verify: test -f .claude/rules/ui-areas.md && grep -q 'anesthesia_sim/app' .claude/rules/ui-areas.md
---

**Problem.** `ROADMAP.md` planned-milestone item 34 places the Blender-style
area system and says the Qt port "reserves for this item and builds none of
it". Nothing tells a session writing an `app/` view *today* what that
reservation asks of the code it is writing. The port's own reservation is
structural - each dashboard surface is an independent widget inside inert
splitters - and a session that meets only the widgets cannot infer the
constraint from them.

**Why it matters.** The project owner ruled on 2026-09-16, mid-session, that
"any main UI element going forward should understand it will ultimately be
converted into an area-type widget". That is a standing constraint on every
future `app/` change, and `CLAUDE.md`'s behavior-change rule requires it to take
effect in the session that asks for it rather than waiting in the queue while
sessions keep coding into the corner.

**Where it goes, and why not `CLAUDE.md`.** `CLAUDE.md`'s routing test picks the
cheapest disposition that fires at the moment a session needs the rule. This one
matters only under `src/anesthesia_sim/app/`, and it fires when a session opens
a view - which a read precedes - so it is a path-scoped rule, disposition 3.
`.claude/rules/ui-reader.md` and `.claude/rules/ui-color.md` are the two
existing rules on that same path and the shape it is written to match. It adds
nothing to the resident character total.

**What it says.** One test - if this widget were lifted into an area a reader
can split, resize, close or replace, what would break? - and the five recurring
answers: a view is given what it draws rather than reaching for it; state a
layout could duplicate or relocate does not live inside the widget; a view is
instantiable more than once; a view does not assume its size; a required value
never moves into something closeable. It also fixes Area/Editor/Workspace as the
vocabulary, which `ROADMAP.md` item 34 already adopted from Blender, so the code
and the roadmap do not drift apart before the system is built.

**It does not authorize building the area system.** Item 34 is placed and its
ordering is decided; the rule says so in terms, because "build for areas" reads
as permission to start otherwise.

**Done when.** A path-scoped rule under `.claude/rules/` loads for
`src/anesthesia_sim/app/**` and states the constraint. Closed the same session
it was asked for, per `CLAUDE.md`'s behavior-change rule.

**Found while building `PL-8PSW`**, which is the first view work done under it:
its run naming and its compartment-selection cap were both shaped by test 1 and
test 2 above rather than by the chart alone. `PL-VN6M` is the one concrete
violation the pass found and did not fix here.
