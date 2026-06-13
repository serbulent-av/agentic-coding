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
diff --git a/sphinx/directives/other.py b/sphinx/directives/other.py
index 35e16e623..b096f357a 100644
--- a/sphinx/directives/other.py
+++ b/sphinx/directives/other.py
@@ -118,7 +118,7 @@ class TocTree(SphinxDirective):
                 docname = docname_join(self.env.docname, docname)
                 if url_re.match(ref) or ref == 'self':
                     toctree['entries'].append((title, ref))
-                elif docname not in self.env.found_docs:
+                elif docname not in self.env.found_docs and docname not in {'genindex', 'modindex', 'search}:
                     if excluded(self.env.doc2path(docname, False)):
                         message = __('toctree contains reference to excluded document %r')
                         subtype = 'excluded'

```
A senior reviewer (Opus 4.8) gave this feedback — address ALL of it:
VERDICT: REVISE

1. **Syntax error**: `{'genindex', 'modindex', 'search}` is missing the closing quote on `'search'`. This will fail to parse â should be `{'genindex', 'modindex', 'search'}`.

2. **Incomplete fix**: Suppressing the warning alone is not enough. The entry still needs to be appended to `toctree['entries']` so the link actually resolves. As written, when `docname` is one of the builtin pages, the code falls through and appends `(title, docname)` as a normal toctree entry â but the resolver later still needs to handle these special docnames when generating the TOC/HTML, or you'll get a broken/empty link or a later resolve-time warning. Verify the resolve phase (`sphinx/environment/adapters/toctree.py`) handles these builtin docnames and produces working `genindex.html`/`search.html` links with proper titles.

3. **Edge case**: confirm behavior when builder doesn't generate these pages (e.g. genindex disabled, or non-HTML builders) so you don't create dangling references.

4. Add a test confirming a toctree with these three entries builds without warnings and links resolve.

Fix the typo first, then ensure the entries actually render as working links end-to-end.
Produce a corrected, complete solution.
---
