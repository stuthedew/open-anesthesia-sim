---
id: PL-XJ37
title: Nothing in v0.5.0's scope lets a learner take a fork or select between runs, and SimulationView's run set is fixed at construction
priority: P2
effort: M
status: done
classes: planning, ux
feature: scenario-branching
touches: ROADMAP.md, docs/items
added: 2026-09-14
closed: 2026-09-20
payoff: turns v0.5.0 from a milestone a learner cannot reach into one they can, by naming the fork control as scope instead of leaving branching as machinery with no caller
verify: grep -qF 'Selecting which two runs are displayed' ROADMAP.md
---

**Problem.** Nothing in v0.5.0's scope lets a learner take a fork or select between runs, and SimulationView's run set is fixed at construction

**Why it matters.** `ROADMAP.md`'s v0.5.0 Goal states the end state as "a
learner runs a case, marks the decision point, **forks there**, manages the two
branches differently, and reads both on one time axis", and its out-of-scope
list allows that "N branches may exist and be **selected between**". Neither
act has an item. The milestone could close with every Required-scope entry done
and no way for a learner to take a fork.

**What the eighteen Required-scope entries cover.** `PL-LPLD` creates, lists
and removes bookmarks; `PL-8PSW` overlays two branches that already exist;
`PL-1XPX` decides what the readouts say while two are shown. The fork itself is
`PL-J2TD` (the resumption) and `PL-TFX5` (the trunk-and-branches structure),
and both declare `touches` that exclude `simulation_view.py` and `main.py` —
correctly, since both are internal by design. Nothing picks up where they stop.

**What the code says, measured 2026-09-14.** `SimulationController` is
constructed in exactly two places in `src/`: `main.build_app` builds the trunk,
and `resumed_at` builds a branch. `resumed_at` has no production caller at all —
every call site is a test. `SimulationView.__init__` takes
`controllers: Sequence[SimulationController]` and freezes `self._runs` at
construction, with `MAX_DISPLAYED_RUNS = 2` and no add-run path: the page tree,
the per-run asyncio tasks and the chart's series list are each built once from
that tuple. So the dashboard can *render* a trunk and a branch if handed both
at startup, and cannot come to hold a branch taken during a session.

**What it would take.** `main.build_app` builds a `BranchedCase` rather than a
bare controller; `SimulationView` takes the case and a displayed-pair selection
instead of a fixed sequence, and gains a path that adds a `RunView` after
construction; and a control somewhere offers `BranchedCase.fork_points_s` and
calls `fork_at`. The first two are `simulation_view.py` work and sit naturally
beside `PL-8PSW`; whether they belong to it or to an item of their own is the
question here.

**A related edge, worth deciding with it.** A branch shown in a `RunView` gets
the same agent dropdown the trunk does, and `set_agent` now refuses on a branch
(`PL-TFX5`): a branch carries the agent of the case it continues. The refusal
reaches the view's ordinary refused-setting path, so nothing breaks — but a
control that always refuses is a control presenting itself as working, which is
the hidden mode this project's own `start()` docstring argues against.

**Decision needed.** Whether the learner-facing half of forking - a control that
takes a fork, and a way to select which two runs are shown - belongs to
`PL-8PSW` (overlay two branches on one time axis) or to an item of its own, and
whether v0.5.0's `Required scope` is amended to name it.

This is the project owner's rather than a session's: it changes what v0.5.0
*is*. The milestone is called "the case you can branch", and on the code as it
stands a learner cannot take a branch - so either the scope is incomplete or the
milestone means something narrower than its name, and only the owner can say
which.

**The code claim, verified 2026-09-14.** `SimulationController` is constructed
in exactly two places in `src/`: `main.build_app` builds the trunk, and
`resumed_at` builds a branch. `resumed_at` has no production caller - every call
site is a test. `SimulationView.__init__` takes
`controllers: Sequence[SimulationController]` and freezes `self._runs` at
construction, with `MAX_DISPLAYED_RUNS = 2` and no add-run path. So the
dashboard can *render* a trunk and a branch if handed both at startup, and
cannot come to hold a branch taken during a session.

**What it would take**, so the two options can be priced: `main.build_app`
builds a `BranchedCase` rather than a bare controller; `SimulationView` takes
the case and a displayed-pair selection instead of a fixed sequence, and gains a
path that adds a `RunView` after construction; and a control offers
`BranchedCase.fork_points_s` and calls `fork_at`. The first two are
`simulation_view.py` work sitting naturally beside `PL-8PSW`. `PL-J2TD` and
`PL-TFX5` both declare `touches` that exclude `simulation_view.py` and `main.py`
deliberately, so nothing currently picks up where they stop.

**A related edge, worth deciding in the same breath.** A branch shown in a
`RunView` gets the same agent dropdown the trunk does, and `set_agent` now
refuses on a branch (`PL-TFX5`) because a branch carries the agent of the case
it continues. The refusal reaches the ordinary refused-setting path so nothing
breaks - but a control that always refuses is a control presenting itself as
working, which is the hidden mode this project's own `start()` docstring argues
against.

**Note for whoever answers it:** the Qt port now runs *ahead* of v0.5.0, and it
rewrites `simulation_view.py` wholesale. Building the selection on Flet first
would be building it where the port deletes it.

**Done when.** `ROADMAP.md` says whether taking a fork and selecting between runs
is inside v0.5.0, and if it is, the work is named - either folded into `PL-8PSW`
with that entry's scope widened to say so, or filed as its own item and added to
the `Required scope` list. The agent-dropdown edge above is disposed of in the
same answer rather than left to be rediscovered.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and the reason it
gave for deferring has expired.** The gap is unchanged:
`SimulationView.__init__` still takes `controllers: Sequence[...]` and freezes
`self._runs` at `simulation_view.py:181` with no `add_run` or `set_runs` path,
`MAX_DISPLAYED_RUNS` is 2 at `dashboard_frame.py:120`, v0.5.0's eighteen
`Required scope` entries contain neither act, and `ROADMAP.md:88` still cites
this item as live fact. `status: needs-decision` is correct.

Three corrections. The brief defers on "the Qt port now runs *ahead* of
v0.5.0 … building the selection on Flet first would be building it where the
port deletes it" - the port **shipped** in v0.4.26, so that reason is spent and
the item is stronger rather than weaker for it. `main.build_app` no longer
exists; the equivalent is `main.py:32-33`, `SimulationView((controller,))`
inside `main()`. And `resumed_at` does have a production caller now,
`controller.py:1261` inside `BranchedCase` - though nothing in `src/`
constructs a `BranchedCase`, so the gap one level up is exactly as described.

## Decided 2026-09-20 (project owner): B2 and C — forking is v0.5.0, the selector is not

The question was put as three options for the fork work and, once forking was
provisionally deferred, two for the version number. The owner's answer was
**"B2 and C, move comparison to later"**.

**What was chosen, in this item's own terms.** Both halves of the
`**Decision needed.**` above are answered:

- *Does the learner-facing half belong to `PL-8PSW` or an item of its own?*
  **Its own item.** The brief's first alternative is moot rather than rejected:
  `PL-8PSW` closed and merged in v0.4.26 (`pr: 618`), so folding into it is no
  longer available. Its scope entry stands as the record of what shipped.
- *Is v0.5.0's `Required scope` amended to name it?* **Yes**, for the fork
  control. **No** for run selection, which is deferred.

**The shape that was chosen (option C).** `main()` builds a `BranchedCase`
rather than a bare controller; `SimulationView` gains a path that adds a
`RunView` after construction; and one control offers
`BranchedCase.fork_points_s` and calls `fork_at`. The dashboard then shows the
trunk and one branch. **No run selector**, and `MAX_DISPLAYED_RUNS` stays 2.

The learner-visible result is the milestone's Goal sentence verbatim: run a
case, mark the decision point, fork there, manage the two branches differently,
read both on one time axis.

**What "move comparison to later" defers, stated so a later session does not
re-open it as an oversight.** Not comparison itself — trunk-against-branch is
what option C draws, and `PL-8PSW` already built it. What moves out is the
**selector**: choosing *which two* of N runs are displayed, and therefore

- comparing one branch directly against another rather than each against the
  trunk, and
- returning to a branch the learner has left.

Both were priced and declined on the educational question rather than the
technical one: the display is capped at two runs under either option, so the
selector buys the *choice* of pair rather than more curves, and branch-against-
branch was judged not to be a first-release teaching case. `BranchedCase.branches`
already returns a stable-ordered tuple chosen for exactly this — "a list
re-sorted by instant would renumber the branch they were looking at" — so
adding the selector later is additive rather than a rework.

**The consequence that has to be designed, not discovered: the second fork.**
With no selector, a learner who forks twice has no way to say which branch is
shown. Silently replacing the displayed branch while the first lives on in
`BranchedCase` is hidden state of exactly the kind this project refuses, so the
recommended answer is to **refuse a second fork while a comparison is shown** —
one comparison at a time, reset to start another. That is explicit and carries
no hidden mode, and it is the implementation item's to settle rather than
something to leave to the first pull request.

**The agent-dropdown edge, disposed of here as this item's `Done when`
requires.** A branch's `RunView` gets the same agent dropdown the trunk does,
and `set_agent` refuses on a branch (`PL-TFX5`), so it is a control presenting
itself as working. **Answer: a branch's `RunView` shows the running-agent chip
instead of the dropdown** — the same `setDisabled(locked)`-beside-`setHidden(locked)`
pair `run_view.py` already uses for a running trunk, with
`dashboard_frame.transport` gaining a branch test alongside `is_running`, which
today reads `selector_locked=snapshot.is_running` alone. This is also
`PL-QRD1`'s answer, which is why that item's brief asked for the two to be
decided together.

**The version-number half (B2), which is not this item's but constrains it.**
Bookmarks — `PL-LPLD` and `PL-CTD7` — ship as `v0.4.x` patches rather than
becoming v0.5.0 themselves. That needs no scope surgery: nine of v0.5.0's
entries have already shipped early as patches and stayed on the Required-scope
list, closed against it, and § "The plan" row 5 records each such case. v0.5.0
keeps its name and its Goal and arrives when forking is reachable.

**Three entries stay in v0.5.0 that an earlier reading of this decision would
have moved out.** `PL-B8MK` (a bookmark is a forkable instant), `PL-Z3W6` (the
branch reproduces its parent element-wise) and `PL-W7H9` (what a comparison
asserts) are all forking work, and under B2 forking *is* v0.5.0. None is
deferred.

**Done when** — unchanged, and now executable rather than blocked on an answer:

1. `ROADMAP.md` § "Explicitly out of scope for v0.5.0" names the deferral. Its
   existing third bullet already says "More than two runs displayed at once …
   N branches may exist and be selected between" (line 4399) — that sentence
   now reads as permitting a future the milestone does not build, so it is
   amended to say so outright.
2. The fork-control work is filed as its own item, sized, and added to
   v0.5.0's `Required scope` with the second-fork refusal and the
   running-agent-chip disposition named in its brief.
3. `PL-QRD1` and `PL-W7H9`, both currently `blocked-by: PL-8PSW, PL-XJ37`, are
   re-pointed at that new item, which is what actually makes their hazards
   reachable.

**Recorded rather than executed, and why.** The session that took this decision
reached 331,481 tokens of context against `CLAUDE.md`'s 150,000 handoff budget.
Its rule for a design round past the budget is to externalize and hand off
rather than to spend the remaining edit at low attention on the document that
governs the milestone. Everything above is the externalization; nothing in the
three steps needs the conversation that produced it.

## Executed 2026-09-20: all three steps landed

1. **`ROADMAP.md` § "Explicitly out of scope for v0.5.0" names the deferral.**
   The third bullet read "More than two runs displayed at once. The comparison
   is specified for a trunk and one branch; N branches may exist and be
   selected between", which stated a permitted future as though it were scope.
   It now defers the selector outright, says what that defers with it
   (branch-against-branch comparison, and returning to a branch the learner has
   left), records that it was declined on the educational question rather than
   the technical one, and keeps the one part worth keeping - that adding the
   selector later is additive, because `BranchedCase.branches` returns a stable
   order chosen so a later selector does not renumber the branch a learner is
   looking at.
2. **The fork-control work is `PL-VKJW`** (a learner takes a fork from the
   dashboard: `main()` builds a `BranchedCase`, `SimulationView` gains a run
   added after construction, and a control offers `fork_points_s`), `P2`, `M`,
   `feature, ux`, `scenario-branching`, `ready`. It is the nineteenth entry of
   v0.5.0's `Required scope`, placed after `PL-8PSW`'s overlay entry, which is
   where the dependencies put it - every part of a branch is built by the four
   entries above it and none of them is reachable. The `Required scope` lead
   paragraph's arithmetic moved with it: eighteen to nineteen, and the feature
   group from ten to eleven.
3. **`PL-QRD1` and `PL-W7H9` are re-pointed** at `PL-VKJW`, in place of this
   item, with `PL-8PSW` kept beside it as `PL-JFQ3` left it. Both briefs carry
   a section saying what moved and why.

**The agent-dropdown edge is disposed of** in `PL-VKJW`'s brief and in
`PL-QRD1`'s, per this item's `Done when`: a branch's `RunView` shows the
running-agent chip in place of the dropdown.

**One finding this execution made, recorded rather than fixed here.** The chip
answers the *branch's* selector, where `set_agent` refuses. It does not answer
the *trunk's*, where `set_agent` succeeds: with a branch displayed and the
trunk paused, the trunk's dropdown is live, `RunView._confirm_new_case` asks
only about the control changes it would discard, and after the switch
`assemble_chart_frame` refuses the frame over the shared MAC axis and
`_halt_every_run` fails both runs. `PL-VKJW` is what makes that reachable, so
it cannot be deferred past it. The choice - lock the trunk's selector too, or
keep it live and grow the confirmation dialog a clause about the branches it
orphans - is in `PL-VKJW`'s brief with a recommendation to lock, and is the
project owner's.
