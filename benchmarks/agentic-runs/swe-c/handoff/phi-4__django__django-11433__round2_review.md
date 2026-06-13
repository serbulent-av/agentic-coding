VERDICT: REVISE

The patch is empty. No changes were made to `construct_instance()` in `django/forms/models.py`.

Implement the fix per the plan: in the loop, the current condition skips fields where the value was omitted from the data and the model field has a default. Change it so that when `f.name` is present in `form.cleaned_data`, the cleaned value is still applied. Specifically, only `continue` when `f.has_default()` AND `form[f.name].field.widget.value_omitted_from_data(...)` AND `f.name not in cleaned_data` (i.e., cleaned_data didn't set it).

Edge cases to verify: don't break the normal default behavior when cleaned_data doesn't contain the field; ensure widgets like CheckboxInput still behave correctly; add/adjust tests.