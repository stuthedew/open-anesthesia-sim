---
id: PL-7QKY
title: The working-notes discovery instruction is circular - a session must read the whole file to learn whether its task touches one of its threads
priority: P2
effort: M
status: done
verify: uv run pytest subprojects/docket/tests/test_notes.py subprojects/docket/tests/test_cli.py && grep -q 'def test_show_names_the_notes_threads_that_concern_the_item' subprojects/docket/tests/test_cli.py
classes: defect, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/notes.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_notes.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, docket.toml, docs/WORKING_NOTES.md
added: 2026-09-01
closed: 2026-09-14
---

**Problem.** `docs/WORKING_NOTES.md:17-19` instructs: "Any session working on
this repository should read this file at the start of a task that touches one
of its open threads." The condition cannot be evaluated without doing the
thing it gates. Nothing else names the file either — the session-start digest
reports the queue, the plan and the release state, and `bin/docket next` ranks
items; neither mentions an open thread.

So the instruction resolves in practice to one of two behaviours, and both are
wrong: read the whole file every session (34.5 KB, roughly 8.6k tokens,
against `CLAUDE.md`'s turns-times-context discipline), or read none of it and
lose exactly the cross-session continuity the file exists for.

**Why it matters.** The threads carry measurements and decisions that outlive
their items — the playback-speed thread survives `PL-009` being dropped, and
the scenario-branching thread says outright that its measurements are kept
because a scoped milestone will need them again. Content nothing routes a
session to is content that will be re-derived at full cost, which is the
failure the file was written to prevent.

**Where.** `docs/WORKING_NOTES.md:17-19` is the instruction. The fix is
plausibly not there: the decidable part is *which threads exist and which ids
each concerns*, which a script can read off the `##` headings — every one of
the 52 ids the file cites resolves to a real item file, so the mapping is
already sound enough to key on. A digest or `bin/docket next` line naming the
thread that concerns the item being started would deliver the pointer at the
moment it is needed, at a cost of one line rather than 573.

**Decision (2026-09-01, project owner).** `bin/docket show <id>` carries the
pointer. The reason is the one its own in-flight guard already rests on: an
item named by the project owner skips `bin/docket next` entirely, so `show` is
the path that otherwise has no check on it, and the `docket` skill already
makes it the mandatory pre-start step. The two rejected alternatives, recorded
so they are not re-argued:

- *The session-start digest.* Fires unconditionally, so nothing can miss it —
  but at session start no item has been picked, so it would have to name every
  open thread rather than the relevant one. That is the 573-line read again,
  shortened rather than removed.
- *`bin/docket next`.* Fires only on the sessions that let `next` pick, which
  is the subset `show` already covers and then some.

**Where.** The reading is one pass over `docs/WORKING_NOTES.md`'s `##`
headings, each of which already names the ids its thread concerns; every one
of the 52 ids the file cites resolves to a real item file, so the mapping is
sound enough to key on without parsing prose.

**Do not hardcode the path.** `subprojects/docket/` is a standalone package
with no dependency on this simulator, and it has no notion of a notes file
today — `items_dir` reaches `cli.py` from `config`, and a notes path must
arrive the same way, as a `docket.toml` key with an empty default so a project
without such a file is unaffected. Hardcoding `docs/WORKING_NOTES.md` into the
subproject would be the one change here that is hard to undo.


**Watch for.** Do not solve this by making every session read the file. The
thread-to-id mapping is the cheap half; deciding whether a thread is still
true is not, and must stay with the session.

**Done when.** A session is told which thread concerns the work it is about
to start, without having read the file to find out, and the instruction in
the file states that rather than asking for a judgement it cannot make.

**Done 2026-09-14, on the recorded decision: `bin/docket show <id>` carries the
pointer.**

```
  notes: 2 thread(s) in docs/WORKING_NOTES.md name PL-2FM6
    docs/WORKING_NOTES.md:1187 (about) Measured and answered: a server-rendered chart is not the way out
    docs/WORKING_NOTES.md:1006 (mentions) Decided: no numpy, and the reason is fit rather than dependency avoidance
    Whether a thread is still true is not something this can tell you.
```

**Headings alone were not enough, and the count is what said so.** This brief
proposed reading the `##` headings, on the ground that "every one of the 52 ids
the file cites resolves to a real item file, so the mapping is already sound
enough to key on". Resolvability was the wrong measure. Counted on 2026-09-14:
the file now cites **106** ids and only **31** of them appear in a heading, so
a heading-only reading would have printed nothing for 75 - and silence is
indistinguishable from "no thread concerns your item", which is this defect
rather than a cheaper version of it.

Reading bodies too matches **105 of 106** and does not become noise: 74 ids
reach exactly one thread, 23 reach two, 7 reach three, and one cross-cutting id
(`PL-2FM6`) reaches six. So both are read and the output distinguishes them -
`(about)` where the heading names the id, `(mentions)` where the body does,
`about` first. The distinction is the useful half: it lets a session with a
budget spend one jump on the right thread.

**It points and does not summarize**, which is this brief's "Watch for" honored
rather than worked around. Whether a thread is still true is not derivable from
the file, and a generated precis of a stale thread would be read as current, so
the line is a `file:line` and a title and nothing else - and says so, in the
output, every time.

**Silent in three cases**, all of them "there is nothing to say": no
`notes_file` configured, no such file in this checkout, no thread naming the
id. A line reporting any of them would print on nearly every `show` and change
no decision, which `CLAUDE.md` calls a defect in the check.

**Nothing is hardcoded**, per this brief's own "Do not hardcode the path".
`Config.notes_file` defaults to empty, `subprojects/docket/` has no notion of
`docs/WORKING_NOTES.md`, and a project without such a file sees no change. The
parser is a new `notes.py`, standard-library only, reusing `roadmap.HEADING_RE`
and `store.ID_PATTERN` rather than spelling either a second time.

**The file's own instruction is rewritten**, which is the other half of the
Done-when. It now names the command and states what it asks of a thread's
heading - put the ids the thread is *about* there - so the file's convention is
what feeds the tool. It also carries the current cost: 34.5 KB when this item
was written, **95 KB and 1,603 lines now**, roughly 24k tokens.

**A test was passing vacuously and was caught while writing these.**
`store.ID_ALPHABET` excludes vowels, so the invented `PL-AAAA` in the first
draft of `test_notes.py` matched nothing - the test asserting that preamble
text belongs to no thread passed because the parser could never have parsed
that id, not because the rule held. Every id in the fixture is now spellable,
and the file's docstring says why that matters.
