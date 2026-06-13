VERDICT: REVISE

The patch references `FigureBase` but does not import it. legend.py only imports `Figure` (via `from matplotlib.figure import Figure`), so `isinstance(parent, (Figure, FigureBase))` will raise `NameError: name 'FigureBase' is not defined`.

Fix:
- Add `FigureBase` to the import in lib/matplotlib/legend.py (e.g. `from matplotlib.figure import Figure, FigureBase`).
- Since `Figure` is a subclass of `FigureBase`, you can simplify the check to just `isinstance(parent, FigureBase)`.

Also consider checking `set_figure(parent)` works correctly for a SubFigure parent (the existing code sets the figure to `parent`, which should be fine), and verify the reproduction snippet runs.