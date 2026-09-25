---
id: PL-H253
title: Measure session context length as the dominant instruction-adherence variable, and give a session a way to see its own
priority: P2
effort: S
status: done
classes: session-cost
milestone: v0.4.26
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-09-16
closed: 2026-09-16
pr: 622
verify: grep -qF 'at about 150,000 tokens' CLAUDE.md && grep -qF 'context_usage.used_tokens' CLAUDE.md && grep -qF 'session-length cap in' docs/resident-instructions.md && python3 tools/doc_check.py check
---

**Problem.** Instruction adherence in this project is being attributed to
resident-file size, and the measurement does not support it. On 2026-09-16 the
resident set was 52,000 characters over 749 lines — roughly 13,000–15,000
tokens. Concurrent sessions on this repository were running at 263,964,
265,066, 295,446, 328,374, 362,582, 453,340 and 519,237 used tokens against a
1,000,000-token window (`list_sessions`, `external_metadata.context_usage`).

The resident set is therefore 2.5%–5.6% of those contexts. Halving `CLAUDE.md`
— which no rule in `docs/resident-instructions.md` would permit anyway — moves
that share by about one percentage point.

**The threshold, per `.claude/rules/expert-review.md`.** Trimming resident text
is the right primary lever only if resident share is what drives adherence. The
count says it is not: the sessions are 5×–20× the resident set. What the
evidence attributes degradation to is total context length. Attention dilution
scales with input length, with a measured negative correlation between input
length and system-prompt adherence; multi-turn adherence degrades across turns
independently of instruction size
([context degradation](https://www.emergentmind.com/topics/context-degradation-in-large-language-models),
[long-context instruction following](https://aclanthology.org/2026.findings-eacl.254.pdf),
[multi-turn attention loss](https://arxiv.org/pdf/2605.12922)).

**Citation correction, 2026-09-25 (`PL-YJG1`).** The paragraph above
overstates two of its three sources.
- arXiv 2605.12922 (Dongre et al., *When Attention Closes*, May 2026) measures
  *attention to system-prompt tokens* against turn number, in 2B-32B
  open-weight models. It does not measure adherence, and it reports that "some
  models preserve goal-conditioned behavior at vanishing attention".
- The EACL 2026 paper (Robinette et al., *We Are What We Repeatedly Do*,
  Findings of EACL 2026, pp. 4855-4884) says in its abstract that longer
  contexts "pose challenges to system instruction adherence". The abstract
  does not carry "independently of instruction size", and its PDF could not be
  reached to check further.

The conclusion, that total length rather than resident size is the lever,
stands on better sources: Anthropic, *Effective context engineering for AI
agents* (2025), which calls the effect "a performance gradient rather than a
hard cliff"; and Laban P, et al., *LLMs Get Lost In Multi-Turn Conversation*,
arXiv:2505.06120 (2025).

`CLAUDE.md` § "Session and tool-use efficiency" already states the rule — "Keep
a session short and scoped to one topic; start a fresh one for an unrelated
topic rather than continuing or compacting a long one". It is being missed by
3×–5×, and nothing surfaces it. A session cannot see its own context usage from
inside; the harness can, through `get_session`.

**Decided, project owner, 2026-09-16: hand off at about 150,000 tokens, and
build no mechanism for it.** The options put were a `SessionStart` budget line,
a periodic `get_session` self-check, a low `/autocompact`, or nothing beyond
ending sessions sooner. The last was taken.

What landed is the rule and not a mechanism: one sentence in `CLAUDE.md`
§ "Session and tool-use efficiency", naming the number, the one call that reads
it (`get_session`, `external_metadata.context_usage.used_tokens` — confirmed
against a live call, not assumed), and the measurement that makes it the
primary lever. No hook, no script, no polling loop.

**Why the reason is in the rule rather than only here.** Without it the next
session to notice a 444-line `CLAUDE.md` re-derives the trim proposal from
scratch, which is what this pass was. The sentence forecloses it by carrying
its own refutation — 2.5–5.6% — so the objection is answered where it will be
raised.

**Honoured on the spot.** The session that landed this was at 176,689 tokens
when it read its own number, past the cap it was writing, and handed off.
