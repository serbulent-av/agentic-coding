VERDICT: REVISE

The candidate patch is emptyâno changes were made. Implement the fix in `xarray/core/computation.py` in the `where` function:

1. Add `keep_attrs=None` parameter.
2. If `keep_attrs is None`, resolve via `_get_keep_attrs(default=False)`.
3. When `keep_attrs is True`, set it to a lambda/callable that propagates attrs from `x` (the second positional arg). Pass `keep_attrs` to `apply_ufunc(...)`.
4. Ensure default behavior remains unchanged unless the global option is set.

Without any code, the issue is unresolved.