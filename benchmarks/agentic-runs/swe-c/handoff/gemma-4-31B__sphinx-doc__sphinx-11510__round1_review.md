VERDICT: REVISE

The candidate patch is empty - no changes were made. The issue is not resolved.

Implement the fix as planned:
- Create a custom `Include` directive subclassing `docutils.parsers.rst.directives.misc.Include` in `sphinx/directives/other.py`.
- Override `run()` to read the included file content and emit the `source-read` event so the included text passes through the same rewriting pipeline as top-level documents.
- Register this directive (replace the standard `include` directive) so it's actually used.
- Edge cases to handle: the `literal`/`code` options of include (where content is read as a literal block), the `start-after`/`end-before`/`lines` slicing, and ensuring the correct docname is passed for the included file.