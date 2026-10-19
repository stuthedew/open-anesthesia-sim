---
id: PL-4T32
title: triage, delegable, wave, feature, gate and generators still answer from the working tree's copy of each item behind origin/main, where the digest, list, status, concurrent, next, show and picks read the base's newer copy through cli._load_to_read
status: untriaged
feature: one-snapshot
added: 2026-10-19
---

**Problem.** triage, delegable, wave, feature, gate and generators still answer from the working tree's copy of each item behind origin/main, where the digest, list, status, concurrent, next, show and picks read the base's newer copy through cli._load_to_read

**Why it matters.** Found closing `PL-KS01`, which moved the digest, `list`,
`status` and `concurrent` onto `cli._load_to_read`, the loader that reads the
default branch's newer copy of each item. That item's brief named only those
four, so the other read commands were left as they were. Behind a closure on
`origin/main`, `delegable` can still offer a worker an item that `main` has
closed, and `triage` can list an item that `main` has already triaged.
`triage` is followed by edits to the working tree's files, so whether it
should read the base's copy is a real question rather than a plain defect.

**Done when.** Each of these commands either loads the store through
`cli._load_to_read`, or the README's `PL-Y48N` paragraph gives the reason it
reads the working tree's copy.
