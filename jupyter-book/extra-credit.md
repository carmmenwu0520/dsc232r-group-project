# Extra Credit: Spark vs Ray

For MS4 extra credit we ran the same data task in Spark and Ray, timed both, and compared the results. Our project already runs on Spark end to end. [data-preprocessing.ipynb](../data-preprocessing.ipynb) saves to parquet, Model 1 trains in [data-modeling.ipynb](../data-modeling.ipynb), and [speedup-analysis.ipynb](../speedup-analysis.ipynb) times RF fit on the same data with the same warmup convention (run 1 discarded, avg runs 2-3). This extra credit task adds Ray on a group-by task and we compare frameworks. The code can be found in [framework-comparison.ipynb](../framework-comparison.ipynb).

## Part 1: Implementation

We picked Option B: averaging INCTOT by STATEFIP (average income by state) on data/final_preprocessed. Same aggregation idea as the income-by-state plot in data-plots.ipynb.

| Framework | Implementation |
|-----------|----------------|
| Spark | read parquet, group by STATEFIP, average INCTOT, count |
| Ray | read parquet, groupby STATEFIP, mean on INCTOT, count |

We ran `scripts/framework_comparison.py` on Expanse via SSH and `scripts/run_framework_comparison.sh`.

Expanse setup:

- shared partition, 8 CPUs, 128 GB (srun --cpus-per-task=8 --mem=128G)
- container: ~/esolares/singularity/spark_raydp.sif
- module load singularitypro, then python3 inside the container

## Part 2: Performance Comparison

### Timings

Same warmup convention as speedup analysis: run 1 is the first load on the node and we discard it; the reported number is avg runs 2-3.

| Framework | Run 1 | Run 2 | Run 3 | Avg (runs 2-3) |
|-----------|------:|------:|------:|---------------:|
| Spark | 66.90 s (warmup) | 2.06 s | 1.56 s | 1.81 s |
| Ray | 90.56 s (warmup) | 86.90 s | 86.73 s | 86.82 s |

Here we see Spark about 48x faster on avg runs 2-3 (1.81 s vs 86.82 s).

While looking at Run 1 only (first read): Spark 66.90 s, Ray 90.56 s, about 1.35x apart. They are much closer, since they deal with the loading costs.

### Comparison table

| Metric | Spark | Ray |
|--------|------:|----:|
| Execution time (avg runs 2-3) | 1.81 s | 86.82 s |
| Execution time (run 1, warmup) | 66.90 s | 90.56 s |
| Lines of code (aggregation only) | ~3 | ~3 |
| Memory (peak) | TBD | TBD |
| Ease of implementation (1-5) | 4 | 3 |

## Part 3: Analysis

### 1. Which framework was faster? By how much?

Spark was faster. On avg runs 2-3, Spark was about 48x faster (1.81 s vs 86.82 s). After the first read, Spark dropped to about 2 seconds on runs 2 and 3 because the parquet was cached on the node. Ray stayed around 87 seconds each run.

### 2. Which was easier to implement? Why?

Spark was slightly easier (4/5 vs 3/5). The aggregation matches data-plots and the rest of our pipeline. Ray needed ray.init and ray.shutdown each timed run on top of the Ray Data API. Spark matched what we already had in the project.

### 3. For your specific use case, which would you choose?

Spark for the pipeline we built - extraction, preprocessing, modeling, and speedup analysis on 67M rows. This group-by also ran faster on Spark in our timed runs.

Ray could still make sense later for modeling experiments like hyperparameter tuning or many parallel training trials. Spark owns what we have now; Ray is worth a look for that kind of work.

<!-- ## Extra Credit: Framework Comparison (5 points)

Implement a data processing task using **both Spark and Ray**, then compare their performance.

### 1. Implementation (2 points)

Choose one task from your project and implement equivalent functionality in both frameworks:

- **Option A:** Compute statistics on your dataset (mean, std, percentiles)
- **Option B:** Perform a group-by aggregation
- **Option C:** Train an XGBoost model on a subset of your data

### 2. Performance Comparison (2 points)

Create a table comparing:

- Execution time (average of 3 runs)
- Lines of code
- Memory usage (peak)

### 3. Analysis (1 point)

Answer these questions:

- Which framework was faster? By how much?
- Which was easier to implement? Why?
- For your specific use case, which would you choose?

See the [Framework Comparison Guide](https://github.com/ucsd-dsc232r/group-project/blob/main/Class16/09_framework_comparison.md) for detailed instructions. -->
