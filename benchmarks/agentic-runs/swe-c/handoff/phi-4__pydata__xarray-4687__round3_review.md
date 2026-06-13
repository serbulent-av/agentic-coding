VERDICT: REVISE

The candidate patch is emptyâno changes were made. The issue is unresolved.

Implement in `xarray/core/computation.py` in the `where` function:
1. Add `keep_attrs=None` parameter.
2. If `keep_attrs is None`, resolve via `_get_keep_attrs(default=False)`.
3. Pass `keep_attrs` to `apply_ufunc`. Note: a `keep_attrs=True` that copies the cond's attrs is wrong hereâyou must propagate `x`'s attrs (the second positional arg). Use a callable/lambda for keep_attrs so the correct variable's attrs are selected, since apply_ufunc's default keep_attrs picks the first argument (cond), not x.
4. Add a test confirming attrs preserved and default behavior unchanged.