# Notebooks

Notebooks are for exploring, plotting and explaining. Code you want to reuse
belongs in `src/guiding_simulator/`, where it can be tested and imported from
anywhere.

- **Name** notebooks with a number and a purpose, e.g. `01_quicklook.ipynb`.
- **Python (kernel):** choose the project's `.venv`, so the notebook can
  import `guiding_simulator`.
- **Pick up code changes** without restarting by running this first:

  ```python
  %load_ext autoreload
  %autoreload 2
  ```

- **Restart & Run All** should work. If a notebook only works when cells run
  in a particular order, move that logic into `src/`.
- **Save figures** you want to keep in `outputs/`.
