VERDICT: REVISE

The candidate patch is emptyâno changes were made at all. The issue is therefore unresolved.

Implement the fix in `sphinx/directives/other.py`, in the `TocTree` directive's content-parsing logic. Specifically:

1. When iterating over toctree entries, before the check that emits the `toctree contains reference to nonexisting document` warning, special-case the builtin generated pages `genindex`, `modindex`, and `search`.

2. For these entries, append them to `toctree['entries']` (and `toctree['includefiles']` as appropriate) with their standard titles (e.g. "Index", "Module Index", "Search Page") so the links resolve, rather than treating them as missing documents.

3. Ensure the resolution stage (in `sphinx/environment/adapters/toctree.py`) generates proper references to these special pages so the rendered links point to `genindex.html`, etc.

Edge cases to verify: explicit title syntax (e.g. `Index <genindex>`), `:glob:` option interaction, and that no warning is emitted while building.