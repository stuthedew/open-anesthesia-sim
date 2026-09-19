---
id: PL-VJPJ
title: bin/docket next raises BrokenPipeError and prints a traceback when its output is piped into a command that closes early, so next | head looks like a crash to every session that pipes it
status: untriaged
added: 2026-09-19
---

**Problem.** bin/docket next raises BrokenPipeError and prints a traceback when its output is piped into a command that closes early, so next | head looks like a crash to every session that pipes it
