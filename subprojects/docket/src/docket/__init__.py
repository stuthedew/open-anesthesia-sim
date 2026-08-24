"""docket - a backlog that survives its author's memory.

Built for a repository where the work is done by sessions that start with no
recollection of the last one, and where two of them may be running at once.
Those two constraints produce every design decision here:

- **One file per item.** Adding work adds a file, so no two writers contend,
  and no id has to be allocated from shared state.
- **A brief written for a stranger.** Every item carries what someone needs
  to start it without having been present when it was written down.
- **State that is derived wherever it can be.** Whether work is in flight is
  read from branch names, not stored, so it cannot be left stale by a session
  that ended badly.
- **Mechanical checks in code, judgment left alone.** The tool decides what
  the files can decide and reports the rest for a person to look at.
"""

from .model import Item, parse_item, render_item

__all__ = ["Item", "parse_item", "render_item"]
__version__ = "0.1.0"
