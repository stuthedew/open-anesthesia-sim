---
id: PL-3HMQ
title: bin/docket release writes the notes from the items' pr: fields before bin/docket record can supply them, so an item whose pull request merged without one loses its link in the shipped notes permanently - v0.4.33 lost PL-LPLD's #758 and v0.4.34 would have lost three
status: dropped
added: 2026-09-20
closed: 2026-09-20
reason: Same finding as PL-W7WL, which supersedes it, and the third live filing of one defect (PL-66X4 dropped into PL-2M5T; PL-2M5T dropped into PL-W7WL). A bare capture with no triage; its evidence - v0.4.33 shipping without PL-LPLD's #758, and v0.4.34 having lost three more but for a hand correction at the cut - is carried into PL-W7WL. Found by PL-JKML's duplicate sweep, 2026-09-20.
---

**Problem.** bin/docket release writes the notes from the items' pr: fields before bin/docket record can supply them, so an item whose pull request merged without one loses its link in the shipped notes permanently - v0.4.33 lost PL-LPLD's #758 and v0.4.34 would have lost three
