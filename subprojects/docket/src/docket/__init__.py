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

__all__ = ["Item", "parse_item", "render_item"]
__version__ = "0.1.0"


def __getattr__(name: str) -> object:
    """The names `__all__` re-exports from `model`, loaded only when one is asked for (PEP 562).

    Every guard hook imports `docket.shell` on each Bash call, which imports
    this package first, and `model` brings `dataclasses`, `inspect` and
    `pathlib`, about 15 ms of that call (`PL-JNYL`). No module in the tree
    asks the package for these names; each imports the module it needs.
    """
    if name in __all__:
        from . import model

        return getattr(model, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
