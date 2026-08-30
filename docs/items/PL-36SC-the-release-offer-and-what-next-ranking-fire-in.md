---
id: PL-36SC
title: The release offer and 'what next' ranking fire in topic-specific discussions, where they read as noise
status: untriaged
feature: worker-instructions
touches: CLAUDE.md, .claude/skills/docket/SKILL.md
added: 2026-08-30
---

**Problem.** `CLAUDE.md`'s "Offer the release; do not wait to be asked" and the
docket skill's "Open with where the release stands" are written for the
question "what should we work on next". Nothing scopes them to it, so a session
in a narrow topic-specific discussion - one that never ran that workflow - ends
its reply with a release offer and a next-item ranking that have nothing to do
with what was being discussed. The project owner raised this directly: in a
side discussion, recommend only what is relevant to it, whether that is the
discussion's own next step or an existing item that would fix or unblock what
was found. Not an unrelated ranking.

**Why it matters.** The closing block exists so the genuinely actionable lines
are seen. Padding it with items the reply never discussed is the same failure
as the parked items the "Every line must be actionable now" rule already
forbids: the reader skims past the real actions along with the filler. It also
misreads the mode - offering a release in the middle of a design conversation
converts ideation into implementation, which `CLAUDE.md` says not to do
silently.

**Where.** `CLAUDE.md`'s "Offer the release" bullet and the docket skill's
"Mode: recommend what to work on" and "Mode: ship a release" sections.

**Note the recency.** `6f56aac` strengthened the release-opening rule two
commits before this was filed, on evidence from testing a genuine "what should
we work on next" session. That evidence stands and the rule is right for that
mode. What is missing is the scope line saying which mode it belongs to, so
fixing this must not weaken it where it applies.

**Done when.** Both documents scope the release offer and the item ranking to
sessions actually answering "what next", and say what a topic-specific
discussion should close with instead.
