---
id: PL-R5GN
title: Adopt the nine instruction-writing rules, scoped for an agent that can read and edit files itself
priority: P2
effort: S
status: done
classes: docs
feature: worker-instructions
milestone: v0.2.7
touches: .claude/rules, CLAUDE.md
added: 2026-08-30
closed: 2026-08-30
commit: 487d7d5
pr: 76
---

**Problem.** The project owner supplied nine rules for multi-step instructions
on 2026-08-30 — plan first, chronological order, one action per step,
self-contained steps, closed-loop verification, flag irreversible actions,
referential consistency, proximal warnings, and separating explanation from
action — and asked where they should live so they apply to this project and to
every other.

**Why it matters.** Seven of the nine are unambiguous improvements and two of
them, chronological order and separating rationale from actions, already exist
here in narrower project-specific form (`PL-HZC2`, and the closing-block rule).
Adopting the general set without reconciling the narrow ones risks the failure
the memory documentation warns about directly: "if two rules contradict each
other, Claude may pick one arbitrarily."

**Two rules assume an assistant that cannot touch the filesystem.** They were
written for a chat context and are actively wrong for Claude Code:

  - **Rule 4** ends "If uncertain of a file's current state, ask the user to
    paste it before issuing an edit." Claude Code reads the file itself, and
    the Edit tool already refuses to operate on a file not read in the session.
    Asking the owner to paste it is slower and strictly worse. The intent —
    never edit blind, no `...` placeholders, no "the function we discussed" —
    is right and should be kept with the mechanism replaced by "read the file
    first".
  - **Rule 5** ends "Do not provide the next phase until the user confirms the
    prior one." Correct when the owner is executing the steps, as with a
    repository setting or a tag. Applied to work the session executes itself it
    converts one task into a round trip per phase, which contradicts
    `CLAUDE.md`'s own "session cost scales with the number of turns multiplied
    by the size of the context". It should be scoped to steps the owner runs.

**Placement.** `~/.claude/CLAUDE.md` alone does not reach a web or remote
session: the container starts with no user-level configuration, so a user-scope
rule is invisible in exactly the sessions this project uses most. Only
checked-in files reach them. So the canonical copy belongs in
`.claude/rules/instruction-writing.md` in this repository, with the user-scope
copy a symlink to it. `.claude/rules/` supports symlinks by design.

A rules file rather than an addition to `CLAUDE.md`: rules load at launch with
the same priority as `.claude/CLAUDE.md`, one topic per file, and `CLAUDE.md`
is already at 547 lines against a documented 200-line adherence target
(`PL-JQY5`).

**Folded in from `PL-JZKV`.** A concurrent session received the same request
worded as four human-factors principles — chronological linearity, zero context
assumption, cognitive chunking, visual salience — and reached the same
placement answer independently. Three points from its analysis that this item
did not have:

  - **The chunking/batching conflict, and its resolution.** Rule 5 pulls
    against `CLAUDE.md`'s "batch related questions, and related edits, into one
    turn". Resolve by who executes, and write the resolution down rather than
    leaving it implicit: **chunk what the owner executes; batch what the
    session does.** Steps handed to a person are limited to a few at a time;
    tool calls and questions the session issues are still batched into one
    turn.
  - **Rule 1 subsumes `PL-HZC2`.** `PL-HZC2` (the closing action block
    annotates order instead of carrying it) scoped ordering to the closing
    block; rules 1 and 2 cover all multi-step output. The narrow rule should
    fold into the general one rather than sit beside it — two rules on
    ordering is the conflict case the documentation warns about.
  - **Drop any role preamble.** `CLAUDE.md` is delivered as a user message
    after the system prompt, so a second persona statement competes with the
    voice already there and buys nothing.

**Symlink or copy, for the user-scope half.** `PL-JZKV` argued against a
symlink from the home directory into this checkout, on the grounds that it
makes personal configuration depend on one repository existing — and a broken
symlink fails silently, which is worse than drift. Two copies, with the
checked-in one canonical, is the safer default; the content is stable enough
that drift is a small risk.

**Done when.** The rules live in one checked-in file that loads in this
repository and has a stated route to user scope, rules 4 and 5 are scoped for
an agent with filesystem access, the chunking/batching resolution is written
down, and `PL-HZC2`'s narrower ordering rule is folded in rather than
duplicated.

**Resolved by the project owner (2026-08-30).** Rule 4 reads "establish a
file's current state by reading it; asking the reader to paste it is a last
resort, for when it cannot be read" — his wording, keeping the paste as a
fallback rather than dropping it. Rule 5 is scoped by who executes, as
proposed. The rules are **general guidance rather than a project convention**,
which settles the framing: the file names no project, and says in its own
opening that the canonical copy is the user-scope one and the checked-in copy
exists only because user scope does not reach a web session.

His numbering is preserved 1-9 rather than regrouped, so that "rule 5" refers
to the same thing in every later conversation — which is rule 7 applied to the
document itself.

`PL-HZC2`'s closing-block rule was **not** folded away. Once the rules are
general rather than project-specific, the closing action block is a project
artifact and its ordering rule belongs in `CLAUDE.md`; it now names the general
rule it applies, in one clause, so the two read as principle and instance
rather than as competitors.
