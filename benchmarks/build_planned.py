import json, os
from datasets import load_dataset, Dataset

# Plans authored by Opus 4.8 (this session) from problem_statement ONLY.
# No gold patch / test_patch / FAIL_TO_PASS were consulted. Grounded in the issue text
# + general knowledge of these libraries. This is the "planner" half of the experiment.
PLANS = {
"astropy__astropy-8707": """Root cause: Header.fromstring (astropy/io/fits/header.py) and Card.fromstring (astropy/io/fits/card.py) assume a text `str` and break on Python-3 `bytes`.
Plan:
1. In Header.fromstring(cls, data, sep=''): at the top, if isinstance(data, bytes): decode it, e.g. data = data.decode('ascii'). Keep sep handling consistent (decode sep too if bytes).
2. Do the same guard at the start of Card.fromstring(cls, image): if isinstance(image, bytes): image = image.decode('ascii').
3. Verify: Header.fromstring(b'...80-char cards...') works identically to the str version; add no new public API.""",

"django__django-11163": """Root cause: model_to_dict(instance, fields=[]) returns all fields because an empty list is falsy.
Plan:
1. Edit django/forms/models.py, function model_to_dict.
2. Change the guard `if fields and f.name not in fields:` to `if fields is not None and f.name not in fields:`.
3. Verify: model_to_dict(instance, fields=[]) == {} while fields=None still returns all fields.""",

"django__django-11433": """Root cause: construct_instance() in django/forms/models.py skips fields that are absent from the submitted data when the model field has a default, so cleaned_data cannot override the default.
Plan:
1. In construct_instance(), the loop skips a field when form field value is omitted from data AND f.has_default(). Change it so a value explicitly present in form.cleaned_data is still applied even if the model field has a default.
2. Concretely: only `continue` on the omitted-and-has-default branch when the field name is NOT in cleaned_data (or its cleaned value equals the initial/empty). Apply cleaned_data[f.name] otherwise.
3. Verify: a form that omits a field from data but sets it in cleaned_data writes that value, overriding the model default.""",

"matplotlib__matplotlib-20859": """Root cause: Legend.__init__ (lib/matplotlib/legend.py ~L437) only accepts an Axes or a Figure parent; a SubFigure is a FigureBase, not Figure, so it raises 'Legend needs either Axes or Figure as parent'.
Plan:
1. In lib/matplotlib/legend.py import FigureBase from matplotlib.figure.
2. In Legend.__init__, change the parent isinstance check from `isinstance(parent, Figure)` to `isinstance(parent, FigureBase)` (keep the Axes branch).
3. Verify: subfig = plt.figure().subfigures(); ax=subfig.subplots(); ax.plot(...,label='t'); subfig.legend() works.""",

"matplotlib__matplotlib-22865": """Root cause: with drawedges=True and extend='both', the colorbar's dividers (separating lines) are drawn only for the inner solid boundaries, omitting the two extension triangles at the extremities.
Plan:
1. Edit lib/matplotlib/colorbar.py where self.dividers (a LineCollection) is built (in _add_solids / _do_extends).
2. When self.drawedges is True, include the extremity boundaries in the divider segments when extend is 'min'/'max'/'both' (i.e. add the start and/or end edge so all color boundaries, including the extended ends, get a line).
3. Verify: the repro figure shows black dividing lines at both extended ends.""",

"pydata__xarray-2905": """Root cause: as_compatible_data() in xarray/core/variable.py (~L641) does data = getattr(data, 'values', data), which unwraps ANY object exposing a `.values` attribute, corrupting object-dtype assignments (e.g. a HasValues instance becomes 5).
Plan:
1. In as_compatible_data(), restrict the `.values` unwrapping to genuine array-like containers (pandas/xarray types already handled above), not arbitrary Python objects.
2. Concretely: only extract `.values` when isinstance(data, (pd.Series, pd.DataFrame, pd.Index, Variable/DataArray))-style types; otherwise leave the object as-is so it is stored in the object array.
3. Verify: assigning HasValues() via .loc keeps the instance (object dtype), while pandas/xarray inputs still unwrap.""",

"pydata__xarray-4687": """Root cause: xr.where() (xarray/core/computation.py) calls apply_ufunc without keep_attrs, so attributes are dropped.
Plan:
1. Add a keep_attrs parameter to where(cond, x, y, keep_attrs=None).
2. If keep_attrs is None, resolve from xarray's global option (_get_keep_attrs(default=False)). Pass keep_attrs through to apply_ufunc(...). When keeping attrs, propagate the attrs of x (the second arg) to the result.
3. Verify: xr.where(data==1, 5, 0, keep_attrs=True) preserves data.attrs; default behaviour unchanged unless global option set.""",

"scikit-learn__scikit-learn-10844": """Root cause: fowlkes_mallows_score in sklearn/metrics/cluster/supervised.py computes tk / np.sqrt(pk * qk); pk*qk overflows int32 for large inputs, producing a RuntimeWarning and nan.
Plan:
1. Replace `return tk / np.sqrt(pk * qk) if tk != 0. else 0.` with a mathematically equal but overflow-safe form: `return np.sqrt(tk / pk) * np.sqrt(tk / qk) if tk != 0. else 0.`.
2. Verify: large pk,qk no longer warn/overflow and the score matches the original for normal inputs.""",

"scikit-learn__scikit-learn-13439": """Root cause: Pipeline supports slicing/indexing but has no __len__, so len(pipe) and pipe[:len(pipe)] fail.
Plan:
1. In sklearn/pipeline.py, class Pipeline, add: def __len__(self): \"\"\"Returns the length of the Pipeline\"\"\" return len(self.steps).
2. Verify: len(Pipeline([...])) equals number of steps and pipe[:len(pipe)] works.""",

"sphinx-doc__sphinx-10673": """Root cause: putting genindex/modindex/search in a toctree warns 'toctree contains reference to nonexisting document' because these are generated pages without a source document.
Plan:
1. In sphinx/directives/other.py (TocTree directive parse_content) where each entry's docname is validated, special-case the builtin pages {'genindex','modindex','search'} so they are accepted as valid toctree entries instead of emitting the 'nonexisting document' warning.
2. Add them as explicit toctree entries (with their standard titles) so links resolve.
3. Verify: a toctree listing genindex/modindex/search builds with no warning and produces working links.""",

"sphinx-doc__sphinx-11510": """Root cause: the 'source-read' event is emitted for top-level documents but not for content pulled in by the include directive, so extensions that rewrite source don't affect included text.
Plan:
1. Find Sphinx's include handling (the include directive in sphinx/directives/other.py / docutils Include override, or where included file content is read).
2. After reading the included file's text and before parsing, emit the 'source-read' event (app.events.emit('source-read', docname, arg_source_list)) so the content passes through the same rewriting as normal documents, then use the (possibly modified) source.
3. Verify: the repro extension replacing &REPLACE_ME; now also replaces it inside the included file in the built HTML.""",

"sympy__sympy-13372": """Root cause: in sympy/core/evalf.py, evalf()'s if/elif chain that assigns reprec/imprec has no final else, so for unsupported funcs (e.g. Max) reprec/imprec are referenced before assignment -> UnboundLocalError (order-dependent via evalf_mul).
Plan:
1. In evalf(), locate the elif clauses that set reprec and imprec (around the re/im handling, ~L1308).
2. Add a trailing `else: raise NotImplementedError` so an unsupported argument raises NotImplementedError (which the caller already handles) instead of leaving reprec/imprec unbound.
3. Verify: both Mul(x, Max(0,y), evaluate=False).evalf() and Mul(Max(0,y), x, evaluate=False).evalf() no longer raise UnboundLocalError.""",
}

pilot = [l.strip() for l in open("repo/benchmarks/agentic-runs/swe-verified/pilot_ids.txt")]
assert set(pilot) == set(PLANS), (set(pilot) ^ set(PLANS))

ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
rows = [dict(r) for r in ds if r["instance_id"] in set(pilot)]
NOTE = ("\n\n---\n## Implementation plan (from a senior Opus 4.8 planner — follow these steps)\n"
        "A senior engineer analyzed this issue and produced the plan below. Use it to go "
        "straight to the right file(s) and change. You still must implement and verify it.\n\n")
for r in rows:
    r["problem_statement"] = r["problem_statement"] + NOTE + PLANS[r["instance_id"]] + "\n---\n"

os.makedirs("planned_pilot", exist_ok=True)
Dataset.from_list(rows).to_parquet("planned_pilot/test-00000-of-00001.parquet")
with open("repo/benchmarks/agentic-runs/swe-verified/plans_pilot.jsonl","w") as f:
    for iid in pilot:
        f.write(json.dumps({"instance_id":iid,"plan":PLANS[iid]})+"\n")
print(f"built planned_pilot/ ({len(rows)} instances) and plans_pilot.jsonl")

# verify load_dataset can read it the same way the runner does
test = load_dataset("planned_pilot", split="test")
print("load_dataset('planned_pilot', split='test') ->", len(test), "rows; fields ok:",
      all(k in test.column_names for k in ["instance_id","problem_statement","base_commit","repo"]))
print("sample injected task tail:\n", test[0]["problem_statement"][-300:])
