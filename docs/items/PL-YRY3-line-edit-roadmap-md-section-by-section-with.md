---
id: PL-YRY3
title: Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed

**Why it waits.** The project owner put structure ahead of every line edit (2026-11-07, over keeping restructures for later): no document is line edited before its structure read's findings are applied. `ROADMAP.md`'s restructure lands in nine slices, `PL-W0TS` to `PL-4BCF`. The repository's remaining copy edits wait until the copy editor no longer drops requirements, qualifiers and reasons (`PL-F0Q2`, project owner, 2026-11-07, ratified, over continuing with an audit of each document).

**How.** Run `python3 tools/copy_edit.py --sections ROADMAP.md`, as `docs/prose-review/README.md` § "Reviewing a whole document" step 3 says. Audit each edited section against the text before it for dropped statements, qualifiers, requirements and reasons, as `PL-95SW` did for `docs/MODEL.md`. Then close-out step 8 is satisfied for every slice's changed passages. The run planned on the owner's Mac on 2026-11-05 left out the frozen lists and § "Current baseline". Decide again whether to: a frozen list is a snapshot of what the gate held, and each release cut rewrites the baseline.

**Done when.** Each section of `ROADMAP.md` has been line edited and audited, and each statement the edit dropped is restored or recorded with its reason.

**Left for this line edit by slice 2 (`PL-P0C5`), 2026-11-07.** Each needs a
sentence reworded or a term chosen, which a move-only slice does not do. The
row numbers are `ROADMAP.md` at `aff76df1`; find each passage by its words.

1. Choose one word for the cadence's four stages and define it where the list
   starts. The list's own text says "beats", and other passages say "steps",
   while "step" also names the simulation step and the timeline's `Step`
   column.
2. Call the snapshot rule by its heading's name everywhere. It is also called
   "the presence rule", "the presence test", "the snapshot rule" and "the
   presumption".
3. In § "What counts", fold the `infra` example (`uv.lock` left stale is a
   defect, release tagging is not) into the process-work paragraph.
4. In § "Which findings re-enter the gate", cut the second "The gate tests when
   a problem was present, not when it was discovered", which repeats the
   section's opening, and reword the sentence after it to stand alone.
5. Date or cut "while Gate 2 does" in § "How gate work is released".
6. Cut the two "is why this rule is written down rather than left to imitation"
   sentences in § "Writing a milestone entry", keeping each id as a pointer.
7. Define, or replace with plain words, the terms the chapter read found
   undefined: "the store", "release train", "places" and "takes", "promoted",
   "grooming pass", "capture rule", "fails closed", the `verify:` field, and
   what `bin/docket` is.
8. Date each undated figure: "12 of 134 open items dead and 31 more
   overtaken", "thirteen items in one session generated fourteen new ones",
   and "Gate 2's 190".
9. Give an example of the wording that draws the exclusion warning. The phrases
   are `SCOPE_EXCLUSION_MARKERS` in `tools/doc_check.py`.
10. Name the release and the saving in "the saving the release exists to
    deliver".
11. Say what each subsection of a milestone entry holds (Goal, Required scope,
    Definition of done, Explicitly out of scope), in § "Writing a milestone
    entry".
12. Cut the narration about the text itself that the moves left behind.

**From `PL-DWGC` part 1 (2026-11-07).** Eight version-table rows keep a first
sentence that does not say what the release changed: v0.2.9, v0.3.4, v0.3.5
and v0.4.1 say only what did not change, and v0.3.8, v0.3.9, v0.4.4 ("**The
code is the model.**") and v0.4.5 ("**Going public, finished.**") are too
general to tell. Each needs a sentence on what changed for a learner, taken
from the rest of its row in the item the Details cell names. v0.4.4 comes
first: its row no longer shows that a displayed value moved in that release,
because the operator split was replaced by an exact step. Four rows also still
run past 600 characters as one sentence (v0.6.12 to v0.6.15).

