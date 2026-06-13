VERDICT: REVISE

The candidate patch is emptyâno changes were made. The issue is unresolved.

Implement in `xarray/core/computation.py`, function `where`:
- Add `keep_attrs=None` parameter.
- If `keep_attrs is None`, resolve via `_get_keep_attrs(default=False)`.
- Pass `keep_attrs` through to `apply_ufunc`.
- Ensure attrs come from `x` (the second argument). A common approach: when `keep_attrs is True`, set `keep_attrs = lambda attrs, context: attrs[1]` so the result takes x's attributes rather than cond's.
- Update the docstring accordingly.

Edge case: default behavior should remain unchanged unless the global option is set.