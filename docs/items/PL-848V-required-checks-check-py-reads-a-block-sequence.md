---
id: PL-848V
title: required_checks_check.py reads a block-sequence on: (on: followed by - pull_request lines) and a flow-mapping on: ({pull_request: ...}) as no events, so a pull-request workflow spelled either way drops out of the reconciliation and the check passes; its docstring calls the three spellings it reads the three the YAML spec allows
status: untriaged
added: 2026-10-01
---

**Problem.** required_checks_check.py reads a block-sequence on: (on: followed by - pull_request lines) and a flow-mapping on: ({pull_request: ...}) as no events, so a pull-request workflow spelled either way drops out of the reconciliation and the check passes; its docstring calls the three spellings it reads the three the YAML spec allows
