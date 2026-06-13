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

The candidate patch is empty â no changes were made. The issue is unresolved.

Implement the fix in `sphinx/directives/other.py` in `TocTree.parse_content`. In the loop processing toctree entries, before the existing docname-existence check that emits the "toctree contains reference to nonexisting document" warning, special-case the builtin pages. Specifically:

- Add a check for `docname` (or explicit ref) being in `{'genindex', 'modindex', 'search'}`.
- When matched, append the entry to `toctree['entries']` (and `toctree['includefiles']` handling appropriately â note these are NOT real includefiles, so do not add them there) with a suitable title, then `continue` past the nonexisting-document warning.

Edge cases / details to handle:
- Provide default titles (e.g. "Index", "Module Index", "Search Page") when no explicit title given, so the link text renders correctly.
- Ensure these entries do not get added to `includefiles` (otherwise the builder may try to read them as source documents).
- Confirm the resolve phase (`environment/adapters/toctree.py`) generates correct references to these special pages; you may need to ensure the reference URIs resolve to genindex/modindex/search rather than treating them as documents.

Please produce the actual code change and verify a build with such a toctree emits no warnings and yields working links.
Produce a corrected, complete solution.
---
