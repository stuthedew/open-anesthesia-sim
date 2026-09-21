---
id: PL-XJWG
title: The repository's own tests/ tree reads the developer's global git config too - 142 commits, 6.20s of a 257s run - and takes the identical two lines PL-YRYR put in subprojects/docket/tests/conftest.py
status: dropped
added: 2026-09-21
closed: 2026-09-21
reason: PL-YRYR's conftest.py landed at the repository root rather than in subprojects/docket/tests, so pytest applies it to this tree too - the two lines this item asked for are already in place
---

**Problem.** The repository's own tests/ tree reads the developer's global git config too - 142 commits, 6.20s of a 257s run - and takes the identical two lines PL-YRYR put in subprojects/docket/tests/conftest.py
