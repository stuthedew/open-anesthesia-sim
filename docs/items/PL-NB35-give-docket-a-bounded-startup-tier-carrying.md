---
id: PL-NB35
title: Give docket a bounded startup tier carrying failed approaches and why they failed
status: untriaged
added: 2026-09-13
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
