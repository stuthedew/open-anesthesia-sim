---
id: PL-29RB
title: bin/docket verify refuses a closing item's recorded test that passes at the commit where the branch left the default branch with the branch's test files laid over it, so a test that passes with and without the work is not accepted as showing it
status: dropped
feature: standing-weight
added: 2026-11-21
closed: 2026-11-21
reason: the changed-line mutation check that the close-out audit already runs once per branch (PL-CZXN) refuses a branch whose unit tests miss a mutant of a changed simulator line, which shows more than a recorded test failing before the work; the review that asked for this withdrew it on 2026-11-21 (PL-TPXK)
---

**Problem.** bin/docket verify refuses a closing item's recorded test that passes at the commit where the branch left the default branch with the branch's test files laid over it, so a test that passes with and without the work is not accepted as showing it
