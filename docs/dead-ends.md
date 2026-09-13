# Dead ends

Approaches that were tried here, measured, and refuted. One line each, with
the id that carries the full reasoning — `bin/docket show <id>` is the whole
retrieval path.

**The entry lines below are emitted into every session's context at start, and
a `SessionStart` hook's output is resent on every turn** — so they are capped
at 30 entries and 4,000 bytes by `tools/dead_ends.py check`, which `make check`
runs. This preamble is not emitted and not budgeted: it is instructions for
adding an entry, which a session reading the entries never needs.

The cap is the mechanism, not a formality — raise it and you have removed the
thing that works. `tools/dead_ends.py` carries the measurements behind the
numbers. A dead end earns a line only if a session could plausibly propose it
again.

**Edit this file one entry at a time — add one, remove one — and never rewrite
it as a whole.** Those are different operations and only the last is the
failure mode. Monolithic rewriting of an accumulated context is measured:
18,282 tokens to 122 in a single step, accuracy 66.7 to 57.1, while itemized
bullets with *incremental delta updates and periodic de-duplication* beat
rewriting by +10.6% on agent tasks (Agentic Context Engineering,
arXiv:2510.04618). Removing a single stale entry is the de-duplication half of
that prescription, not a violation of it.

**So the cap does not saturate — it is what forces the removal.** Entries are
not permanent: one earns its line only while a session could plausibly propose
the approach again, and an entry whose code, command or design question no
longer exists fails that test and comes out. Hitting the cap means that pass is
overdue, which is why `tools/dead_ends.py check` fails rather than warns. The
observed arrival rate leaves room — the twelve seeded entries are the whole
project's refuted approaches to date, against a cap of thirty — but the
regulator is the admission test, not the headroom.

**What does not belong here.** An item dropped as a duplicate, as superseded,
or as out of scope. Those are ordinary queue outcomes and their `reason:` field
already records them. This file is for an approach whose *premise* was tested
and failed, where the refutation is a fact a future session would otherwise
have to rediscover by building the thing.

## Store and queue design

- **An index, database or manifest committed beside the items** — rejected: anything an index holds is recomputable, and an index is one more thing two branches conflict over. `subprojects/docket/src/docket/store.py`
- **Sequential item ids** — rejected: allocating one is a read-modify-write on shared state, so two branches pick the same number and find out at the merge. `subprojects/docket/src/docket/store.py`
- **One shared queue document** — rejected: it serializes every writer, which is the property one-file-per-item exists to buy. `subprojects/docket/src/docket/model.py`
- **Partitioning closed items out of the live store** — refuted 2026-09-13: the parse is 76 ms of an 830 ms command whose cost is git; no filesystem knee to 100,000 files; and this store is cross-referenced (86.1%, 2,773 edges), which is the shape that stays flat in every comparable record store. `PL-KM3X`
- **Open-backlog ratio as a health measure** — refuted 2026-09-13: the comparison set is multi-contributor projects where an open issue is a promise to a stranger. `PL-03XH`

## Provenance and merge detection

- **`commit:` as closure provenance** — retired: measured over 83 items, 21 hashes resolved, 21 were reachable from nothing, and 41 sat below a shallow clone's horizon. Replaced by `pr`. `PL-T63T`
- **Commit-containment (`git branch --merged`) for in-flight and stranded detection** — rejected: a squash merge contains none of the branch's commits, so every squash-merged branch reads as unmerged forever.
- **Writing `pr` from a CI job fired by the merge** — cannot land: a push made with `GITHUB_TOKEN` starts no workflow, so a protected default branch never sees required checks report. `PL-N5WZ`

## Classification and concurrency

- **`classes`-derived lanes instead of `touches`-derived** — refuted 2026-09-04: put 33 of 145 open items on the wrong side, 18 of them workflow defects that would have gone to a simulator session.
- **Treating a shared file as a concurrency refusal** — refuted 2026-09-06: excluded 27 of Gate 1's 112 open entries, all declaring `docs/MODEL.md`, from every batch. `PL-VRMK`

## Capture and briefs

- **A four-heading empty capture template** — refuted: sessions appended the brief *below* the stub and the checker read the dead stub as the brief. `PL-D188`

## Process claims that did not survive checking

- **Raising the apparatus capture bar on the self-generation rate** — refuted: the count never run came back 67% still-real findings. Name the number and count it before tightening anything. `PL-LKGL`
