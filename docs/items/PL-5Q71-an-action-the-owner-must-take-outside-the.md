---
id: PL-5Q71
title: An action the owner must take outside the repository is handed back as intent rather than as its steps
priority: P2
effort: S
status: done
classes: defect
feature: worker-instructions
milestone: v0.2.7
touches: CLAUDE.md
added: 2026-08-30
closed: 2026-08-30
commit: e1ccbd4
pr: 76
verify: python3 tools/doc_check.py check
not-delegable: the change rewrites a rule in CLAUDE.md that every session then follows, and whether a set of steps is genuinely followable is a judgment no check decides
---

**Problem.** `CLAUDE.md` had exactly one rule of this shape — "Never ask for a
tag without pasting the commands" — written for the one case that had already
gone wrong. Every other action outside the repository was left to a session's
judgment, and on 2026-08-30 a closing block asked the owner to "turn on the
required-check ruleset" with no menu path, no field values and no check name.
He had to come back and ask what settings to change, which is the same round
trip the tag rule exists to prevent.

**Why it matters.** An action item the owner cannot execute from the line
itself is not an action item; it is a research task handed back, and it costs
a round trip at exactly the moment they were ready to act. The general form
was always the rule — the tag case was just the instance that had been
noticed.

**Where.** `CLAUDE.md`, the closing-block bullet list, as a general rule above
the tag bullet, with the tag bullet kept and marked as its named instance so
the two cannot drift apart.

**Approach.** Anything the session cannot reach — a repository or account
setting, a tag, a plan change, a third-party console — is written as the steps
themselves: where to click or what to run, the values, and what success looks
like.

Two clauses earn their place beyond that. **Verify against current
documentation before writing the steps**, because a UI path recalled from
training is the same class of error as a solubility coefficient recalled from
memory, and this project already refuses the second. And **where the
documentation cannot be reached, say so and give the API or CLI equivalent
alongside**, so a stale label in one is caught by the other. That case is not
hypothetical: `docs.github.com` is blocked by this environment's egress proxy,
which is how the gap was found.

**Done when.** The rule states that an action outside the repository carries
its exact steps, requires them to be checked against current documentation,
and says what to do when that documentation cannot be reached.
