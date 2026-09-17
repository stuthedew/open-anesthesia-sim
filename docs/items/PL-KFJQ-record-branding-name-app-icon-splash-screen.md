---
id: PL-KFJQ
title: Record branding - name, app icon, splash screen, wordmark - as planned-milestone intent
priority: P3
effort: S
status: done
classes: planning
milestone: v0.4.26
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-16
pr: 614
verify: python3 tools/doc_check.py check && grep -qF 'Decide what this project is called and what it looks like' ROADMAP.md
---

**Problem.** Record branding - name, app icon, splash screen, wordmark - as planned-milestone intent

The project owner raised branding on 2026-09-16 as something to start thinking
about "down the road" - not a change to make now. `.claude/skills/docket/SKILL.md`
routes that shape to one unscoped line of intent in `ROADMAP.md`'s "Planned
milestones" rather than to a queue item: an aspirational feature filed as an `L`
item is work nobody can work, sitting at the bottom of the queue being read past.
This item is the recording act, not the branding work, and closes with it.

**Why it is not folded into an existing item.** Three planned items consume a
branding decision without being the place to make one - item 23 (packaging,
signing and distribution) needs platform bundle icons, item 32 (make the
repository presentable to a first-time visitor) needs the top of the README, and
item 33 (the interface pass) sets the interface's own palette and type, which is
adjacent to an identity and is not one. The section keeps each item to one
improvement so that scoping one does not drag others along, which is the same
reason this gets its own line.

**What the line records beyond the request.** Two constraints a later scoping
round would otherwise have to rediscover. The name is upstream of every other
artefact and is the owner's alone, so it is the first decision rather than one
of several. And a splash screen, if the application has one, is a safety surface
under `CLAUDE.md`'s clinical-output standard rather than decoration: it would be
the last screen before any modelled number, so it is both the least skippable
place for the not-for-clinical-use statement and the place where polish does most
to make a simulator read as a shipped product. Having no splash screen is written
as a legitimate outcome, per `.claude/rules/expert-review.md` on recording the
instance rather than the rule - a fast-launching desktop application has no
reason to hold a user at a logo, which would move the statement to the first real
screen rather than remove it.

**Prior state.** `PL-J7MM` removed the empty branding asset directory on
2026-09-15, the day before this was raised, because it had held one placeholder
file since the bootstrap commit with nothing referencing it. That was right - an
empty directory is not a plan - and this line is where the intent now lives.
