#!/usr/bin/env python3
"""
MS4 extra credit (Option B): avg(INCTOT) by STATEFIP in Spark and Ray.
Run 1 = warmup; reported average = runs 2-3 (same as speedup-analysis.ipynb).
"""

import argparse
import os
import time

RUNS = 3
NUM_CPUS = int(os.environ.get("SLURM_CPUS_PER_TASK", 8))


def spark_task(parquet_path: str) -> None:
    from pyspark.sql import SparkSession, functions as F

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


def ray_task(parquet_path: str) -> None:
    import ray
    import ray.data as rd

    ray.init(num_cpus=NUM_CPUS, ignore_reinit_error=True)
    rd.read_parquet(parquet_path).groupby("STATEFIP").mean(on=["INCTOT"]).count()
    ray.shutdown()


def bench(label: str, fn) -> float:
    print(f"=== {label} ===")
    times = []
    for i in range(RUNS):
        t0 = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        tag = " (warmup - discard)" if i == 0 else ""
        print(f"run {i + 1}: {elapsed:.2f} sec{tag}")

    avg = sum(times[1:]) / len(times[1:])
    const = "T_SPARK" if label == "Spark" else "T_RAY"
    print(f"{const} (avg runs 2-3) = {avg:.2f} sec\n")
    return avg


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=os.environ.get("PARQUET_PATH", "data/final_preprocessed"))
    p.add_argument("--framework", choices=("spark", "ray", "both"), default="both")
    args = p.parse_args()

    path = os.path.abspath(args.data)
    if not os.path.isdir(path):
        raise SystemExit(f"Data path not found: {path}")

    print(f"PARQUET_PATH = {path}")
    print("Task: groupBy STATEFIP -> avg(INCTOT)")
    print(f"Ray num_cpus = {NUM_CPUS}\n")

    t_spark = t_ray = None
    if args.framework in ("spark", "both"):
        t_spark = bench("Spark", lambda: spark_task(path))
    if args.framework in ("ray", "both"):
        t_ray = bench("Ray", lambda: ray_task(path))

    if t_spark is not None and t_ray is not None:
        faster = "Spark" if t_spark < t_ray else "Ray"
        ratio = max(t_spark, t_ray) / min(t_spark, t_ray)
        print(f"{faster} faster by ~{ratio:.2f}x")


if __name__ == "__main__":
    main()
