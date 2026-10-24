---
id: PL-9K28
title: A builder subagent that runs make check in the background ends its turn and is not woken when the command finishes, so the PL-ZZ03 builder stopped twice with tested work unpushed until the parent resumed it; builder briefs do not say to run long checks in the foreground
status: untriaged
added: 2026-10-24
---

**Problem.** A builder subagent that runs make check in the background ends its turn and is not woken when the command finishes, so the PL-ZZ03 builder stopped twice with tested work unpushed until the parent resumed it; builder briefs do not say to run long checks in the foreground
