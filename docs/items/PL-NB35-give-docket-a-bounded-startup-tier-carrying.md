---
id: PL-NB35
title: Give docket a bounded startup tier carrying failed approaches and why they failed
status: done
added: 2026-09-13
closed: 2026-09-13
priority: P2
effort: M
classes: infra
feature: worker-instructions
touches: docs/dead-ends.md, tools/dead_ends.py, .claude/hooks/docket-digest.sh, Makefile, docket.toml, docs/ARCHITECTURE.md, tests/unit/test_dead_ends.py
verify: python3 tools/dead_ends.py check && grep -q 'dead_ends.py" emit' .claude/hooks/docket-digest.sh
---

**Problem.** Every reference design for memoryless multi-session work splits
state on one axis - what enters context at session start versus what is fetched
on demand - and bounds the first tier hard. docket has no startup tier. The
session-start digest is the nearest thing and it reports queue state, not
rationale. The 1,836-line `subprojects/docket/README.md` holds the single
highest-value artifact this project has produced - a list of design alternatives
that were tried, measured and rejected, with the numbers - and nothing loads it.

**Why it matters.** This is where the measured harm actually is, and it is not
on disk.

- Curation policy, not store size, drives agent accuracy: add-all memory reached
  13.04% accuracy over 2,411 records where strict selective addition reached
  38.86% over 1,012 - a 3x difference from policy alone (Xu et al., "How Memory
  Management Impacts LLM Agents", ACL 2026, arXiv:2505.16067).
- Irrelevant material in context costs more than any retrieval choice: a focused
  ~300-token prompt beat the full ~113,000-token prompt by 30-60 points on
  identical LongMemEval questions across 18 models (Hong, Troynikov, Huber,
  "Context Rot", Chroma, 2025-07-14).
- Position alone moves accuracy >20 points and can fall below closed-book
  (Liu et al., "Lost in the Middle", TACL 2024;12:157-173).
- Anthropic's largest published memoryless-multi-session project - ~2,000
  sessions, a 100,000-line C compiler - carried its state in one progress file
  and explicitly recorded failed approaches "because without them, successive
  sessions will re-attempt the same dead ends".
- The documented budget is small and hard: MEMORY.md loads the first 200 lines
  or 25 KB, whichever comes first; everything past it is silently dropped; topic
  files are never loaded at startup.

**Build it as itemized deltas, never as a periodic rewrite.** Monolithic
rewriting of an accumulated context caused measured collapse - 18,282 tokens to
122 in one step, accuracy 66.7 to 57.1 - while itemized bullets with incremental
delta updates and periodic de-duplication beat rewriting by +10.6% on agent
tasks (Agentic Context Engineering, Stanford/SambaNova/UC Berkeley, 2025-10,
arXiv:2510.04618). This is also an argument for keeping one file per item rather
than consolidating: the per-item structure already is the itemized form.

**Watch out.** Empirical ADR work finds the rationale sections - decision drivers
and considered options - are "absent or misused in most ADRs". The value here is
entirely in the rejected alternative and the measurement that killed it, which
is exactly what the README's rejected-alternatives list already has and what a
bare decision record would not.

**Done when.** A session starts with a bounded, line-capped tier naming the
approaches already tried and refuted, and the retrieval path to the full record
is one command rather than one traversal.

**Decision needed — the mechanism is built and green, and it has an eviction
hole the project owner has been asked to close (2026-09-13).**

What is built: `docs/dead-ends.md`, emitted at session start by
`.claude/hooks/docket-digest.sh` through `tools/dead_ends.py emit`, capped at
30 entries and 4,000 bytes of *emitted* text by `tools/dead_ends.py check` in
`make check`, with 12 seeded entries at 2,521 bytes and tests in
`tests/unit/test_dead_ends.py`.

What is missing is a curation policy. The cap is an eviction trigger with no
rule behind it: at 30 entries `make check` goes red and whoever trips it drops
something, mid-task, with no evidence about which entry has ever been worth
anything. A high-yield entry - the `GITHUB_TOKEN` one, which otherwise costs a
session a CI cycle to rediscover - is indistinguishable from a stale one to a
session scanning for something to cut. That is the same failure the evidence
behind this item names: curation policy, not store size, drove the threefold
accuracy difference in Xu et al.

**The proposal.** Each entry names its own expiry condition, carried in the
cited item rather than in the emitted line, so it costs the always-loaded half
nothing:

    stale-when: src/anesthesia_sim/app/ no longer exists
    stale-when: docket no longer stores items as files
    stale-when: never - the constraint is GitHub's, not ours

`dead_ends.py check` resolves the path-shaped and item-shaped conditions
deterministically and reports candidates *with evidence*; the `never` case is
explicit, which is what defends a high-yield entry. The cap then becomes a
review trigger - red means the expiry pass is overdue - rather than an
eviction trigger. This is `CLAUDE.md`'s decidable/judgment split: the tool
never decides whether an approach could recur, and the person who refuted it
writes down what would make it moot at the one moment anybody has that context.

**The second question, which is the owner's and not this session's:** whether
an entry carrying no expiry condition is refused or merely flagged. Refusing
keeps the list honest; flagging lets a session record a dead end at the moment
it finds one without stopping to work out what would make it moot. This session
leans flagging, on the same ground that capture is cheap everywhere else here.

**Until that is answered the entries stand and the cap holds.** The list is at
12 of 30, so nothing is forced.

**Decision taken, 2026-09-13 (project owner).** Three changes, all landed.

1. **`stale-when` per-entry expiry conditions: withdrawn before building.** The
   closest production analogue does not do it. Anthropic's own always-loaded
   index warns *near* its limit and names three repairs - "keep one line per
   entry, move detail into topic files, and merge or drop stale entries" -
   rather than carrying an expiry language per entry. Building one here would
   have been more machinery than the field uses, against `CLAUDE.md`'s rule
   that where the benefit is unclear the answer is no.
2. **Size warns; it never fails the build.** `budget()` nudges at 80% of either
   budget so the decision arrives with slack, and warns louder over it. Only a
   structural fault - a dangling id, a wrapped entry - fails, because both are
   silent otherwise. A red gate on an unrelated commit is how a session learns
   to raise the cap, which is the one repair that is never right.
3. **Entries cut from 12 to 9**, on a sharpened admission test: an entry earns
   its line only while a session could plausibly propose the approach again
   *without first reading the code that refutes it*. Dropped were sequential
   item ids and the four-heading capture template (a session would be refuted
   by `store.py` and by the template's absence), and `commit:` as closure
   provenance (superseded by `pr` and documented where a session would meet
   it). Emitted text is now 1,961 bytes. Reversing any cut is one line.

**What the primary source actually says, since it corrected the record.** The C
compiler post prescribes "extensive READMEs and progress files" with no cap and
no curation policy, and its failed-approaches doc is emergent and per-bug -
"when stuck on a bug, Claude will often maintain a running doc of failed
approaches and remaining tasks". Its context lesson runs the other way from
this design: log detail to a file and make it greppable, rather than pushing it
into context. The counterweight is narrower than the one first
offered here, and the correction matters. NASA's LLIS - audited 2012, neither
searched nor contributed to outside JPL over five years - is a *human* system,
and its failure mechanism was tedium, which does not transfer: an agent does
not get bored of `grep`. What transfers is that nothing triggers a lookup. A
test failure announces itself, which is why the compiler harness's greppable
log works; a dead end announces nothing, and a pointer read at session start is
no help because the proposal it should stop arrives many turns later. A
`SessionStart` hook's output is resent on every turn, so the entries are
present at the moment of the proposal. That property, not the LLIS analogy, is
what the 1,961 bytes buy.
