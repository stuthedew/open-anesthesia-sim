---
id: PL-2CPD
title: During product focus the session-start digest still leads with the bare next pick, a workflow generator item, so a product session that follows its Top line is handed apparatus work; only the docket skill's text routes it to the By lane product entry
status: untriaged
feature: workflow-stress-2026-09
touches: subprojects/docket/src/docket/render.py
added: 2026-09-25
---

**Problem.** During product focus the session-start digest still leads with the bare next pick, a workflow generator item, so a product session that follows its Top line is handed apparatus work; only the docket skill's text routes it to the By lane product entry

**Found** while writing `PL-2866`'s text, 2026-09-25. The digest's `Top:` line is `next` with no lane, so under product focus it names whatever ranks first overall - on the day of the switch, `PL-FX5Q`, a workflow item ranked above every band as a generator's blocker. `.claude/skills/docket/SKILL.md`'s Implementation paragraph now tells a product session to take the `By lane` line's product entry instead, but that holds only once the skill has loaded, and the digest is read at launch. `PL-NZC0`'s fallback, if the trial fails its bar, makes the digest's top line the pick; if the trial passes, nothing changes this line. Captured, not built: it is a new mechanism under the generator pause.
