#!/usr/bin/env bash
# PL-8MZ9 probe, on a branch that is never merged. Write an effort cap while
# the session starts, and log when, so the session can check whether the cap
# applied from its first turn.
root="$(cd "$(dirname "$0")/../.." && pwd)"
printf '{\n  "maxEffortLevel": "medium"\n}\n' > "$root/.claude/settings.local.json"
date -u +%Y-%m-%dT%H:%M:%S.%3NZ >> /tmp/probe-cap.log
