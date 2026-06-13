VERDICT: REVISE

The candidate patch is empty â no changes were made. The issue is unresolved.

Implement in `xarray/core/computation.py` `where()`:
- Add `keep_attrs=None` parameter.
- If `keep_attrs is None`, resolve via `_get_keep_attrs(default=False)`.
- Pass `keep_attrs` to `apply_ufunc`. When True, propagate attrs of `x` (the second arg) to the result â define a `keep_attrs` callable that selects `attrs[1]` so the result gets x's attributes rather than cond's.
- Edge case: handle scalar `x` without attrs gracefully.