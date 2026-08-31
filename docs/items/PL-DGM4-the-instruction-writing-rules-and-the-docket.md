---
id: PL-DGM4
title: The instruction-writing rules and the docket skill prescribe opposite openings for a 'what next' reply
priority: P2
effort: S
status: ready
verify: python3 tools/doc_check.py check
classes: docs
feature: worker-instructions
touches: CLAUDE.md, .claude/rules/instruction-writing.md, .claude/skills/docket/SKILL.md
added: 2026-08-31
---

**Problem.** Two in-repo instruction sources give opposite instructions for
the same message, and a session cannot satisfy both.

`.claude/rules/instruction-writing.md` rule 10: "A message asking the user to
decide opens with the question(s) and the recommendation, one line each.
Supporting detail follows; **nothing precedes the questions**."

`.claude/skills/docket/SKILL.md`, "Mode: recommend what to work on": "**Open
with where the release stands - two or three sentences, before any item.**
`docket wave` prints the facts; state them as prose, because a row of counts
is not an answer to 'where are we'."

A recommendation names an item, so the skill's opening paragraph either
precedes the question (violating rule 10) or does not come first (violating
the skill). The reply to "what next" is exactly the message both describe.

**Observed 2026-08-31.** A session answering "what next" followed the skill,
opened with the release paragraph, and put the question at the end across
several screens. The project owner rejected the format and named the rules
file. So the conflict is not theoretical: it has produced one wrong reply,
and the skill is the more specific document, which is why it won.

**Why it matters.** Neither document is wrong about what it wants. Rule 10
protects the owner's attention - a decision request should be answerable
without reading to the bottom. The skill protects against a different
failure, a reply that lists items without saying where the release stands,
which is the "list of homework" `CLAUDE.md` also warns about. The cost is
paid on every "what next" reply, which is one of the most frequent messages
this project produces.

**Where.** `.claude/rules/instruction-writing.md` (rule 10) and
`.claude/skills/docket/SKILL.md` ("Mode: recommend what to work on").
`CLAUDE.md`'s "Answer 'what should we work on next?' at feature altitude"
bullet is the third statement of the same thing and should be checked for
consistency with whatever is decided. Note `PL-019F` already proposes
rewriting that bullet, so the two should be worked together or at least in
that order.

**Approach.** A reconciliation exists and is probably right: rule 10's
question-and-recommendation lines come first, and the skill's release
paragraph becomes the first block of "supporting detail" rather than the
opening. That satisfies rule 10 literally and keeps what the skill is
protecting. It needs the owner's agreement because it changes a rule they
wrote, and then an edit to whichever document loses.

**Done when.** One of the two documents is edited so that a session following
both produces one format, and `CLAUDE.md`'s altitude bullet agrees with it.


**Decided by the project owner (2026-08-31).** The rules file wins, and it
wins generally rather than in this one instance: it should apply without being
named in the prompt, which is how the conflict surfaced — the owner had to say
"use instruction md file" to get rule 10's shape back.

So precedence is now stated in three places, each doing a different job.
`.claude/rules/instruction-writing.md` gains a `PRECEDENCE` preamble saying the
rules apply to every reply unasked and decide its shape; it stays project-free,
so the user-scope copy carries the same statement. `CLAUDE.md` names the file
and states the split that makes the precedence liveable — **the rules file
decides shape, the other document decides content** — because a bare "the rules
win" would read as licence to drop what a skill was protecting. The `docket`
skill's "Mode: recommend what to work on" is edited rather than obeyed: its
release paragraph is no longer the opening but the first block of supporting
detail, under the recommendation. Nothing it was protecting is lost — the
paragraph is still required, still before any other item — and rule 10 is
satisfied literally.

`PL-019F` (the 'what next' rule answers one altitude below the roadmap step)
was folded into the same branch rather than filed behind this one: its edit is
to the same `CLAUDE.md` bullet this item had to touch, so two branches would
have contended on one paragraph. The bullet now answers from the roadmap step
down and opens with the recommendation.
