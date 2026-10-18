"""Packaged data resources. No executable code.

The agent, patient and machine parameter JSON files are loaded via
`importlib.resources` in `core/parameters.py`. The shipped Workspaces under
`workspaces/` are not parameters: `layout/shipped.py` reads them.
"""
