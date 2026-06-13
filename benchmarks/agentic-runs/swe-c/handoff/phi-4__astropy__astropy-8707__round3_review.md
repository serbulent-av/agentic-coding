VERDICT: REVISE

The guard is inserted **before** the docstring in both methods. This breaks the docstring (it's no longer the first statement, so it stops being `__doc__`) and is poor style. Move the `if isinstance(...)` line to **after** the docstring closes in both `Card.fromstring` and `Header.fromstring`.

Additional issues:
- In `Header.fromstring`, `sep` can also be bytes when `data` is bytes. Decode `sep` too (or ensure type consistency), otherwise `data.split(sep)` / string ops mix bytes and str and fail.
- Use proper multi-line `if:` blocks rather than one-liners for readability/consistency with the codebase.

So: place guards after docstrings, handle `sep` decoding in `Header.fromstring`, and confirm `Header.fromstring(b'...')` behaves identically to the str version.