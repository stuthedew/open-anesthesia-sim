---
id: PL-VMMB
title: quality.yml's assert-rewrite cache step runs one share per core, and a share that holds no test module makes pytest exit 5 and fails the job: with 183 modules split by CRC-32 that is negligible on 4 cores but likely past about 40, so a larger runner would fail CI for no fault in the code (found closing PL-GQCQ)
status: untriaged
feature: ci-cost
added: 2026-10-25
---

**Problem.** quality.yml's assert-rewrite cache step runs one share per core, and a share that holds no test module makes pytest exit 5 and fails the job: with 183 modules split by CRC-32 that is negligible on 4 cores but likely past about 40, so a larger runner would fail CI for no fault in the code (found closing PL-GQCQ)
