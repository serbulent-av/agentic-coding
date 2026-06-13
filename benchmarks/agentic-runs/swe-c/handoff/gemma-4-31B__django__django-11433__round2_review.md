VERDICT: APPROVED

This matches the upstream Django fix exactly. The added condition `cleaned_data.get(f.name) in form[f.name].field.empty_values` ensures the default is only kept when the cleaned value is empty, allowing a non-empty `cleaned_data` value to override the model default while preserving the original behavior for truly omitted/empty fields.