VERDICT: REVISE

The candidate patch is empty â no changes were made. The issue is unresolved.

Implement the fix in `sphinx/directives/other.py` in `TocTree.parse_content`. In the loop processing toctree entries, before the existing docname-existence check that emits the "toctree contains reference to nonexisting document" warning, special-case the builtin pages. Specifically:

- Add a check for `docname` (or explicit ref) being in `{'genindex', 'modindex', 'search'}`.
- When matched, append the entry to `toctree['entries']` (and `toctree['includefiles']` handling appropriately â note these are NOT real includefiles, so do not add them there) with a suitable title, then `continue` past the nonexisting-document warning.

Edge cases / details to handle:
- Provide default titles (e.g. "Index", "Module Index", "Search Page") when no explicit title given, so the link text renders correctly.
- Ensure these entries do not get added to `includefiles` (otherwise the builder may try to read them as source documents).
- Confirm the resolve phase (`environment/adapters/toctree.py`) generates correct references to these special pages; you may need to ensure the reference URIs resolve to genindex/modindex/search rather than treating them as documents.

Please produce the actual code change and verify a build with such a toctree emits no warnings and yields working links.