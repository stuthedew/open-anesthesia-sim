---
id: PL-9KSY
title: store.write_item's replace= parameter has no caller left now that every field write uses rewrite_item, and PL-YTDN's rename pass is specified as git mv, so the rename branch is dead code that the next field writer could still reach for
status: untriaged
feature: slug-rename-on-write
added: 2026-09-19
---

**Problem.** store.write_item's replace= parameter has no caller left now that every field write uses rewrite_item, and PL-YTDN's rename pass is specified as git mv, so the rename branch is dead code that the next field writer could still reach for
