---
id: PL-H2V3
title: make check cannot run in a cloud container whose uv (0.8.17) is older than pyproject's required-version >=0.12.5 and cannot self-update behind the proxy (GitHub API rate limit); the quality suite has to be run tool by tool with PYTHONPATH, and nothing says so
status: dropped
added: 2026-09-26
closed: 2026-09-26
reason: duplicate of PL-QKXZ: the same uv 0.8.17 observation, made in a Projects thread running in the Anthropic-hosted default environment; PL-QKXZ carries it and the decision
---

**Problem.** make check cannot run in a cloud container whose uv (0.8.17) is older than pyproject's required-version >=0.12.5 and cannot self-update behind the proxy (GitHub API rate limit); the quality suite has to be run tool by tool with PYTHONPATH, and nothing says so
