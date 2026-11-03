---
id: PL-D16Y
title: tools/pr_body_check.py screens only title and body, so an address in a merge's commit_message, which becomes the squash commit on main, or in push_files content passes; it also refuses git@github.com remotes and GitHub's own users.noreply.github.com addresses
status: untriaged
feature: guards-keyed-on-the-action
added: 2026-11-03
---

**Problem.** tools/pr_body_check.py screens only title and body, so an address in a merge's commit_message, which becomes the squash commit on main, or in push_files content passes; it also refuses git@github.com remotes and GitHub's own users.noreply.github.com addresses
