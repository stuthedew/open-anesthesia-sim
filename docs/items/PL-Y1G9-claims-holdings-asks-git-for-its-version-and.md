---
id: PL-Y1G9
title: claims.holdings asks git for its version and its remotes, and neither subcommand is in GitRunner's _READ_ONLY, so every call empties the memo twice once PL-N162 puts it on the digest's path
status: untriaged
feature: claim-record
added: 2026-09-24
---

**Problem.** claims.holdings asks git for its version and its remotes, and neither subcommand is in GitRunner's _READ_ONLY, so every call empties the memo twice once PL-N162 puts it on the digest's path
