---
id: PL-H253
title: Measure session context length as the dominant instruction-adherence variable, and give a session a way to see its own
status: untriaged
added: 2026-09-16
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

`CLAUDE.md` § "Session and tool-use efficiency" already states the rule — "Keep
a session short and scoped to one topic; start a fresh one for an unrelated
topic rather than continuing or compacting a long one". It is being missed by
3×–5×, and nothing surfaces it. A session cannot see its own context usage from
inside; the harness can, through `get_session`.

**Not yet decided.** Whether to give a session that number, and what it should
do with it. Options: a `SessionStart` line stating the budget; a periodic
self-check via `get_session`; `/autocompact` set low enough that compaction is
the signal; or nothing beyond the owner ending sessions sooner. The last is
free and may be sufficient — this is the project owner's working habit, not a
mechanism, and no mechanism should be built before they choose.
