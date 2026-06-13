model_to_dict() should return an empty dict for an empty list of fields.
Description
	
Been called as model_to_dict(instance, fields=[]) function should return empty dict, because no fields were requested. But it returns all fields
The problem point is
if fields and f.name not in fields:
which should be
if fields is not None and f.name not in fields:
PR: ​https://github.com/django/django/pull/11150/files


---
## Implementation plan (from a senior Opus 4.8 planner — follow these steps)
Root cause: model_to_dict(instance, fields=[]) returns all fields because an empty list is falsy.
Plan:
1. Edit django/forms/models.py, function model_to_dict.
2. Change the guard `if fields and f.name not in fields:` to `if fields is not None and f.name not in fields:`.
3. Verify: model_to_dict(instance, fields=[]) == {} while fields=None still returns all fields.
---


---
## YOUR PREVIOUS ATTEMPT WAS REVIEWED
Your previous patch:
```diff
diff --git a/django/forms/models.py b/django/forms/models.py
index d157c291ef..fadac848d0 100644
--- a/django/forms/models.py
+++ b/django/forms/models.py
@@ -83,7 +83,7 @@ def model_to_dict(instance, fields=None, exclude=None):
     for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
         if not getattr(f, 'editable', False):
             continue
-        if fields and f.name not in fields:
+        if fields is not None and f.name not in fields:
             continue
         if exclude and f.name in exclude:
             continue
@@ -431,7 +431,7 @@ class BaseModelForm(BaseForm):
         for f in chain(opts.many_to_many, opts.private_fields):
             if not hasattr(f, 'save_form_data'):
                 continue
-            if fields and f.name not in fields:
+            if fields is not None and f.name not in fields:
                 continue
             if exclude and f.name in exclude:
                 continue

```
A senior reviewer (Opus 4.8) gave this feedback — address ALL of it:
VERDICT: REVISE

The first hunk (model_to_dict in `django/forms/models.py`) is correct and exactly matches the fix the issue requests.

However, the second hunk modifies `construct_instance` (around line 431), which is out of scope for this issue. The issue and the referenced PR (#11150) only change `model_to_dict`. The semantics of `fields` in `construct_instance` are differentâan empty `fields` list there historically means "no fields restriction applied the same way," and flipping it to `fields is not None` changes behavior for callers (e.g., `_post_clean`/save logic) that may pass an empty list, potentially causing m2m/private fields to be silently skipped. That is a behavior change not justified by the issue and could introduce a regression.

Action: drop the second hunk and keep only the `model_to_dict` change. Verify that `model_to_dict(instance, fields=[]) == {}` and `fields=None` still returns all fields, while `construct_instance` behavior remains untouched.
Produce a corrected, complete solution.
---
