toctree contains reference to nonexisting document 'genindex', 'modindex', 'search'
**Is your feature request related to a problem? Please describe.**
A lot of users try to add the following links to the toctree:
```
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
like this:
```
.. toctree::
   :maxdepth: 1
   :caption: Indices and tables

   genindex 
   modindex
   search
```

See:
* https://stackoverflow.com/questions/36235578/how-can-i-include-the-genindex-in-a-sphinx-toc
* https://stackoverflow.com/questions/25243482/how-to-add-sphinx-generated-index-to-the-sidebar-when-using-read-the-docs-theme
* https://stackoverflow.com/questions/40556423/how-can-i-link-the-generated-index-page-in-readthedocs-navigation-bar

And probably more.

However when doing this we get:
```
$ make html
...
.../index.rst:30: WARNING: toctree contains reference to nonexisting document 'genindex'
.../index.rst:30: WARNING: toctree contains reference to nonexisting document 'modindex'
.../index.rst:30: WARNING: toctree contains reference to nonexisting document 'search'
...
```

**Describe the solution you'd like**
The following directive should be possible and do not rise errors:
```
.. toctree::
   :maxdepth: 1
   :caption: Indices and tables

   genindex 
   modindex
   search
``


---
## Implementation plan (from a senior Opus 4.8 planner — follow these steps)
Root cause: putting genindex/modindex/search in a toctree warns 'toctree contains reference to nonexisting document' because these are generated pages without a source document.
Plan:
1. In sphinx/directives/other.py (TocTree directive parse_content) where each entry's docname is validated, special-case the builtin pages {'genindex','modindex','search'} so they are accepted as valid toctree entries instead of emitting the 'nonexisting document' warning.
2. Add them as explicit toctree entries (with their standard titles) so links resolve.
3. Verify: a toctree listing genindex/modindex/search builds with no warning and produces working links.
---


---
## YOUR PREVIOUS ATTEMPT WAS REVIEWED
Your previous patch:
```diff

```
A senior reviewer (Opus 4.8) gave this feedback — address ALL of it:
VERDICT: REVISE

The candidate patch is empty â no changes were made. Nothing in the issue is resolved.

You need to implement the plan in `sphinx/directives/other.py`, in the `TocTree` directive's `parse_content` method. Specifically:

1. Define the builtin set `{'genindex', 'modindex', 'search'}`.
2. When iterating over toctree entry lines, before the existing check that emits the "toctree contains reference to nonexisting document" warning, special-case these names. Append them to `toctree['entries']` (as `(title, docname)` tuples with their standard titles, e.g. `genindex` â "Index", `modindex` â "Module Index", `search` â "Search Page") and also add to `toctree['includefiles']` appropriatelyâbut note these aren't real docs, so do NOT add them to `includefiles` (which would later trigger nonexistence checks elsewhere). Just add the entry reference.
3. Ensure the environment's later toctree resolution (`sphinx/environment/adapters/toctree.py`) handles these special docnames by generating reference nodes to the builtin pages rather than trying to resolve a real document. You likely need to handle them in `_entries_from_toctree` / `resolve` so a proper `reference`/`compact_paragraph` with the correct URI (`genindex`, etc.) is produced.

Edge cases to verify: explicit titles like `Index <genindex>`, the entries appearing alongside normal docs, and that no "nonexisting document" warning is emitted. Add a regression test under tests covering a toctree with these three entries.

Please submit an actual patch.
Produce a corrected, complete solution.
---
