VERDICT: REVISE

The candidate patch is emptyâno changes were made. The issue remains unresolved.

You need to edit `construct_instance()` in `django/forms/models.py`. Locate the block:

```python
if (f.has_default() and
        form[f.name].field.widget.value_omitted_from_data(form.data, form.files, form.add_prefix(f.name))):
    continue
```

Change it so the `continue` only happens when the field is NOT explicitly present in `cleaned_data`. Add a check:

```python
if (f.has_default() and
        form[f.name].field.widget.value_omitted_from_data(form.data, form.files, form.add_prefix(f.name)) and
        getattr(form[f.name].field, 'initial', None) != form.cleaned_data.get(f.name)):
    continue
```

Compare the cleaned_data value against the field's initial to detect whether the user actually overrode it.

Also verify edge cases: fields not in cleaned_data at all (KeyError), and ensure existing behavior (using model default when truly omitted) still works.