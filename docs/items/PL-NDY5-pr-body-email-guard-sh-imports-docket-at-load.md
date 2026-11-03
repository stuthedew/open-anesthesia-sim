---
id: PL-NDY5
title: pr-body-email-guard.sh imports docket at load for modes --screen never uses, which costs about 213 ms on every MCP call and lets an unrelated rename in docket switch the guard off with only an ImportError on swallowed stderr
status: untriaged
feature: guards-say-when-they-cannot-check
added: 2026-11-03
---

**Problem.** pr-body-email-guard.sh imports docket at load for modes --screen never uses, which costs about 213 ms on every MCP call and lets an unrelated rename in docket switch the guard off with only an ImportError on swallowed stderr
