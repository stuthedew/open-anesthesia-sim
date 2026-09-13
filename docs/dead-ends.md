# Dead ends

Approaches that were tried here, measured, and refuted. One line each, with
the id that carries the full reasoning — `bin/docket show <id>` is the whole
retrieval path.

**The entry lines below are emitted into every session's context at start, and
a `SessionStart` hook's output is resent on every turn** — so they are budgeted
at 30 entries and 4,000 bytes by `tools/dead_ends.py`, which `make check` runs.
This preamble is not emitted and not budgeted: it is instructions for adding an
entry, which a session reading the entries never needs. That tool carries the
measurements behind the numbers.

**Edit this file one entry at a time — add one, merge two, remove one — and
never rewrite it as a whole.** Those are different operations and only the last is the
failure mode. Monolithic rewriting of an accumulated context is measured:
18,282 tokens to 122 in a single step, accuracy 66.7 to 57.1, while itemized
bullets with *incremental delta updates and periodic de-duplication* beat
rewriting by +10.6% on agent tasks (Agentic Context Engineering,
arXiv:2510.04618). Removing a single stale entry is the de-duplication half of
that prescription, not a violation of it.

**So the budget does not saturate — it is what forces the removal.** Entries
are not permanent: one earns its line only while a session could plausibly
propose the approach again *without first reading the code that refutes it*. An
entry whose refutation sits in a docstring the session would open anyway, or
whose design question no longer exists, fails that test and comes out.

**Why these are resident rather than grepped on demand.** Not because records
like this go unread — that is a finding about human lessons-learned systems and
its mechanism was tedium, which does not transfer to an agent. What transfers
is that nothing *triggers* a lookup: a test failure announces itself, a dead
end does not. A pointer read at session start does not fix that either, because
the proposal it should stop comes many turns later. A `SessionStart` hook's
output is resent on every turn, so these lines are present at the moment
somebody re-proposes the thing — which is the only moment they are worth
anything.

**Size warns; it never fails the build.** `tools/dead_ends.py` nudges at 80% of
either budget, naming the headroom and the three repairs, so the decision
arrives with slack rather than being forced on whoever trips the cap mid-task.
Going over warns louder and still does not go red — a blocked commit on an
unrelated task is how a session learns to raise the cap, which is the one
repair that is never right. Only a structural fault fails: an entry citing an
id that resolves to nothing, or one wrapped across two lines. Both are
otherwise silent.

**What does not belong here.** An item dropped as a duplicate, as superseded,
or as out of scope. Those are ordinary queue outcomes and their `reason:` field
already records them. This file is for an approach whose *premise* was tested
and failed, where the refutation is a fact a future session would otherwise
have to rediscover by building the thing.

## Store and queue design

- **An index, database or manifest committed beside the items** — rejected: anything an index holds is recomputable, and an index is one more thing two branches conflict over. `subprojects/docket/src/docket/store.py`
- **One shared queue document** — rejected: it serializes every writer, which is the property one-file-per-item exists to buy. `subprojects/docket/src/docket/model.py`
- **Partitioning closed items out of the live store** — refuted 2026-09-13: the parse is 76 ms of an 830 ms command whose cost is git; no filesystem knee to 100,000 files; and this store is cross-referenced (86.1%, 2,773 edges), which is the shape that stays flat in every comparable record store. `PL-KM3X`
- **Open-backlog ratio as a health measure** — refuted 2026-09-13: the comparison set is multi-contributor projects where an open issue is a promise to a stranger. `PL-03XH`

## Provenance and merge detection

- **Commit-containment (`git branch --merged`) for in-flight and stranded detection** — rejected: a squash merge contains none of the branch's commits, so every squash-merged branch reads as unmerged forever.
- **Writing `pr` from a CI job fired by the merge** — cannot land: a push made with `GITHUB_TOKEN` starts no workflow, so a protected default branch never sees required checks report. `PL-N5WZ`

## Classification and concurrency

- **`classes`-derived lanes instead of `touches`-derived** — refuted 2026-09-04: put 33 of 145 open items on the wrong side, 18 of them workflow defects that would have gone to a simulator session.
- **Treating a shared file as a concurrency refusal** — refuted 2026-09-06: excluded 27 of Gate 1's 112 open entries, all declaring `docs/MODEL.md`, from every batch. `PL-VRMK`

## Process claims that did not survive checking

- **Raising the apparatus capture bar on the self-generation rate** — refuted: the count never run came back 67% still-real findings. Name the number and count it before tightening anything. `PL-LKGL`
