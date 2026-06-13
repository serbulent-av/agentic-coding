VERDICT: REVISE

The candidate patch is empty â no changes were made. You must implement the fix in `construct_instance()` in `django/forms/models.py`.

Specifically, the loop currently has:
```python
if (f.has_default() and
        form[f.name].field.widget.value_omitted_from_data(form.data, form.files, form.add_prefix(f.name))):
    continue
```
Change this so it only `continue`s when the field is NOT present in `form.cleaned_data`:
```python
if (f.has_default() and
        form[f.name].field.widget.value_omitted_from_data(form.data, form.files, form.add_prefix(f.name)) and
        cleaned_data.get(f.name) in form[f.name].field.empty_values):
    continue
```
This lets an explicitly set non-empty `cleaned_data` value override the model default, while still preserving the default when the value is genuinely empty/omitted.

Please produce the actual diff.