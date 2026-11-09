---
id: PL-DB6N
title: docs/MODEL.md § 'How this document is held to the tree' says every entry of the invariants list names its test or says no test yet, but the entries in § 'Required invariants' name no test (copy editor structure read, 2026-11-05)
status: dropped
feature: model-md-structure
added: 2026-11-05
closed: 2026-11-09
reason: Covered by PL-8LDF, which ties the required invariants to named tests; checked 2026-11-09, the held-to-the-tree section now says the check does not yet read the invariants
---

**Problem.** docs/MODEL.md § 'How this document is held to the tree' says every entry of the invariants list names its test or says no test yet, but the entries in § 'Required invariants' name no test (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** § "How this document is held to the tree" now says the
automatic check "does not yet check the entries of the required invariants"
(line 12510), so it no longer claims that every invariant names its test. The
gap that remains is that the 17 entries of § "Required invariants" name no
test. `PL-8LDF` (tie the required invariants to named tests) already holds
that work, so this item is dropped.
