VERDICT: REVISE

The candidate patch is emptyâno changes were made. The issue remains unresolved.

Implement the plan in `xarray/core/computation.py`'s `where()` function:
1. Add `keep_attrs=None` parameter to the signature.
2. Resolve `keep_attrs` from global options when `None` via `_get_keep_attrs(default=False)`.
3. Pass `keep_attrs` to the `apply_ufunc` call.
4. Ensure attrs are taken from `x` (the second argument), e.g. via a `keep_attrs` callable that selects the attrs of the relevant argument, so `xr.where(da==0, -1, da)` propagates `da.attrs`.

Edge case: keep_attrs must select x's attributes, not cond's.