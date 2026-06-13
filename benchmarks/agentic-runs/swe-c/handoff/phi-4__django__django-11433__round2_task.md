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
Produce a corrected, complete solution.
---
