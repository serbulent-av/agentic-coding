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
diff --git a/django/forms/models.py b/django/forms/models.py
index 5edbbd376f..211be56d49 100644
--- a/django/forms/models.py
+++ b/django/forms/models.py
@@ -48,7 +48,7 @@ def construct_instance(form, instance, fields=None, exclude=None):
             continue
         # Leave defaults for fields that aren't in POST data, except for
         # checkbox inputs because they don't appear in POST data if not checked.
-        if (f.has_default() and
+        if (f.has_default() and f.name not in cleaned_data and
                 form[f.name].field.widget.value_omitted_from_data(form.data, form.files, form.add_prefix(f.name))):
             continue
         # Defer saving file-type fields until after the other fields, so a

```
A senior reviewer (Opus 4.8) gave this feedback — address ALL of it:
VERDICT: REVISE

The candidate's condition `f.name not in cleaned_data` is wrong. When a field belongs to the form (which it does for fields in this loop), `f.name` will almost always be present in `cleaned_data`âeven when the value was omitted from POST data, `cleaned_data` still contains the field's empty/default-cleaned value. So:

- `f.name not in cleaned_data` evaluates to False in the normal omitted case, meaning the `continue` is skipped and the empty cleaned value gets written, **overriding the model default**. This breaks the existing, intended behavior where omitted fields should keep their model defaults.

Root cause/fix location is right (`construct_instance()` in `django/forms/models.py`), but the discriminating condition should be based on whether the cleaned value is actually empty, not on key presence. Use something like:

```python
if (
    f.has_default()
    and form[f.name].field.widget.value_omitted_from_data(form.data, form.files, form.add_prefix(f.name))
    and cleaned_data.get(f.name) in form[f.name].field.empty_values
):
    continue
```

This way:
- Field omitted and cleaned value empty â keep the model default (preserves current behavior).
- Field omitted from data but `clean()`/`clean_<field>` set a non-empty value in `cleaned_data` â that value overrides the default (fixes the issue).

Edge cases to confirm: a field whose intentionally-set override value happens to be an empty value won't override the defaultâthis matches Django's accepted resolution, so it's acceptable, but be aware of it.
Produce a corrected, complete solution.
---
