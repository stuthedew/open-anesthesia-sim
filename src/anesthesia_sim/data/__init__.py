"""Packaged data resources, with no executable code.

`core/parameters.py` loads the agent, patient and machine parameter JSON files
through `importlib.resources`. The shipped Workspaces under `workspaces/` are
not parameters: `layout/shipped.py` reads them.
"""
