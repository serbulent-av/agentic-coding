VERDICT: REVISE

The candidate patch is empty â no changes were made. The issue is unresolved.

You need to override docutils' `Include` directive in Sphinx (the `SphinxDirective`-based include in `sphinx/directives/other.py`, class `Include`). In its `run()` method, after the file content is read but before it's parsed, emit the `source-read` event so included content passes through the same rewriting.

Key implementation points:
- Read the file content yourself (using the rawtext/source), wrap it in a list, call `self.env.app.events.emit('source-read', docname, arg)`, then feed the modified content back into the parsing path (e.g., via `StateMachine.insert_input` or by setting it as the include directive's input).
- Determine an appropriate `docname` for the included file.
- Preserve all existing `include` options (literal, code, start-after, end-before, tab-width, encoding, etc.) â don't break the literal/code-block include path.
- Guard against breaking parallel reads and circular includes.

Until a real patch is provided, this cannot be approved.