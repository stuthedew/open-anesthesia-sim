---
id: PL-XJV3
title: docs/maintainer.md's model choice is dated 2026-09-19 and names Fable 5.1, Opus 5, Sonnet 5 and Haiku 4.5 but not Opus 5.5, Sonnet 5.5 or Haiku 5.5, so its strongest-model and delegable answers and its three reasons against Haiku may no longer hold; the owner moved hard work to Opus 5.5 on 2026-10-14 (found in PL-KLN5)
priority: P2
effort: S
status: ready
classes: docs
feature: model-evidence
touches: docs/maintainer.md
added: 2026-10-17
payoff: the owner and sessions choose models for hard and delegated work from the current model list, not from one a generation old
verify: ! grep -qF 'As of 2026-09-19 the strongest available model' docs/maintainer.md
---

**Problem.** docs/maintainer.md's model choice is dated 2026-09-19 and names Fable 5.1, Opus 5, Sonnet 5 and Haiku 4.5 but not Opus 5.5, Sonnet 5.5 or Haiku 5.5, so its strongest-model and delegable answers and its three reasons against Haiku may no longer hold; the owner moved hard work to Opus 5.5 on 2026-10-14 (found in PL-KLN5)

**What may be stale.** `docs/maintainer.md` § "Which model each flag means"
says which model "use your strongest model" means and which model `delegable`
means, both "as of 2026-09-19". It names Claude Fable 5.1 as the strongest
model, Claude Opus 5 as the step below, and Claude Sonnet 5 for delegated
work. Its three reasons for Sonnet over Haiku are all about Haiku 4.5: it is a
generation behind, its context window is 200K, and it takes no effort
parameter. Its prices are those of Opus 5, Sonnet 5 and Haiku 4.5.

**What has changed since.** The harness of a 2026-10-17 session lists the
current models as Fable 5.1, Opus 5.5, Sonnet 5.5 and Haiku 5.5. The owner's
Projects instructions moved this project's hard work from Fable 5.1 to Opus
5.5 on 2026-10-14. So a Haiku of the current generation now exists. The
passage's reasons against Haiku, its prices and its two answers need checking
against the current models page
(https://platform.claude.com/docs/en/about-claude/models/overview) before a
session acts on them. Nothing else in the tree outside closed items and old
pull request bodies names these model ids (`grep`, 2026-10-17).

**Generator check.** Not a member of a head. The fact is Anthropic's list of
current models, which only this one dated passage records, so it is one item.

**Why it matters.** Sessions and the owner read this passage to decide which
model takes a hard item and which takes a delegated one. Its reasons against
Haiku describe Haiku 4.5, so they may wrongly rule out a current model, or keep
a model the owner has moved away from.

**Done when.** The passage is dated after 2026-10-17, names the current models
from the models page with their prices, and says whether each of its three
reasons against Haiku still holds for Haiku 5.5.
