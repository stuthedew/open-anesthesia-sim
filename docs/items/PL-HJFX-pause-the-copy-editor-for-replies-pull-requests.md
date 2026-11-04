---
id: PL-HJFX
title: Pause the copy editor for replies, pull requests and close-out until PL-HGZS is fixed and the owner agrees to bring it back; use it only to test or debug it
priority: P1
effort: S
status: done
classes: housekeeping
feature: prose-quality
milestone: v0.6.15
touches: .claude/rules/instruction-writing.md, .claude/skills/pull-request/SKILL.md, .claude/skills/docket/modes/close-out.md, docket.toml, tests/unit/test_new_prose.py
deferred-from: v0.7.0 - a workflow change the owner ordered, closed in the change that files it
added: 2026-11-04
closed: 2026-11-04
pr: 2033
payoff: no reply, pull request or branch waits on a copy editor that passes verbose text
verify: grep -qF 'THE COPY EDITOR IS PAUSED' .claude/rules/instruction-writing.md
---

**Problem.** Pause the copy editor for replies, pull requests and close-out until PL-HGZS is fixed and the owner agrees to bring it back; use it only to test or debug it

**Why it matters.** The copy editor passed, and lengthened, every text the owner judged too verbose on 2026-11-04 (`PL-HGZS`). Each run cost minutes and its result was used as proof that the text was plain.

**Decision** (project owner, 2026-11-04): "Pause using the copy editor in prod except for testing and debugging purposes until verified to be working (generator fixed and I agree to reintroduce)."

**Done when.** Rule 16 of `.claude/rules/instruction-writing.md`, the pull-request skill and close-out step 8 say the copy editor is paused, and `docket.toml`'s `prose_count_command` is empty, so `bin/docket arm` holds no branch for a missing copy edit. Reintroducing it is a separate change, made only after `PL-HGZS` closes and the owner agrees.

**Generator check.** A response to `PL-HGZS`, not a member: it stops sessions relying on the copy editor while that head is fixed.
