---
id: PL-WP3Z
title: docs/maintainer.md keeps 'the compaction rule' only in the Projects instructions and also gives the /compact practice (PL-YJG1); say whether they are one rule, which would then stand in two places (copy editor structure read, 2026-11-07)
priority: P3
effort: S
status: done
classes: docs
feature: maintainer-guide-structure
touches: docs/maintainer.md, .claude/skills/docket/modes/start.md
deferred-from: v0.7.0 - a new problem, not present at the freeze: the sentence that the compaction rule lives only in the instructions arrived in ec9eeb8d (PL-NZC0)
added: 2026-11-07
closed: 2026-11-11
pr: 2097
payoff: the compaction rule has one home, and a thread and its coordinator follow the same version of it
not-delegable: the compaction rule's current text is in the Project's instructions, which only the owner or the Project's coordinator can read
reenters: PL-PDVF
---

**Problem.** docs/maintainer.md keeps 'the compaction rule' only in the Projects instructions and also gives the /compact practice (PL-YJG1); say whether they are one rule, which would then stand in two places (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** `docs/maintainer.md` § "Rules for sessions live in the repository" still says the compaction rule is "the one rule that lives only in the instructions", and § "Settings that make sessions cheaper" still gives the `/compact` practice (`PL-YJG1`). `.claude/skills/docket/modes/start.md` also states what a Projects thread does instead of `/compact`, citing "the Projects trial's instructions, read 2026-10-03". The repository does not hold the instructions' current text, so no file shows what the compaction rule says.

**Why it matters.** If the compaction rule and `start.md`'s rule for threads are one rule, it stands in two places that can drift, against the owner's word that it lives only in the instructions. If they differ, a thread follows one and the coordinator expects the other.

**Done when.** The compaction rule's current text in the Project's instructions has been compared with `start.md` and with § "Settings that make sessions cheaper", and `docs/maintainer.md` says in one clause what the compaction rule covers. Where the repository holds a copy, both are reported to the owner, as § "Rules for sessions live in the repository" says for a rule held in both places.

**Generator check.** An instance of `PL-PDVF`'s fact (the owner's current rules for sessions, as the Project's instructions and the repository hold them), filed after that head closed on 2026-10-03.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, no file outside the item store named the compaction rule. The sentence that it lives only in the instructions arrived in ec9eeb8d (`PL-NZC0`, #1799, 2026-10-25), after the freeze, so this is a new problem and is deferred.

**Done 2026-11-11.** The coordinator quoted the compaction rule from the Project's instructions on 2026-11-11 at 00:25Z. It is dated 2026-10-04 17:33Z, and the instructions say, by the owner's word of 2026-10-04 17:38Z, that it lives only there and never in the repository.

- **`.claude/skills/docket/modes/start.md` held an older copy**, taken from the instructions as read on 2026-10-03 (`PL-PDVF`). It disagreed with the current rule about what a thread does at its context budget. Since the owner's word puts the rule only in the instructions, the copy is replaced by a pointer to the instructions. Both texts went to the owner in the thread's reply.
- **§ "Settings that make sessions cheaper"** gives the `/compact` practice for the owner's own sessions, which the compaction rule does not cover. They are two rules, and `docs/maintainer.md` § "Rules for sessions live in the repository" now says in one clause what each covers.
- **`.claude/skills/docket/modes/coordinator.md`** names where the rule lives without restating it, so it is unchanged.
