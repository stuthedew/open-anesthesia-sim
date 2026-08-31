---
id: PL-DGM4
title: The instruction-writing rules and the docket skill prescribe opposite openings for a 'what next' reply
status: untriaged
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

