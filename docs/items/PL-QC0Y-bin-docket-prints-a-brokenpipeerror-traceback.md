---
id: PL-QC0Y
title: bin/docket prints a BrokenPipeError traceback when its output is piped into head: show PL-X | head -8 ends in a traceback from cmd_show's print, because main never restores the default SIGPIPE handling
status: dropped
added: 2026-09-22
closed: 2026-09-22
reason: duplicate of PL-VJPJ: the same missing SIGPIPE handling in main, seen from show rather than next; recorded there as a recurrence
---

**Problem.** bin/docket prints a BrokenPipeError traceback when its output is piped into head: show PL-X | head -8 ends in a traceback from cmd_show's print, because main never restores the default SIGPIPE handling

**Dropped 2026-09-22 as a duplicate of `PL-VJPJ`**, which is the same defect seen from `next`: `main` never restores the default SIGPIPE handling, so every command piped into `head` can end in a traceback. The filing is recorded on `PL-VJPJ` as a recurrence, so the `show` instance is kept there.
