# Writing multi-step instructions, procedures and code changes

General guidance, not specific to this project. The canonical copy lives at
`~/.claude/rules/instruction-writing.md`; this checked-in copy exists because
user-scope rules do not reach a Claude Code web or remote session, which starts
on a fresh machine with no user configuration.

Applies to any response that hands someone a procedure, a multi-step change, or
a sequence of commands.

1. **Plan first.** For tasks over roughly five steps, open with a one-line-per-
   phase overview of the whole plan, then deliver Phase 1 in detail.

2. **Chronological order.** Steps appear in strict execution order. A
   prerequisite discovered later is moved to the front of the sequence, never
   phrased as "before doing X, first do Y."

3. **One action per step.** Each numbered step contains exactly one action.
   Split compound steps.

4. **Self-contained steps.** Assume no memory of anything before the current
   message. Restate file names, paths, and complete code verbatim. No `...`
   placeholders, no "the function we discussed." Establish a file's current
   state by reading it; asking the reader to paste it is a last resort, for
   when it cannot be read.

5. **Closed-loop verification.** End each phase with the expected observable
   result ("You should now see X"), and say to stop and report if the result
   differs.

   Gate on confirmation only where the *reader* executes the steps: do not
   provide the next phase until they confirm the prior one. Where the session
   executes the work itself, do not gate — batch the work and report the
   result, because a round trip per phase spends turns without buying
   verification the session could do itself.

6. **Flag irreversible actions.** Any destructive or hard-to-undo step gets an
   explicit warning immediately before it, plus a backup or rollback step
   placed earlier in the sequence.

7. **Referential consistency.** Use exactly one name per file, variable,
   button, or setting for the entire conversation. Never substitute synonyms.

8. **Proximal warnings, sparing emphasis.** Warnings and environment
   requirements sit immediately before the step they govern, never only in a
   preamble or footer. Reserve bold and callouts for genuinely critical items.

9. **Separate explanation from action.** Rationale goes in prose; executable
   steps go in a clearly delimited numbered block containing only actions.
