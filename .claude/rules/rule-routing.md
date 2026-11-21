---
paths:
  - "/CLAUDE.md"
  - "/.claude/**"
---

# Where a rule about how sessions work is written

`CLAUDE.md` § "The queue, and how the project owner works" says that a behavior
change takes effect in the session that asks for it, and that the edit is
routed. These are the four places it can go. They load with the instruction
files, because a session chooses among them only when it edits one (`PL-GDN7`).

**Route it; do not append to `CLAUDE.md` by default.** Ask *at what moment a
session needs the rule, and what is the cheapest thing that delivers it then.*
Four dispositions, cheapest first:

1. **A check or a script**, wired into `make check`, a hook, or CI. Zero
   resident context, and it never fails to fire. Deleting prose because
   something deterministic now enforces it is the strongest outcome here.
2. **A skill**, for a multi-step procedure whose trigger is the skill's own
   trigger. It loads only when relevant; the queue workflows are the example.
3. **A path-scoped rule** — a `.claude/rules/*.md` with `paths:` frontmatter,
   which loads when a session reads, writes or edits a matching file. Right
   for a rule that matters only in part of the tree; wrong for one that must
   fire before a first write, which it reaches only after that write.
4. **Resident in `CLAUDE.md`**, only for what a session could violate before
   it would think to look anything up.

**A rule that lands in none of the four has been lost**, which is worse than
`CLAUDE.md` staying long. Never delete a rule for being wordy. A rule whose
failure a check now catches is retired rather than kept, on the test in
`docs/resident-instructions.md` § "When a resident rule is retired"
(`PL-NJTZ`).
