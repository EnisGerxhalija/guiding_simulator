# Notebooks

Notebooks are for exploring, plotting and explaining. Logic you want to reuse
belongs in `src/my_project/`, where it can be tested and imported from
anywhere.

- **Name** notebooks with a number and a purpose: `01_quicklook.ipynb`,
  `02_fit_comparison.ipynb`.
- **Kernel:** run `make kernel` once, then choose "Python (my-project)" so the
  notebook uses this project's `.venv`.
- **Autoreload:** start with the cell from `01_quicklook.ipynb`, so edits to
  the package are picked up without restarting the kernel.
- **Paths:** use `load_settings()` rather than hard-coded paths; it finds the
  project root and `.env` even though notebooks run from this folder.
- **Outputs are stripped on commit** by the `nbstripout` pre-commit hook. This
  keeps diffs readable and stops results or secrets leaking into git. Save
  figures you want to keep to `outputs/`.
- **Restart & Run All** should work. If a notebook only works when cells run in
  a particular order, move that logic into the package.
