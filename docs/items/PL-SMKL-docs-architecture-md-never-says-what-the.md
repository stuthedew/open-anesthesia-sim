---
id: PL-SMKL
title: docs/ARCHITECTURE.md never says what 'the unconditional set' holds, yet tells contributors it never goes in a View (copy editor structure read, 2026-11-05)
status: dropped
feature: architecture-md-structure
added: 2026-11-05
closed: 2026-11-09
reason: Fixed by the line edit (#2044): docs/ARCHITECTURE.md § 'Where new code belongs' now defines the unconditional set as the values docs/MODEL.md § 'Minimum displayed outputs' requires on screen at all times; listing its members here too would be a second copy of MODEL.md's list
---

**Problem.** docs/ARCHITECTURE.md never says what 'the unconditional set' holds, yet tells contributors it never goes in a View (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, "the unconditional set".** The contributor needs to know what "the unconditional set" (also "the unconditional region") holds before obeying "never goes in a View" (1187-1202). The text does not give it. The term appears in Package map 104 and 108 and in Where new code belongs 1187-1202 and 1238-1253. No row says in words what it is, beyond row 108's "refuses a run lacking a declared value" and the pointer to `docs/MODEL.md` § "Minimum displayed outputs".

**Checked 2026-11-09:** `grep -n 'unconditional' docs/ARCHITECTURE.md` finds the term in the package map and in § "Where new code belongs". That section now says what the set is: "A View never shows a value from the unconditional set, the values that `docs/MODEL.md` § "Minimum displayed outputs" requires on screen at all times." The line edit in #2044 added that definition, which the structure read had not seen. Listing the set's members here as well would make a second copy of a list that `docs/MODEL.md` owns, so the pointer is the right answer and nothing is left to do.
