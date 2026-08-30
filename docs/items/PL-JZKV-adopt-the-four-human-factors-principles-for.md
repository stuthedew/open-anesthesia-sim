---
id: PL-JZKV
title: Adopt the four human-factors principles for multi-step output, and place them where web sessions actually read them
status: dropped
feature: worker-instructions
touches: .claude/rules, CLAUDE.md
added: 2026-08-30
closed: 2026-08-30
reason: duplicate of PL-R5GN, which records the same request in the nine-rule wording the project owner sent to the other session; its distinct analysis - the chunking/batching conflict and its resolution, PL-HZC2 folding into rule 1, and dropping the role preamble - is folded into PL-R5GN rather than lost
---

**Problem.** The project owner supplied four human-factors principles for
multi-step output on 2026-08-30 — chronological linearity, zero context
assumption, cognitive chunking, and visual salience — and asked where they
belong, for this project and globally. Verbatim into both `CLAUDE.md` and
`~/.claude/CLAUDE.md` is the obvious answer and the wrong one, for three
reasons established before proposing:

  - `~/.claude/CLAUDE.md` **does not reach a Claude Code web session**. This
    container has no `/root/.claude/CLAUDE.md` and no `/root/.claude/rules/`.
    User-scope memory is per-machine; the web container is a fresh machine. So
    the global copy alone would miss every session this project is actually
    worked in.
  - `CLAUDE.md` is 547 lines against a documented target of under 200, and the
    documentation is explicit that longer files reduce adherence. Adding ~45
    lines makes every existing rule slightly less likely to be followed. See
    `PL-H7XN`.
  - Principle 1 restates a rule `PL-HZC2` landed the same day, and principle 3
    contradicts an existing one. The documentation states that when two rules
    conflict, the model may pick between them arbitrarily.

**Why it matters.** These principles govern how every instruction this project
produces is read by a human executing it, which on the safety-critical paths
is the difference between a step followed and a step skipped. They are worth
getting into effect properly rather than pasted twice and half-followed.

**The four, and what each needs.**

  1. **Chronological linearity.** Broader than `PL-HZC2` (the closing action
     block annotates order instead of carrying it), which scoped ordering to
     the closing block only. This covers all multi-step output. It should
     **replace** `PL-HZC2`'s rule rather than sit beside it.
  2. **Zero context assumption.** New, no conflict. The concrete half — never
     leave `...` placeholders the reader is expected to fill from memory — is
     the checkable part and the reason it earns its place.
  3. **Cognitive chunking.** **Conflicts with an existing rule**: "Session and
     tool-use efficiency" says to batch related questions and edits into one
     turn, because each turn resends the whole context. Chunking says break
     the work up and pause. Resolvable by scope, and the resolution has to be
     written down rather than left implicit: chunk what the *owner executes*;
     batch what the *session does*. Steps handed to a human are limited to
     3–5; tool calls and questions the session issues are still batched.
  4. **Visual salience.** New, no conflict. Warnings belong at the step they
     bite, not at the top of a reply.

**Drop the role preamble.** "You are an expert system designer" is a
system-prompt shape, and the documentation states that `CLAUDE.md` is
delivered as a user message after the system prompt rather than as part of it.
A second persona statement inside a file that already has a voice competes
with it and buys nothing; the principles are stronger as plain rules.

**Where.** A new `.claude/rules/human-factors.md`, checked in. Rules without
`paths:` frontmatter load at launch with the same priority as
`.claude/CLAUDE.md`, so a checked-in rule reaches every session including the
web ones, and it gives this repository the `.claude/rules/` mechanism it does
not yet have — which is the pressure valve `PL-H7XN` needs.

Globally: the same file at `~/.claude/rules/human-factors.md`, which applies
to every project on that machine. Two copies of stable text is the accepted
cost; the alternative is a symlink from the home directory into this
repository, which makes personal configuration depend on one checkout
existing.

**Done when.** `.claude/rules/human-factors.md` carries the four principles
with the conflicts above resolved rather than restated, `PL-HZC2`'s narrower
ordering rule is folded into principle 1 rather than duplicated, `CLAUDE.md`
is no longer than it is today, and the project owner has the exact path for
the global copy.
