# Methods

## Methods Section (5 points)

This section includes exploration results, preprocessing steps, and models chosen in the order they were executed. Describe the parameters chosen. Create sub-sections for each step:

- **Data Exploration**
- **Preprocessing** (using Spark)
- **Model 1** (your first distributed model)
- **Model 2** (PCA/SVD + clustering or supervised)

Include code blocks using markdown: `` ```python ... ``` ``

*Note: A methods section does not include "why"—the reasoning goes in the Discussion section. This is just a summary of your methods.*

## Notebooks

Analysis notebooks live at the **repository root** (not in a `notebooks/` folder). In the left sidebar, open the **Notebooks** section for the full pipeline in execution order.

| Step | Notebook |
|------|----------|
| Environment setup | `expanse-env.ipynb` |
| Data extraction | `data-extraction-all-col.ipynb` |
| Data exploration | `data-exploration.ipynb` |
| Figures / EDA plots | `data-plots.ipynb` |
| Preprocessing (Spark) | `data-preprocessing.ipynb` |
| Model 1 — EDUC classifier | `data-modeling.ipynb` |
| Model 1 — income regressor | `data-modeling-income.ipynb` |
| Speedup analysis | `speedup-analysis.ipynb` |
| Model 2 — PCA / second model | `data-second-model.ipynb` (add to Notebooks when at repo root) |
