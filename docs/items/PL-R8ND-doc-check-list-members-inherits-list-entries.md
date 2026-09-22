---
id: PL-R8ND
title: doc_check._list_members inherits list_entries' hardcoded depth-3 stop, so a future bound family whose list is closed by a #### heading would silently read that subsection's bullets as its own members
priority: P3
effort: S
status: dropped
classes: defect
added: 2026-09-22
closed: 2026-09-22
reason: The limit is already documented on _list_members itself, with the route to take (a depth argument on list_entries); no bound family is laid out with a #### heading closing its list; and the failure is loud rather than silent, since a stray bullet read as a member is held to the family's clause and reported by line unless it already satisfies it. Support arrives with the family that needs it, as the check's own rule says its entries do (PL-14QR triage, 2026-09-22).
---

**Problem.** doc_check._list_members inherits list_entries' hardcoded depth-3 stop, so a future bound family whose list is closed by a #### heading would silently read that subsection's bullets as its own members
