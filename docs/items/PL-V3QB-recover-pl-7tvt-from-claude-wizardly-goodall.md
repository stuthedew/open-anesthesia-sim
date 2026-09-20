---
id: PL-V3QB
title: Recover PL-7TVT from claude/wizardly-goodall-p5ltid, whose session archived with no pull request, leaving the capture readable only on an unmerged branch ref
priority: P2
effort: S
status: done
classes: housekeeping
touches: docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 765
payoff: puts PL-7TVT's finding back where every session can read it, instead of only on an archived session's branch ref that the next prune would have taken
verify: grep -q '^id: PL-7TVT' docs/items/PL-7TVT-bin-docket-flight-separates-a-live-session-from.md
---

**Problem.** Recover PL-7TVT from claude/wizardly-goodall-p5ltid, whose session archived with no pull request, leaving the capture readable only on an unmerged branch ref

**Recovered, 2026-09-20** (`PL-8G48`). The file was restored with `git checkout
origin/claude/wizardly-goodall-p5ltid -- docs/items/PL-7TVT-bin-docket-flight-separates-a-live-session-from.md`,
off the archived session's branch, which carried no pull request and so would
never have merged. `PL-7TVT` arrives here still `untriaged`, which is the state
it was captured in; triaging it is not this item's work.
