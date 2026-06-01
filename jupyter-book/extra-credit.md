# Extra Credit: Spark vs Ray

For the extra credit task we ran the same data task in Spark and Ray, timed both, and compared the results. Our project already runs on Spark end to end, so seeing the differences between these two frameworks will be compelling. We follow a similar structure as speedup-analysis.ipynb with the warmup convention (run 1 discarded, avg runs 2-3). The code can be found in [framework-comparison.ipynb](../framework-comparison.ipynb).

## Implementation

We picked Option B: averaging INCTOT by STATEFIP (average income by state).

| Framework | Implementation |
|-----------|----------------|
| Spark | read parquet, group by STATEFIP, average INCTOT, count |
| Ray | read parquet, groupby STATEFIP, mean on INCTOT, count |

**Spark**

```python
def spark_task(parquet_path: str) -> None:
    spark = (
        SparkSession.builder.appName("framework-comparison-spark")
        .config("spark.driver.memory", "2g")
        .config("spark.executor.memory", "18g")
        .config("spark.executor.instances", "7")
        .getOrCreate()
    )
    spark.read.parquet(parquet_path).groupBy("STATEFIP").agg(
        F.avg("INCTOT").alias("avg_income")
    ).count()
    spark.stop()
```

**Ray**

```python
def ray_task(parquet_path: str) -> None:
    ray.init(num_cpus=NUM_CPUS, ignore_reinit_error=True)
    rd.read_parquet(parquet_path).groupby("STATEFIP").mean(on=["INCTOT"]).count()
    ray.shutdown()
```

We ran scripts/framework_comparison.py on Expanse via SSH and scripts/run_framework_comparison.sh.

Expanse setup:

- shared partition, 8 CPUs, 128 GB (srun --cpus-per-task=8 --mem=128G)
- container: ~/esolares/singularity/spark_raydp.sif
- module load singularitypro, then python3 inside the container

## Performance Comparison

### Timings

```{note}
Timing convention matches speedup-analysis.ipynb: run 1 is warmup (first load on the node) and is discarded; reported times are the average of runs 2 and 3.
```

| Framework | Run 1 | Run 2 | Run 3 | Avg (runs 2-3) |
|-----------|------:|------:|------:|---------------:|
| Spark | 63.35 s (warmup) | 2.59 s | 2.06 s | 2.33 s |
| Ray | 91.04 s (warmup) | 87.84 s | 88.12 s | 87.98 s |

Spark was about 38x faster on avg runs 2-3 (2.33 s vs 87.98 s).

### Page cache note

Spark run 1 took about 63 seconds reading parquet from disk. Runs 2 and 3 were around 2 seconds because the data was already in the OS page cache on the compute node. Ray stayed around 87 seconds every run. On repeat work in a session, Spark was much faster once the data was loaded.

### Comparison table

| Metric | Spark | Ray |
|--------|------:|----:|
| Execution time (avg runs 2-3) | 2.33 s | 87.98 s |
| Execution time (run 1, warmup) | 63.35 s | 91.04 s |
| Lines of code (aggregation only) | ~3 | ~3 |
| Memory (peak) | 43,208 kbytes (~42 MB) | 677,200 kbytes (~661 MB) |
| Ease of implementation (1-5) | 4 | 3 |

We measured peak memory with GNU time -v on Expanse (one run per framework). Ray used much more than Spark in our runs, about 661 MB vs 42 MB.

```{important}
All runs used the same Expanse setup (8 CPUs, 128 GB, shared partition). Spark's faster repeat runs also reflect OS page cache after the first read; Ray stayed near ~88 s each run.
```

## Analysis

### 1. Which framework was faster? By how much?

Spark was faster. On avg runs 2-3, Spark was about 38x faster (2.33 s vs 87.98 s). After the first read, Spark dropped to about 2 seconds on runs 2 and 3 because the parquet was cached on the node. Ray stayed around 87 seconds each run.

### 2. Which was easier to implement? Why?

Spark was slightly easier (4/5 vs 3/5). The aggregation matches data-plots and the rest of our pipeline. Ray needed ray.init and ray.shutdown each timed run on top of the Ray Data API. Spark matched what we already had in the project.

### 3. For your specific use case, which would you choose?

Spark for the pipeline we built - extraction, preprocessing, modeling, and speedup analysis on 67M rows. This group-by also ran faster on Spark in our timed runs.

Ray could still make sense for modeling experiments like hyperparameter tuning or many parallel training trials. It's worth exploring a hybrid approach in future iterations of this project.

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
