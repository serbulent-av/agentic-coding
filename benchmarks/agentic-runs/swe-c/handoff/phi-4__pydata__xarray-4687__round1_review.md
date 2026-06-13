VERDICT: REVISE

The candidate patch is emptyâno changes were made. The issue is unresolved.

Implement the plan in `xarray/core/computation.py` in the `where` function:
- Add `keep_attrs=None` parameter.
- If `keep_attrs is None`, resolve via `_get_keep_attrs(default=False)`.
- Pass `keep_attrs` to the `apply_ufunc` call.
- When keeping attrs, ensure the result takes attrs from `x` (the second argument), e.g. via a `keep_attrs` callable that returns `attrs[1]`.

Without any code, this cannot be approved.