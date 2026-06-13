Allow `cleaned_data` to overwrite fields' default values.
Description
	
See comments here: ​https://github.com/django/django/pull/7068/files#r289432409
Currently, when submitting a form, if 'some_field' isn't in the data payload (e.g. it wasn't included in the form, perhaps because its value is derived from another field), and 'some_field' has a default value on the model, it cannot be overwritten with 'self.cleaned_data'.
This does not really follow the paradigm of modifying data in 'cleaned_data'. It requires the user to copy and overwrite the raw data submitted with the form.


---
## Implementation plan (from a senior Opus 4.8 planner — follow these steps)
Root cause: construct_instance() in django/forms/models.py skips fields that are absent from the submitted data when the model field has a default, so cleaned_data cannot override the default.
Plan:
1. In construct_instance(), the loop skips a field when form field value is omitted from data AND f.has_default(). Change it so a value explicitly present in form.cleaned_data is still applied even if the model field has a default.
2. Concretely: only `continue` on the omitted-and-has-default branch when the field name is NOT in cleaned_data (or its cleaned value equals the initial/empty). Apply cleaned_data[f.name] otherwise.
3. Verify: a form that omits a field from data but sets it in cleaned_data writes that value, overriding the model default.
---


---
## YOUR PREVIOUS ATTEMPT WAS REVIEWED
Your previous patch:
```diff

```
A senior reviewer (Opus 4.8) gave this feedback — address ALL of it:
VERDICT: REVISE

The patch is empty. No changes were made to `construct_instance()` in `django/forms/models.py`.

Implement the fix per the plan: in the loop, the current condition skips fields where the value was omitted from the data and the model field has a default. Change it so that when `f.name` is present in `form.cleaned_data`, the cleaned value is still applied. Specifically, only `continue` when `f.has_default()` AND `form[f.name].field.widget.value_omitted_from_data(...)` AND `f.name not in cleaned_data` (i.e., cleaned_data didn't set it).

Edge cases to verify: don't break the normal default behavior when cleaned_data doesn't contain the field; ensure widgets like CheckboxInput still behave correctly; add/adjust tests.
Produce a corrected, complete solution.
---
