---
id: PL-J503
title: docket's verify.sanctioned_queue_edit compares a recurrences: value one diff line at a time, so a capture's append to a value continued on an indented line reads as an ordinary edit outside touches and fails verify; latent
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** docket's verify.sanctioned_queue_edit compares a recurrences: value one diff line at a time, so a capture's append to a value continued on an indented line reads as an ordinary edit outside touches and fails verify; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. In a temporary repository, the append `with_front_matter_field(append=True)` makes lands on the continuation line, so the diff `-  2026-09-03 PL-CCCC` / `+  2026-09-03 PL-CCCC, 2026-10-04 PL-DDDD` reads as '' rather than 'recurrence', an ordinary edit outside `touches` (its verify failure by reading). `parse_item` reads all three entries both ways. Latent: 77 items carry `recurrences:`, all on one line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
