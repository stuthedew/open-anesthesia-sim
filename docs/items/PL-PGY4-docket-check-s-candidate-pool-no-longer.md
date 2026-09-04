---
id: PL-PGY4
title: docket check's candidate pool no longer benefits from more workers: measured 31.6 s at four, 28.0 s at eight, 32.4 s at sixteen, 32.5 s at twenty-four
status: dropped
classes: perf
feature: dev-tooling
added: 2026-09-03
closed: 2026-09-03
reason: A measurement rather than work. It was captured to stop the figure being lost, and both places that needed it now hold it - `landed_workers()`'s docstring cites the 78-candidate run as what shows the cap at eight is still binding on nothing, and `PL-8BFV` carries the full table as one of the levers already ruled out for `bin/docket check`. Left as an item it would sit in the queue forever with nothing to do: the finding is that the current setting is correct.
---

**Problem.** Measured 2026-09-03 on this store, 78 candidate commands, four
cores, the candidate set selected exactly as `already_passing` selects it:

| pool width | wall clock |
| --- | --- |
| 4 workers | 31.6 s |
| 8 workers | **28.0 s** |
| 16 workers | 32.4 s |
| 24 workers | 32.5 s |

`landed_workers()` returns `min(8, cpu_count * 2)`, so eight is what it chose
here and eight is the best of the four. Sixteen and twenty-four are *slower*,
which is the finding: the pool has stopped gaining from width, so the cap is no
longer the thing limiting it and raising it would cost rather than buy.

**Why it was captured.** The docstring justifying `* 2` rested on a
49-candidate measurement where the knee was at the core count. That the knee is
still there at 78 candidates is what shows the shape is right rather than
merely inherited - and it rules out "raise the cap" as a lever before anybody
spends a session on it.

**Why it is dropped rather than done.** See `reason` above. There is no change
to make; the measurement has landed where it is read.
