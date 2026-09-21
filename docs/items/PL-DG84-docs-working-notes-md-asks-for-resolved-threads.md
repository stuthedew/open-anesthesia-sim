---
id: PL-DG84
title: docs/WORKING_NOTES.md asks for resolved threads to be deleted and nothing reads that policy
priority: P2
effort: M
status: done
classes: docs, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/notes.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_notes.py, subprojects/docket/README.md, docs/WORKING_NOTES.md
added: 2026-09-13
closed: 2026-09-21
verify: uv run pytest subprojects/docket/tests/test_checks.py subprojects/docket/tests/test_notes.py -k "stale_open_thread or declares_open or cites" -q
---

**Problem.** docs/WORKING_NOTES.md asks for resolved threads to be deleted and nothing reads that policy

**Notes.** `docs/WORKING_NOTES.md`'s own header states the policy: "When a
thread here is fully resolved (implemented, tested, and merged), its outcome
belongs in `ROADMAP.md`/`docs/MODEL.md`/commit history as appropriate, and its
entry here should be deleted rather than left stale." Nothing reads it. The file
is 93 KB over 1,536 lines with no archive and no length check, and roughly eight
of its twenty-one sections lead with a settled status word (`Settled:`,
`Decided:`, `Measured and answered:`, `Built and measured:`).

This is the systemic item; the instances are already filed one thread at a time,
which is the evidence that the policy has no reader: `PL-5748` (the PL-009
playback thread states a pre-`PL-010` frame cost as current), `PL-60CQ` (the
PL-024 entry states a venous pool of 1.0 L that `PL-8ZJQ` replaced with
1.222 L), `PL-BHJW` (says `rules_paths_check.py` is wired into CI's floor job,
which `PL-D551` folded away), `PL-C92D` (a Flet frame table measuring a tree that
no longer exists), and `PL-75R0` (a thread headed "Open: the repository has no
README" a week after `PL-N092` shipped one). All five are individually true and
none of them stops the sixth.

`PL-7QKY` is the adjacent decided question — discovery rather than deletion — and
its brief establishes the parse any mechanism here would need: every one of the
ids this file cites resolves to a real item file. `PL-6ZQY` is the same claim
applied to the queue rather than to this file, with 43 of 134 open items measured
dead or overstated.

**Where.** `docs/WORKING_NOTES.md`; a carrier to be decided at triage —
`tools/doc_check.py`'s `candidates` mode is the candidate that already runs at
close-out and could name a thread all of whose cited ids have closed, but a
one-off pruning pass may be the honest answer instead. Do not build a check that
fires every run without changing a decision.

**Why it matters.** The file exists "so that a new conversation can pick up
context without re-deriving it", so a stale thread in it is not merely unread -
it is read and acted on. `PL-75R0` is the sharp case: a thread headed "Open: the
repository has no README" a week after one shipped. The five filed instances are
each individually true and none of them stops the sixth, which is what makes this
the systemic item rather than a sixth instance.

**Decision needed.** Which carrier, and the question is whether anything here
should run every time. Three candidates, and they are not equivalent:

- **A `tools/doc_check.py` `candidates`-mode line.** It already runs at
  close-out, and it could name a thread all of whose cited `PL-` ids have closed.
  `PL-7QKY`'s brief establishes the parse: every one of the ids this file cites
  resolves to a real item file. The risk is `CLAUDE.md`'s own retirement test - a
  thread can legitimately outlive its items, which is one of the three things the
  file's header says belongs in it, so this would fire on correct content and
  train a session to skim it.
- **A grooming advisory**, alongside the existing ones, so it surfaces on a pass
  that is already about queue hygiene rather than on every close-out.
- **A one-off pruning pass and no mechanism at all**, on the ground that the
  decidable half here is small and the judgment half - whether a thread still
  earns its place - is the whole of it.

The answer rests on a rule this repository already states rather than on what the
project is for, so it is a session's to settle with the counts in front of it,
not the owner's. What it must not become is a check that fires every run without
changing a decision.

**Done when.** The carrier above is chosen and recorded here with its reasoning,
and either it is built or the item says why no mechanism earns its place - and in
either case `docs/WORKING_NOTES.md` no longer carries a thread whose every cited
id has closed.

**Found.** 2026-09-13, reviewing an outside article on long AI projects against
this repository.

## Measured 2026-09-21, while closing `PL-4HKS`: the three candidates are not close

`PL-4HKS` was the sixth instance to be resolved by hand (the playback-speed
thread, deleted rather than re-headed). Closing it gave the count this item's
decision needs, so it is recorded here rather than left to be re-derived.
**Recommendation: the grooming advisory, on the narrow signal below.** The
project owner decides; the numbers are what the recommendation rests on.

**The signal this item proposed fires on 16 of 26 sections.** Candidates-mode
was to name "a thread all of whose cited `PL-` ids have closed". Run against
the file as it stands, that is **16 of its 26 `##` sections**, and most are
correct content: § "Decided: no numpy" is kept deliberately because the
question recurs and says so in its own text; § "Decided: control resolution is
not what the interface promised at speed" is the live authority `PL-4HKS`'s
deletion just pointed at; § "Settled: when a session may fix a small finding"
is what `CLAUDE.md`'s resident fix-now rule cites. A check naming those every
run is `CLAUDE.md`'s retirement test met before the check is built.

**Narrowing it by the heading's own status word takes it to 4, and 3 are
right.** Require *both* that the heading declares the thread open and that
every id it cites has closed:

| Section | Verdict |
| --- | --- |
| `## Open thread: scenario branching, bookmarks, and what a snapshot is for` | stale - `PL-DL4M` |
| `## Open thread: which moment a rule has to reach` | stale - `PL-DL4M` |
| `## Open: the repository has no README` | stale - `PL-75R0` |
| `## Open thread: what makes desflurane wash out too fast` | **legitimately open** |

So precision is 3 of 4 on the narrow signal against roughly 3 of 16 on the
loose one, and the two filed instances it recovers are exactly the ones
sessions have been filing one at a time.

**The fourth row is the load-bearing one, and it decides the carrier.** The
desflurane thread's three items (`PL-W21J`, `PL-73G7`, `PL-RFLN`) are all
closed and the thread is still open: "what is left is the published value
itself, which nothing this project runs can settle." That is the file
preamble's third membership test - a thread *having no item at all* - so this
false fire is not a bug to be tuned out. It is permanent, and it means the
signal can never be a hard `make check` failure.

**Which leaves the advisory, and rules out both neighbours.** Candidates-mode
runs at every close-out, where a permanent false fire trains a reader to skim
the block a real advisory shares (`PL-HJZW` is what that costs). A one-off
pruning pass leaves nothing behind, and this file has now generated six
instances, so the seventh is a question of when rather than whether. A
grooming advisory fires on a pass that is already about hygiene, prints four
lines against this file, and one of those four is a judgment a reader makes in
seconds because the thread's own last paragraph says it is open.

**What stays a judgment either way.** Whether the outcome is recorded somewhere
that maintains itself. `PL-4HKS` was deletable only because `ROADMAP.md` item
25 carries the shipped feature, `docs/MODEL.md` § "Supported simulation step"
carries the step, and `tests/benchmarks/frame_cost.py` re-measures the frame in
three seconds. No check can decide that, and it is the whole of the work.

## Decided 2026-09-21 - the grooming advisory, on the narrow signal

**Ratified by the project owner, 2026-09-21**, over the two neighbours this
brief named beside it: the `tools/doc_check.py` `candidates`-mode line that
would run at every close-out, and the one-off pruning pass with no mechanism at
all. So the bar to reopen it is **ordinary evidence** rather than a compelling
argument, per `CLAUDE.md` § "Working with the project owner" - a measurement, a
cost the case did not carry, or a constraint that has since appeared is enough
to put it back to them. It was this session's recommendation, agreed on one
read, which is not the same as a decision they authored.

**What is to be built.** One grooming advisory naming each `##` section of
`docs/WORKING_NOTES.md` where **both** hold:

1. the heading's own status word says the thread is open - it begins `Open`
   (`Open thread:` or `Open:`), as against `Settled:`, `Decided:`, `Measured`,
   `Built`, `Shelved`, `Aspirational` or `Long-term`; and
2. every `PL-` id the section cites, heading and body alike, resolves to an
   item whose status is `done` or `dropped`.

A section citing no id at all is **not** named: two exist today
(§ "Aspirational: power-user custom agents", § "Long-term vision") and both are
direction with no item, which the file's preamble sanctions outright.

**Where.** `subprojects/docket/src/docket/checks.py`, in `_groom`, which is
where the other grooming advisories are produced and which already holds the
store and the config. The file is `docket.toml`'s `notes_file`, so the path is
read from config rather than written in. A test beside the others in
`subprojects/docket/tests/test_checks.py`.

**Why not the other two, in the numbers rather than the argument** (measured
2026-09-21 while closing `PL-4HKS`; the section above carries the full table):
clause 2 alone fires on **16 of 26** sections, most of them correct content
that other rules cite; clause 1 plus clause 2 fires on **4**, of which **3** are
the already-filed instances. The fourth is § "Open thread: what makes
desflurane wash out too fast", whose three items are all closed and which is
genuinely open - *"what is left is the published value itself, which nothing
this project runs can settle."* That false fire is **permanent**, being the
preamble's own third membership test, which is what rules out a hard failure
and rules out close-out candidates mode with it: a permanent false fire at
every close-out trains a reader to skim the block a real advisory shares. The
one-off pass leaves nothing behind, and this file has now generated six
instances.

**Done when.** The advisory exists, fires on the four sections above and on no
other, names the section by heading, and is reachable from `make docket`; a
test pins both clauses, including that the desflurane section is named (it
satisfies the rule) and that the two no-id sections are not.

**What stays a judgment, deliberately.** Whether the outcome is recorded
somewhere that maintains itself, which is the whole of the work a named section
then needs. `PL-4HKS` was deletable only because `ROADMAP.md` item 25 carries
the shipped feature, `docs/MODEL.md` § "Supported simulation step" carries the
step and `tests/benchmarks/frame_cost.py` re-measures the frame. No check
decides that, and none should try.

## Built 2026-09-21 - the advisory, and what it names on the file today

**What landed.** `_check_stale_open_threads` in
`subprojects/docket/src/docket/checks.py`, called from `_groom` as the ratified
decision places it, raising **one** advisory line that names each `##` section
satisfying both clauses, with its heading and its line number. The parsed
threads reach `analyze` as a new `threads` input, gathered once in `cli.py`'s
`_complete_report` from `docket.toml`'s `notes_file` - the same route every
other unreadable-from-store input takes, so `check`, `digest` and `next` all
count it and none of them prints a number another would contradict. A project
configuring no `notes_file` hands `None` and the question goes unasked.

**Where the heading half lives, and why it is not in `_groom`.** `Thread.
declares_open` and `Thread.cites` are in `subprojects/docket/src/docket/notes.py`,
beside the parse they belong to: which leading word means "open" is a fact about
the notes-file convention, and `notes.py` is the module that already owns
headings. `_groom` holds the decision, which is what the ratified `Where`
names. `touches` gained `notes.py`, `cli.py`, `test_notes.py` and the package
README to match what the work actually reached.

**What it names on `docs/WORKING_NOTES.md` today.** Three sections, all of them
already filed: § "Open thread: scenario branching..." and § "Open thread: which
moment a rule has to reach..." (`PL-DL4M`, in flight as this closed) and
§ "Open: the repository has no README" (`PL-75R0`). The fourth the brief
predicted - § "Open thread: what makes desflurane wash out too fast" - is
silent for now only because a note added to that thread cites this item, which
was open while it was being written; it returns to the list with this closure,
which is correct and is what the permanent-false-fire argument says should
happen. That note now states in the thread itself why the advisory names it, so
the next groomer reads the answer instead of re-deriving it.

**The deletions are not this item's.** The original `Done when.` asked that the
file no longer carry such a thread; the ratified decision replaced it with the
mechanism, and the three live instances belong to `PL-DL4M` and `PL-75R0`,
which are `ready` and hold the judgment about what each thread's outcome is
recorded against. Closing those is what takes the advisory to the one permanent
false fire.

**The file's header now carries the convention the check reads.** An open
thread heads `Open thread:` / `Open:` and a resolved one says what it resolved
to; a live thread headed anything else is one this advisory can never name.
That was implicit before and is now stated where a writer meets it, since the
signal is only as good as the heading discipline behind it.

**Not built, deliberately:** no deletion, no archive, no length check, and no
close-out candidates line. The first three were never this item's question; the
fourth is the neighbour the decision ruled out.
