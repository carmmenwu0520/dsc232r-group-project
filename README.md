# US Census Income and Education Analysis

Group project for DSC 232R: Big Data Analytics Using Spark

![GitHub last commit](https://img.shields.io/github/last-commit/jedwin4321/dsc232r-group-project)
![GitHub repo size](https://img.shields.io/github/repo-size/jedwin4321/dsc232r-group-project)

> [!IMPORTANT]
> **[Read the full project report here](https://jedwin4321.github.io/dsc232r-group-project/)**  
> Navigable write-up with Methods, Results, Discussion, and notebooks. This README is the same content.

---

# Introduction

> **[View the Introduction on GitHub Pages →](https://jedwin4321.github.io/dsc232r-group-project/)**

In this project, we analyzed data from the [IPUMS USA dataset](https://usa.ipums.org/usa/), which provides harmonized U.S. census and survey data across multiple years. We then constructed a dataset spanning from 2001 to 2024. The data includes variables such as total income, educational attainment, geographic region or state, survey year, age, sex, and employment status, with a total size exceeding 65 GB with millions of records. **Our research investigates how the relationship between education and income varies across regions and time, and to what extent education predicts income across different geographic regions.**

One of the main reasons we were interested in this project stems from how researchers routinely work with census data to study how education, place, and earnings line up across the country. The models these researchers make are meant to inform people (i.e. lawmakers, school board officials, you, and many more) in making real decisions. A good predictive model could support people make decisions like whether additional education is right for them by comparing if there's an association with higher pay in a given state or year, and where workforce or training efforts should focus when local labor markets look out of step with national trends.

Due to the large scale and complexity of the data, which includes millions of records across multiple years, we relied on Apache Spark on SDSC Expanse (8 cores, 128 GB RAM per job). Even then, full-table preprocessing, feature encoding, and Random Forest training often ran for hours and sometimes failed when memory filled up. A laptop or single-node setup would have been far slower or effectively impossible for the same work at this scale.

> [!IMPORTANT]
> At this scale, distributed Spark on Expanse was required for full-table pipelines. Jobs could run for hours and still hit memory limits on 128 GB nodes.

## Dataset Linkage

- Primary dataset: [IPUMS USA](https://usa.ipums.org/usa/)
- Data access portal: [IPUMS USA Extract System](https://usa.ipums.org/usa-action/variables/group)
- Citation: Steven Ruggles, Sarah Flood, Matthew Sobek, Daniel Backman, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, Renae Rodgers, Jonathan Schroeder, and Kari C.W. Williams. *IPUMS USA: Version 16.0* [dataset]. Minneapolis, MN: IPUMS, 2025. [https://doi.org/10.18128/D010.V16.0](https://doi.org/10.18128/D010.V16.0)

## Team Contact

For project questions, reach out to:

- Edwin Vargas Navarro: [evargasnavarro@ucsd.edu](mailto:evargasnavarro@ucsd.edu)
- Evan Lim: [e2lim@ucsd.edu](mailto:e2lim@ucsd.edu)
- Jiamin Wu: [jiw294@ucsd.edu](mailto:jiw294@ucsd.edu)
- Noopur Chowdary: [nchowdary@ucsd.edu](mailto:nchowdary@ucsd.edu)

---

# Methods

> **[View the Methods on GitHub Pages →](https://jedwin4321.github.io/dsc232r-group-project/methods/)**

## SDSC Expanse Environment Setup 

The very first step we had to consider for our project was our expanse envirnoment setup. For our setup, we requested 8 cores and 128GB total memory as shown below:

![jupyter-session](images/jupyter-session.png)

Now in our JupyterLab session, we can do the following:

```python
spark = SparkSession.builder \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "18g") \
    .config("spark.executor.instances", 7) \
    .getOrCreate()
```

Formula for the above:

- Executor instances = Total Cores - 1
- Executor memory = (Total Memory - Driver Memory) / Executor Instances

Our calculation:

- Total Cores = `8`
- Total Memory = `128GB`
- Driver Memory = `2GB`
- Executor Instances = `8 - 1 = 7`
- Executor Memory = `(128 - 2) / 7 = 18GB` 


### SparkSession Configuration and Justification

When going through [Spark on HPC Best Practices: Example 3](https://github.com/ucsd-dsc232r/group-project/blob/main/SPARK_HPC_BEST_PRACTICES.md#example-3-8-cores-with-128gb-ram-high-memory), this setup most closely aligned with our needs. Since our data is 65GB, it's a fair amount above the 50GB that is mentioned in this example. 

Spark executor/config evidence during data loading:

![spark-ui](images/spark-config.png)

## Speedup Analysis

After settling on the executor configuration above, we measured how much that distributed setup actually buys us. Using the same Spark job that trains our model, we timed a baseline run on 1 executor against our full 7-executor configuration. Following the warmup convention, the first run is discarded as JVM/configuration warmup and we average the next two runs.

| Executors | Time (sec) | Speedup | Efficiency |
|---|---:|---:|---:|
| 1 | 7593.4 | 1.00x | 100% |
| 7 | 1025.7 | 7.40x | 105.8% |

**Metrics:**

* T_1 = 7593.41s
* T_7 = 1025.67s
* speedup = T_1/T_7 = **7.40x**
* efficiency = speedup/7 = **105.8%**

**Amdahl:** Our estimated parallelizable fraction is p = 7 x 6.40 / (7.40 x 6) = 44.8 / 44.4 ~= **1** (from measured speedup). The theoretical speedup at n = 7 with this p is **~7.40x**, and we achieved essentially 100% of that limit. Training time dropped from ~2.1 hours (1 executor) to ~17 minutes (7 executors), showing the work benefits from distributed Spark executors on this dataset.

## Data Exploration

Now that we have finished our Expanse setup and know that it helps us work with big data, we can begin the exploration phase. We start by finding the number of columns and rows.

 ```python
row_count = df.count()
print("Number of Rows:", row_count)
column_count = len(df.columns)
print("Number of Columns:", column_count)
```


| Metric | Value |
|---|---:|
| Number of Rows | 67,125,780 |
| Number of Columns | 238 |


### Target Columns
Our columns of main interest are "YEAR", "STATEFIP", "SEX", "AGE", "RACE", "EDUC", and "INCTOT". EDUC and INCTOT are the major relavant columns to directly answer our abstract. YEAR will provide chronological information, STATEFIP will provide spatial information, and SEX, AGE, and RACE can provide further data partitioning to reveal trends and patterns on sex, age, and race.
The full dataset contains 238 columns, and complete descriptors for all variables are available in both [`usa_00001.xml`](usa_00001.xml) and the [IPUMS variable documentation website](https://usa.ipums.org/usa-action/variables/group).

- YEAR (Numerical): The year the data was collected.
- STATEFIP (Categorical): The US state the data was collected using the FIPS (Federal Information Processing Standards) coding scheme.
- SEX (Categorical): Whether the person was male or female
- AGE (Numerical): The person's age in years.
- RACE (Categorical): The person's race.
- EDUC (Categorical): The person's educational attainment.
- INCTOT (Numerical): The person's pre-tax total personal income (or loss).

All categorical variables have some numeric coding scheme which correspond with qualitative categories. These coding schemes and descriptions are found on the [IPUMS website](https://usa.ipums.org/usa-action/variables/group).


### Descriptive statistics for Numeric data
 ```python
described = df.select(["YEAR", "AGE", "INCTOT"]).describe()
```
| summary | YEAR | AGE | INCTOT |
|---|---:|---:|---:|
| count | 67,125,780 | 67,125,780 | 67,125,780 |
| mean | 2013.8564 | 40.7865 | 1,774,229.3693 |
| stddev | 6.3780 | 23.5751 | 3,777,923.4429 |
| min | 2001.0 | 0.0 | -19998.0 |
| max | 2024.0 | 97.0 | 9999999.0 |

Our dataset captures survey results between 2001 and 2024. Our age range is between 0 and 97 years old with an average age of approximately 41 years old. Since the maximum age is 97, there are no missing data because the assigned code for missing data is 999. According to the IPUMS website, for our dataset which covers 2001-2024, there are special codes to indicate certain circumstances for the `INCTOT` column:

- 0000000 = None
- 0000001 = $1 or break even (2000, 2005-onward ACS and PRCS)
- 9999999 = N/A
- 9999998 = Unknown

### Checking for Duplicates

 ```python
 distinct_counts = df.select(F.countDistinct("YEAR", "PERNUM", "SAMPLE", "SERIAL").alias("unique"))
 distinct_counts.show()
```


Due to the large size of the dataset, it's difficult to look for duplicate rows on all rows. Instead, we will rely on the PERNUM column which uniquely identifies a person. We will combine this with YEAR (since the same person can respond multiple times across years) to identify potential duplicates. Also, as advised by the IPUMS website: "When combined with SAMPLE and SERIAL, PERNUM uniquely identifies each person within the IPUMS." As a safety precaution, we will use all 4 columns to uniquely identify a person's survey response in order to identify duplicates.

| Metric | Value |
|---|---:|
| Unique (`YEAR`,`PERNUM`,`SAMPLE`,`SERIAL`) | 67,125,780 |
| Duplicates | 0 |

There are no duplicates.

### Counting Nulls

 ```python
all_null_counts = df.select([F.count(F.when(F.isnan(c) | F.col(c).isNull(), c)).alias(c) for c in df.columns])
all_null_counts.show(truncate=False)
```

| Column | Null count |
|---|---:|
| YEAR | 0 |
| STATEFIP | 0 |
| SEX | 0 |
| AGE | 0 |
| RACE | 0 |
| EDUC | 0 |
| INCTOT | 0 |

We can see that there are no null values in these columns. However, it remains to be seen if the unavailable data defined by the coding schemes (e.g. 99 for EDUC column) are present in the data. This will be known in the next few sections.

### Special-code check for `INCTOT`

| INCTOT value | count |
|---:|---:|
| 0.0 | 6,773,579 |
| -19998.0 | 196 |
| 1.0 | 6,266 |
| 9999999.0 | 11,690,872 |

There are multiple instances of 9999999, indicating missing data. There are no instances of 9999998, and there are a significant number of instances of 0. This is likely a nice round number that survey participants would use to indicate that they had no income that year. To a lesser degree, the same could be said about the number of instaces of 1. The relatively low count of -19998 instances indicate that this is simply a lower bound.

If we remove the instances of 9999999, the income distribution is:

| summary | INCTOT |
|---|---:|
| count | 55,434,908 |
| mean | 39,466.5038 |
| stddev | 59,723.0848 |
| min | -19998.0 |
| max | 1,945,000.0 |

The income distribution appears to be between -19998 and 1945000 dollars with a mean income of 39466.50 dollars.

### Checking for code-defined missing data in Categorical Data

 ```python
df.groupBy("YEAR").count().sort("YEAR").show(df.count(), truncate=False)
df.groupBy("STATEFIP").count().sort("STATEFIP").show(df.count(), truncate=False)
df.groupBy("SEX").count().sort("SEX").show(truncate=False)
df.groupBy("RACE").count().sort("RACE").show(truncate=False)
df.groupBy("EDUC").count().sort("EDUC").show(truncate=False)
```



There are code scheme defined codes for missing data in the EDUC (code 99), SEX (code 9), and STATEFIP (code 99) columns. We checked if there are any instances of this form of missing data using `.groupBy()` and `.count()`, but the tables in [`data-exploration.ipynb`](data-exploration.ipynb) reveal that these codes were not used. All data points of interest are present within these columns.



## Preprocessing Plan

Before analysis and modeling, the dataset was cleaned and transformed to improve data quality and prepare the data for machine learning and visualization tasks. Because the dataset contained approximately 67 million records and 238 variables, all preprocessing operations were performed using Spark.

### 1. Handling Missing Values

#### For numerical variables such as AGE and INCTOT:

Special missing-value codes were identified and replaced with null values.
The proportion of missing values was examined for each variable.
Missing values were imputed using appropriate summary statistics when necessary.
Variables with excessive missingness were evaluated before further analysis.

#### For categorical variables such as SEX, RACE, EDUC, and MARST:

Invalid or unknown category codes were identified and converted to null values.
Missing categories were retained or imputed depending on the analytical requirements.

### 2. Handling Data Imbalance
The distributions of key categorical variables were evaluated to determine the presence of class imbalance.
Variables examined included:
SEX
RACE
EDUC
STATEFIP
Category frequencies were calculated using Spark aggregation functions. The results were used to assess whether additional balancing techniques would be required during model development.

 ```python
# Designate placeholder values as missing flags to balance feature entries
df = df.replace(0, None, subset=["EMPSTAT", "CITIZEN", "MARRINYR"])

# Impute categorical variables with the mode
df = df.fillna(1, subset=["EMPSTAT", "MARRINYR"])
df = df.fillna(2, subset=["CITIZEN"])

# Impute continuous variables with the column mean
mean_val = df.select(F.mean("WKSWORK1")).collect()[0][0]
df = df.fillna(mean_val, subset=["WKSWORK1"])
```

### 3. Transformations

For numerical features like AGE and INCTOT:

- We applied scaling (normalization or standardization)

For categorical features like SEX, RACE, EDUC, and STATEFIP:

- We  encoded categories into model-ready numeric representations (for example, index encoding and one-hot style vectors when appropriate)

For feature engineering:

- We  created cleaned income features (for example, excluding special-code values from numeric summaries)
- We prepared derived grouping features for year and geography to support regional/time-based modeling
- We  mapped state codes (STATEFIP values such as 1-56, including 1-50 for U.S. states) to readable state names/labels for geographic visualization (e.g., choropleth maps)
- We created an inflation-adjusted income feature (for example, `INCTOT_adjusted`) by joining annual inflation/CPI values by `YEAR` and scaling `INCTOT` into comparable dollars

 ```python
# ### 3. Transformations

## For numerical features like AGE and INCTOT:
# We applied scaling (normalization or standardization)
from pyspark.ml.feature import StandardScaler, VectorAssembler

# Assemble continuous feature columns into temporary vector structures
assembler_inc = VectorAssembler(inputCols=["REALINCTOT"], outputCol="REALINCTOT_VEC")
df = assembler_inc.transform(df)

# Apply Z-score standardization to center the mean at 0 and scale variance to 1
scaler_inc = StandardScaler(inputCol="REALINCTOT_VEC", outputCol="REALINCTOT_Z", withStd=True, withMean=True)
df = scaler_inc.fit(df).transform(df)

assembler_age = VectorAssembler(inputCols=["AGE"], outputCol="AGE_VEC")
df = assembler_age.transform(df)

scaler_age = StandardScaler(inputCol="AGE_VEC", outputCol="AGE_Z", withStd=True, withMean=True)
df = scaler_age.fit(df).transform(df)

# Drop temporary intermediate vectors
df = df.drop("AGE_VEC", "REALINCTOT_VEC")


## For categorical features like SEX, RACE, EDUC, and STATEFIP:
# We encoded categories into model-ready numeric representations (for example, index encoding and one-hot style vectors when appropriate)
from pyspark.ml import Pipeline
from pyspark.ml.feature import OneHotEncoder, StringIndexer

# Build indexer and encoder pipelines for unranked categorical columns
pairs = [("STATENAME", "STATE_INDEX", "STATE_OH"), 
         ("SEXNAME", "SEX_INDEX", "SEX_OH"), 
         ("RACENAME", "RACE_INDEX", "RACE_OH")]
steps = []
for in_col, mid_col, out_col in pairs:
    steps.append(StringIndexer(inputCol=in_col, outputCol=mid_col))
    steps.append(OneHotEncoder(inputCol=mid_col, outputCol=out_col, dropLast=False))
    
pipeline = Pipeline(stages=steps)
df = pipeline.fit(df).transform(df)
df = df.drop("STATE_INDEX", "SEX_INDEX", "RACE_INDEX")

# For inherently ranked attributes (EDUC), map ordinals using adjusted clean indices
df = df.withColumn("EDUC", F.when(F.col("EDUC") >= 10, F.col("EDUC") - 1).otherwise(F.col("EDUC")))

## For feature engineering:
# We created cleaned income features (for example, excluding special-code values from numeric summaries)
# Exclude code-scheme defined missing markers (9999999.0) from raw total income
df = df.replace(9999999.0, None, subset=["INCTOT"])

# Adjust total nominal income for inflation to make values comparable across years
df = df.withColumn("REALINCTOT", F.col("INCTOT") * F.col("CPI99"))
df = df.drop("CPI99")


# We prepared derived grouping features for year and geography to support regional/time-based modeling
# Map numeric IPUMS geographic and demographic codes to descriptive strings
state_mapping = [F.lit(x) for item in statefip.items() for x in item]
df = df.withColumn("STATENAME", F.create_map(state_mapping)[F.col("STATEFIP")])

# Calculate yearly inflation-adjusted baselines and fill missing records conditionally by year group
income_averages = df.select("YEAR", "INCTOT").groupBy("YEAR").agg(F.avg("INCTOT").alias("INCTOT_AVG"))
income_averages_map = income_averages.select("YEAR", "INCTOT_AVG").rdd.collectAsMap()

for key, val in income_averages_map.items():
    df = df.withColumn("INCTOT", F.when((F.col("YEAR") == key) & (F.col("INCTOT").isNull()), val).otherwise(F.col("INCTOT")))

```

### 4. Spark Operations Planned for Preprocessing

Spark Operations Used

The preprocessing pipeline was implemented using Spark DataFrame operations and Spark ML transformers.

Key operations included:

withColumn()
when()
otherwise()
filter()
drop()
na.fill()
na.drop()
groupBy().count()
agg()
join()
StringIndexer
OneHotEncoder
VectorAssembler
StandardScaler
PCA
Outcome

The preprocessing stage produced a cleaned and transformed dataset suitable for modelling , visualization, dimensionality reduction, and machine learning. Missing values were handled appropriately, categorical variables were encoded, numerical variables were standardized, inflation-adjusted income measures were created, and additional engineered features were generated to improve analytical usefulness.


## Model 1 (First Distributed Model)

As an initial modeling approach, Random Forest algorithms were applied to both classification and regression tasks to establish strong baseline models and evaluate the predictive power of the demographic and socioeconomic features available in the dataset. Random Forest was selected because it is a robust ensemble learning technique that can capture complex, non-linear relationships while remaining relatively resistant to overfitting.

To investigate the impact of model complexity, two versions of Random Forest were trained for each task. The first model used numTrees=20 and maxDepth=10, while a second model with tuned hyperparameters used numTrees=30 and maxDepth=12. Performance was evaluated on training, validation, and test datasets.

### Random Forest Classifier (Multiclass Education Prediction)
We used a Random Forest Classifier to predict multiclass education levels (EDUC) using demographic and socioeconomic features such as income, age, sex, race, and state information
 Classification performance was evaluated using:
 1-Accuracy: The proportion of correctly classified observations.
 2-F1 Score: The harmonic mean of precision and recall, providing a balanced measure of classification performance.
 3- Weighted Precision: Precision averaged across all classes while accounting for class frequencies


### Supervised Feature Assembly & Dataset Splitting for classification
The target parameter was defined by mapping the educational column (EDUC) to a double precision label layout. Key independent features capturing scaled financial metrics, z-score scaled demographics, and one-hot encoded vector spaces (REALINCTOT_Z, AGE_Z, STATE_OH, SEX_OH, and RACE_OH) were isolated and combined into a singular unified sparse matrix via PySpark's VectorAssembler.Once assembled, the rows were distributed randomly into distinct processing subsets for training (70%), validation (15%), and testing (15%) splits leveraging a constant evaluation seed.

```python

# Format target label structure and select independent components
ml_df = df.select(F.col("EDUC").cast("double").alias("label"), "REALINCTOT_Z", "AGE_Z", "STATE_OH", "SEX_OH", "RACE_OH", "EDUCNAME")

# Structural consolidation of dimensions into a unified dense features column
assembler = VectorAssembler(inputCols=["REALINCTOT_Z", "AGE_Z", "STATE_OH", "SEX_OH", "RACE_OH"], outputCol="features")
ml_df = assembler.transform(ml_df)

# Perform distributed random splits across fixed random boundaries
train_df, val_df, test_df = ml_df.randomSplit([0.70, 0.15, 0.15], seed=SEED)

```
### Baseline Random Forest Classifier Training
A distributed RandomForestClassifier was initialized to serve as the initial pipeline baseline model. The model configuration constructed 20 distinct decision trees (numTrees=20) allowed to branch out to a localized vertical deep bound limit of 10 (maxDepth=10). This configuration provides a stable baseline for evaluating multiclass prediction capability across the transformed feature matrices.

```python
# Initialize and train the baseline Random Forest Classifier
rf = RandomForestClassifier(labelCol="label", featuresCol="features", predictionCol="prediction", numTrees=20, maxDepth=10, seed=SEED)
model_baseline = rf.fit(train_df)
```
### Hyperparameter Optimization
To optimize classification accuracy and control tree variance, a second, deeper model variant was initialized. The random forest configuration was manually optimized by scaling the ensemble size up to 30 decision trees (numTrees=30) and adjusting the information threshold boundaries down to an expanded structural maximum depth of 12 (maxDepth=12). This structural expansion allows individual nodes to form more precise non-linear decision splits.

```python
# Scale model hyperparameters to improve multi-class boundary limits
rf2 = RandomForestClassifier(labelCol="label", featuresCol="features", predictionCol="prediction", numTrees=30, maxDepth=12, seed=SEED)
model_rf_hp = rf2.fit(train_df)
```

### Distributed Multiclass Evaluation Matrix
Model performance was analyzed holistically by calculating metrics via PySpark’s MulticlassClassificationEvaluator. Performance bounds were verified uniformly against accuracy, Macro-F1 score, and weighted precision parameters across all partitions to monitor generalization characteristics and confirm the absence of overfitting.

```python
# Instantiate separate evaluation metrics targeting specific multi-class parameters
ev_acc = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
ev_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
ev_wp = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="weightedPrecision")

# Evaluate and diagnose out-of-sample metrics against target test features
pred = model_rf_hp.transform(test_df)
print("test_rf30_d12 Results -> Accuracy:", ev_acc.evaluate(pred), "| F1:", ev_f1.evaluate(pred))
```

 ### Random Forest Regressor
 We used a Random Forest Regressor to predict continuous income values (REALINCTOT) using demographic and socioeconomic variables such as age, education, sex, race, and state information. Random Forest Regression is an ensemble learning method that builds multiple decision trees and averages their predictions

### Baseline Random Forest Regressor Training
A distributed RandomForestRegressor pipeline was established to construct an initial ensemble baseline model for real income projection. The baseline pipeline was configured with 20 distinct decision trees (numTrees=20) capped at an individual maximum depth limit of 10 (maxDepth=10). This multi-tree ensemble forms the foundation for mapping continuous target variances across the integrated feature space.

```python
# Initialize and train the baseline Random Forest Regressor
rf = RandomForestRegressor(labelCol="label", featuresCol="features", predictionCol="prediction", numTrees=20, maxDepth=10, seed=42)
model_baseline = rf.fit(train_df)
```
### Hyperparameter Optimization
To capture deep, non-linear feature interactions and optimize residual errors, a second regression model variant was initialized. The parameters were scaled upwards to deploy 30 independent decision trees (numTrees=30) while simultaneously expanding the depth limit per tree down to 12 structural layers (maxDepth=12). This structural optimization allows the regression leaves to isolate more precise regional income variations.

```python
# Scale regression parameters to capture high-variance continuous boundaries
rf2 = RandomForestRegressor(labelCol="label", featuresCol="features", predictionCol="prediction", numTrees=30, maxDepth=12, seed=42)
model_rf_hp = rf2.fit(train_df)
```
### Distributed Continuous Regression Evaluation Matrix
The accuracy of the model projections was systematically measured across the train, validation, and test subsets using a matrix of typical continuous evaluation metrics: Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and the Coefficient of Determination ($R^2$).The hyperparameter-optimized architecture delivered steady, consistent optimization gains over the baseline run across all partitions, achieving an out-of-sample test $R^2$ score of approximately 0.254, confirming stable generalization characteristics without overfitting.

```python
# Initialize continuous performance evaluators
ev_rmse = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
ev_mae = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="mae")
ev_r2 = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="r2")

# Generate test predictions and compute out-of-sample metrics
pred = model_rf_hp.transform(test_df)
print("test_rf30_d12 Results -> RMSE:", ev_rmse.evaluate(pred), "| MAE:", ev_mae.evaluate(pred), "| R2:", ev_r2.evaluate(pred))
```



    
## Model 2 (PCA)


### Feature Expansion & Missing Data Imputation
Because Model 2 leverages Dimensionality Reduction (PCA), the feature space was expanded by extracting additional categorical columns from the original dataset (EMPSTAT, CITIZEN, WKSWORK1, MARRINYR, and HISPAN). This allows PCA to map a richer subset of features.
Before transforming the space, placeholder values representing missing flags (such as 0 for employment and marriage variables) were explicitly set to None. Missing entries in categorical attributes were imputed using their statistical mode (e.g., 1 for employment status, 2 for citizenship status), while continuous columns (WKSWORK1) were filled using their statistical mean.


```python
# Designate placeholder values as missing flags
df = df.replace(0, None, subset=["EMPSTAT", "CITIZEN", "MARRINYR"])

# Impute categorical variables with the mode
df = df.fillna(1, subset=["EMPSTAT", "MARRINYR"])
df = df.fillna(2, subset=["CITIZEN"])

# Impute continuous variables with the column mean
mean_val = df.select(F.mean("WKSWORK1")).collect()[0][0]
df = df.fillna(mean_val, subset=["WKSWORK1"])
```

### Categorical Encoding & Scaled Transformations
To prepare the dataset for PCA, numerical tracking attributes with disparate ranges were normalized using a MinMaxScaler. Ordinal transformations were applied directly to inherently ranked variables like education levels (EDUC). For unranked geographical and demographic indices (STATEFIP, SEX, RACE, and HISPAN), a processing pipeline involving StringIndexer and OneHotEncoder was utilized to prevent the model from inferring a false numerical hierarchy.
Additionally, because the target variable (REALINCTOT) suffered from a severe rightward skew, a signed logarithmic transformation (REALINCTOT_LOG) was implemented prior to calculating its final Z-score normalization.

```python


# Build the encoding pipeline for unranked categorical variables
pairs = [("STATENAME", "STATE_INDEX", "STATE_OH"), 
         ("SEXNAME", "SEX_INDEX", "SEX_OH"), 
         ("RACENAME", "RACE_INDEX", "RACE_OH")]
steps = []
for in_col, mid_col, out_col in pairs:
    steps.append(StringIndexer(inputCol=in_col, outputCol=mid_col))
    steps.append(OneHotEncoder(inputCol=mid_col, outputCol=out_col, dropLast=False))
    
pipeline = Pipeline(stages=steps)
df = pipeline.fit(df).transform(df)

# Target Transformation: Signed Log application before Scaling
df = df.withColumn("REALINCTOT", F.col("INCTOT") * F.col("CPI99"))
df = df.withColumn("REALINCTOT_LOG", F.signum(F.col("REALINCTOT")) * F.log1p(F.abs(F.col("REALINCTOT"))))

```

### Dimensionality Reduction via PCA
All processed numerical columns and high-dimensional one-hot encoded arrays were flattened into a single dense vector structure via a VectorAssembler. A Principal Component Analysis (PCA) estimator was fitted on the training split to identify the orthogonal axes capturing the highest variance.An initial evaluation up to $k=10$ components revealed that the first component explained 30.68% of the total variance, the second explained 14.00%, and the third explained 7.31%. Following the elbow method on the generated scree plot, the feature space was reduced to the top 3 principal components, capturing a cumulative variance of 51.99%.

```python


# Combine features into a single vector column
assembler = VectorAssembler(inputCols=["EDUC_MM", "AGE_Z", "STATE_OH", "SEX_OH", "RACE_OH", "EMPSTAT_MM", "CITIZEN_MM", "MARRINYR_MM", "WKSWORK1_MM", "HISPAN_OH"], outputCol="features")
ml_df = assembler.transform(ml_df)

# Perform train/validation/test split and fit PCA
train_df, val_df, test_df = ml_df.randomSplit([0.70, 0.15, 0.15], seed=42)
pca = PCA(k=10, inputCol="features", outputCol="pca_features")
model = pca.fit(train_df)

```

### Baseline Model Training (Random Forest)
Using the compressed feature representations obtained from the 3 principal components, a RandomForestRegressor was established as the baseline supervisor to predict the real income target. The model was configured as an ensemble of 30 independent decision trees (numTrees=30), allowing each tree to grow to a maximum depth of 12 (maxDepth=12) to map non-linear relationships within the low-dimensional PCA projections.

```python
# Isolate the top 3 principal components from the PCA vector output
train_final_df = train_final_df.withColumn("pca_features_3", array_to_vector(F.slice(vector_to_array("pca_features"), 1, 3)))

# Initialize and train the Random Forest Regressor
rf = RandomForestRegressor(labelCol="label", featuresCol="pca_features_3", predictionCol="prediction", numTrees=30, maxDepth=12, seed=42)
model_baseline = rf.fit(train_final_df)

```
### Performance Evaluation & Error Diagnosis
The model's generalizability was measured systematically across the train, validation, and test subsets using Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and the Coefficient of Determination ($R^2$).The baseline model delivered a highly stable $R^2$ score of approximately 0.235 across all splits. While the consistent performance indicates high generalizability without overfitting, the restricted accuracy metrics reflect the loss of high-frequency information resulting from the aggressive dimensional compression down to 3 components. To assist future optimization, an absolute error tracking column was added to isolate and diagnose extreme prediction outliers.

```python

# Set up standard regression evaluators
ev_rmse = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
ev_r2 = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="r2")

pred_test = model_baseline.transform(test_final_df)
print("Test Results -> RMSE:", ev_rmse.evaluate(pred_test), "| R2:", ev_r2.evaluate(pred_test))

# Calculate absolute residual error to isolate poor predictions
pred_test = pred_test.withColumn("error", F.abs(F.col("label") - F.col("prediction")))
worst_outliers = pred_test.orderBy(F.col("error").desc()).select(["label", "prediction", "error"]).show(1)

```

## Notebooks

Open the **Notebooks** section for the full pipeline in execution order.

| Step | Notebook |
|------|----------|
| Environment setup | `expanse-env.ipynb` |
| Data extraction | `data-extraction-all-col.ipynb` |
| Data exploration | `data-exploration.ipynb` |
| Figures / EDA plots | `data-plots.ipynb` |
| Preprocessing (Spark) | `data-preprocessing.ipynb` |
| Model 1: EDUC classifier | `data-modeling.ipynb` |
| Model 1: income regressor | `data-modeling-income.ipynb` |
| Speedup analysis | `speedup-analysis.ipynb` |
| Model 2: PCA / second model | `data-second-model.ipynb` |

---

# Results

> **[View the Results on GitHub Pages →](https://jedwin4321.github.io/dsc232r-group-project/results/)**

## Data Plots from phase Data Exploration

### Plot-1 Income vs Education


<img width="585" height="437" alt="Screenshot 2026-05-30 at 6 31 25 PM" src="https://github.com/user-attachments/assets/2ffe8a85-1ea9-4fb9-a84e-fb8362b9ae42" />




### Plot2  Income trend over Time

<img width="604" height="445" alt="Screenshot 2026-05-30 at 6 46 52 PM" src="https://github.com/user-attachments/assets/6742707c-3e2f-48e3-b310-8220c1c9e8a2" />



### Plot3 Income by state- Top 10 state with abg income

<img width="589" height="443" alt="Screenshot 2026-05-30 at 6 47 07 PM" src="https://github.com/user-attachments/assets/701a565e-e080-4d2c-a694-2279fe479d03" />


### Plot4 Education vs Income over Time

<img width="600" height="445" alt="Screenshot 2026-05-30 at 6 47 19 PM" src="https://github.com/user-attachments/assets/f4799bb7-5438-4062-8f67-5be76fd880e6" />


### Plot5 Income vs Race 

<img width="583" height="448" alt="Screenshot 2026-05-30 at 6 50 34 PM" src="https://github.com/user-attachments/assets/0f1cc0ce-1a48-4ed7-a85e-bde652a980b5" />



### Plot6 Education vs Income by Gender

<img width="602" height="446" alt="Screenshot 2026-05-30 at 4 58 01 PM" src="https://github.com/user-attachments/assets/e290d7c7-8c9f-46ce-9b4e-5517804c3886" />



### Plot7  US State Median Income Distribution


<img width="994" height="382" alt="Screenshot 2026-05-31 at 8 31 44 PM" src="https://github.com/user-attachments/assets/e4122c13-193c-4d6a-8fe9-80d8bd308bf0" />


> [!NOTE]
> State medians use raw personal income for all adult residents (including part-time workers, students, and retirees), so values run lower than headlines focused on full-time or household earnings.

### Relative Income by state


<img width="1000" height="364" alt="Screenshot 2026-05-31 at 8 43 28 PM" src="https://github.com/user-attachments/assets/cdff9e74-cfd9-4b22-84e8-c56738e3b504" />







## Model-1

> [!WARNING]
> Model metrics below describe predictive fit on census microdata. They are associations, not proof that changing education or location causes income to change.

### RandomForest Classfier



Performance Across Hyperparameter Settings and Data Splits

| Model | numTrees | maxDepth | Split      | Accuracy | F1 Score | Weighted Precision |
| ----- | -------: | -------: | ---------- | -------: | -------: | -----------------: |
| RF    |       20 |       10 | Train      | 0.446404 | 0.333050 |           0.414931 |
| RF    |       20 |       10 | Validation | 0.446472 | 0.333084 |           0.415042 |
| RF    |       20 |       10 | Test       | 0.446635 | 0.333245 |           0.414820 |
| RF    |       30 |       12 | Train      | 0.478052 | 0.389883 |           0.434884 |
| RF    |       30 |       12 | Validation | 0.478075 | 0.389845 |           0.434680 |
| RF    |       30 |       12 | Test       | 0.478180 | 0.389950 |           0.435532 |



### RandomForest Regressor

Random Forest Regression Performance Across Hyperparameter Settings and Dataset Splits

| Model | numTrees | maxDepth | Split      |     RMSE |      MAE |       R² |
| ----- | -------: | -------: | ---------- | -------: | -------: | -------: |
| RF    |       20 |       10 | Train      | 31627.08 | 15340.43 | 0.251201 |
| RF    |       20 |       10 | Validation | 31647.34 | 15340.85 | 0.251349 |
| RF    |       20 |       10 | Test       | 31620.07 | 15330.54 | 0.251243 |
| RF    |       30 |       12 | Train      | 31565.51 | 15258.63 | 0.254113 |
| RF    |       30 |       12 | Validation | 31587.00 | 15260.15 | 0.254201 |
| RF    |       30 |       12 | Test       | 31559.95 | 15249.53 | 0.254087 |




## Model-2

### PCA explained variance

**REALINCTOT model** (3 components selected, 51.99% cumulative variance):

| Component | Explained variance |
|---|---:|
| PC1 | 30.68% |
| PC2 | 14.00% |
| PC3 | 7.31% |

**EDUC model** (4 components selected, 64.57% cumulative variance):

| Component | Explained variance |
|---|---:|
| PC1 | 24.63% |
| PC2 | 23.44% |
| PC3 | 10.84% |
| PC4 | 5.66% |

### Random Forest Regressor (REALINCTOT, 3 PCA components)

Random Forest regression on PCA-reduced features (`numTrees=30`, `maxDepth=12`).

| Split | RMSE | MAE | R² |
|---|---:|---:|---:|
| Train | 31994.74 | 15028.18 | 0.2350 |
| Validation | 31954.07 | 15027.94 | 0.2347 |
| Test | 31868.15 | 14998.55 | 0.2355 |

### Random Forest Classifier (EDUC, 4 PCA components)

Random Forest classification on PCA-reduced features (`numTrees=30`, `maxDepth=12`).

| Split | Accuracy | F1 Score | Weighted Precision |
|---|---:|---:|---:|
| Train | 0.3704 | 0.3665 | 0.4329 |
| Validation | 0.3704 | 0.3666 | 0.4332 |
| Test | 0.3701 | 0.3663 | 0.4327 |

### Figure 1 – PCA Explained Variance – REALINCTOT Model

<img width="566" height="418" alt="Screenshot 2026-05-31 at 6 24 23 PM" src="https://github.com/user-attachments/assets/fab82169-9ae9-4e3c-abbe-03b76fdab771" />


### Figure 2 – Distribution of Absolute Errors in REALINCTOT Predictions

<img width="1226" height="453" alt="Screenshot 2026-05-31 at 6 24 52 PM" src="https://github.com/user-attachments/assets/1ffd34b2-5d5e-4ddb-b3fd-be4d02eb562c" />


### Figure 3 – Distribution of Absolute Errors in REALINCTOT Predictions (Log Scale)

<img width="637" height="443" alt="Screenshot 2026-05-31 at 6 25 07 PM" src="https://github.com/user-attachments/assets/aec71d44-2894-40e9-bc24-740f345743ef" />


### Figure 4-PCA Explained Variance – EDUC Model

<img width="565" height="413" alt="Screenshot 2026-05-31 at 6 25 22 PM" src="https://github.com/user-attachments/assets/b90d4f30-466e-4e49-a723-22a59a203b16" />


### Figure 5 – Confusion Matrix – EDUC Predictions (% of Total Data)

<img width="553" height="562" alt="Screenshot 2026-05-31 at 6 32 42 PM" src="https://github.com/user-attachments/assets/0fece201-d65b-4b7c-a6ba-1778f5f8200d" />


### Figure 6 – Confusion Matrix – EDUC Predictions (% per True Label)


<img width="550" height="549" alt="Screenshot 2026-05-31 at 6 33 08 PM" src="https://github.com/user-attachments/assets/bca2f9f9-f776-465a-a8f0-70590b22a12a" />


### Figure 7 – PCA Explained Variance – REALINCTOT vs. EDUC Models

<img width="401" height="293" alt="Screenshot 2026-05-31 at 6 33 31 PM" src="https://github.com/user-attachments/assets/98d72284-15d4-4de6-919c-95ce6a09d599" />

---

# Discussion

> **[View the Discussion on GitHub Pages →](https://jedwin4321.github.io/dsc232r-group-project/discussion/)**

## 1. Initial Data Exploration & Scale Interpretation
The exploration phase revealed a massive foundational dataset consisting of over 67 million rows and 238 variables. The initial thought process was strictly reductionist: while 238 attributes were present, a vast majority of them represented redundant demographic identifiers, spatial granularities, or high-dimensional socioeconomic codes. Isolating our variables of primary interest—YEAR, STATEFIP, SEX, AGE, RACE, EDUC, and INCTOT—was an intuitive starting step to establish a clean analytical baseline.

At this step, the raw metric counts are entirely believable as they perfectly mirror the expected scale of multi-decade IPUMS decennial census and American Community Survey (ACS) structural microdata extracts. However, a major critical omission during this initial stage was an underestimation of code scheme artifacts. Accepting 238 columns without a thorough programmatic null assessment masked the presence of data scheme missing value flags (such as 9999999.0 for income or 0 for missing indicators). Treating these placeholder values as literal numeric entries early on heavily skewed our initial statistical summaries, forcing an aggressive secondary cleaning cycle during the transformations phase.

## 2. Preprocessing and Transformations
The transformation pipeline represents the core statistical foundation of the project. The logic here required balancing distinct data structures: continuous economics (INCTOT), continuous demographics (AGE), unranked categoricals (SEX, RACE, STATEFIP), and inherently ordinal categoricals (EDUC). 

The thought process for filling missing income data was highly contextual. Rather than applying a global mean imputation, computing separate average personal income baselines grouped explicitly by YEAR was chosen. Because inflation distorts nominal purchasing power across decades, a global mean would have fundamentally corrupted the historical distribution. Multiplying nominal income by the CPI99 factor to create REALINCTOT successfully normalized the target space across time bounds.

### Shortcomings
* **The Log/Z-Score Conflict:** For numerical scaling, Z-score standardization was selected over min-max normalization because it is less susceptible to extreme outliers. However, while this successfully scaled AGE_Z, applying a standard Z-score directly to REALINCTOT proved problematic due to the severe, long-tailed rightward skew of wealth distributions. A signed logarithmic transformation should have been uniformly applied prior to calculating the Z-score to squeeze the variance and bring the distribution closer to normality.
* **One-Hot Sparsity Tax:** Using a StringIndexer and OneHotEncoder pipeline on STATENAME created a 51-dimensional sparse vector for every single record. When scaled across 67 million rows, this created an incredibly wide feature matrix. This high-dimensional encoding choice dramatically escalated cluster memory requirements during model training, a bottleneck that could have been avoided by using a target encoding scheme or geographic regional grouping instead.

## 3. Model 1: Distributed Multiclass Educational Classifier
Model 1 attempted to solve a highly complex, 12-class categorization problem using a distributed PySpark RandomForestClassifier to map an individual's highest educational attainment (EDUC) based on real income, age, state, sex, and race. Scaling from 20 trees (depth 10) to 30 trees (depth 12) was implemented to expand model capacity over the wide sparse arrays.

When we look at the results, even with hyperparameter tuning the best accuracy that we were able to achieve was 48%. At first glance, a test accuracy of ~47.8% seems low, meaning the model fails to predict the correct educational tier more than half the time. However, these results are incredibly honest and mathematically believable. 

The model’s low accuracy is a direct consequence of target variable construction. Differentiating between adjacent educational steps—such as distinguishing between "1 year of college" versus "2 years of college"—relying strictly on basic demographic proxies and income is a fundamentally noisy task. The model captures the macro socioeconomic trend perfectly, but it lacks the fine-grained signature required to isolate precise institutional transitions. 

While accuracy sits at ~47.8%, the underlying Macro-F1 score dropped significantly to 0.3899. This severe drop reveals that the model fell victim to extreme class imbalance. The dataset is heavily dominated by majority categories (e.g., High School Graduates and 4 Years of College). The Random Forest Classifier preserved global accuracy by prioritizing these majority patterns, effectively sacrificing minority classes (such as early vocational tracks or specialized nursery school brackets). To achieve true scientific merit, a class-weight balancing multiplier or down-sampling pipeline should have been integrated into the cluster training steps to force the estimator to treat minority classes with equal weight.

## 4. Model 1 (Income Regressor): Continuous Income Prediction
This reframed the problem as continuous regression to predict exactly how much money a person makes (their total real income, or REALINCTOT) based on facts about them, like their age, education level, gender, race, and the state they live in. The tuned architecture (30 trees, depth 12) achieved a test R² score of 0.254 and an RMSE of 31559.95.

An R² of 0.254 means our model accounts for only 25.4% of the variance in personal income. In social science and economic modeling, an R² between 0.20 and 0.30 is highly standard and believable; human income is dictated by thousands of unobserved variables (such as industry sector, individual talent, family wealth, and employment tenure) that are completely absent from our data.

However, the major shortcoming is highlighted by the massive RMSE of over $31,500. Because the model was trained on raw linear income targets rather than a log-scaled target space, the squared error penalty heavily over-indexed on extreme high-income outliers. The Random Forest leaves were pulled toward these multi-million dollar wealth anomalies, severely degrading the model’s predictive accuracy for the median working-class demographic.

## 5. Model 2: Fitting Analysis

### Where does your model fit in the fitting graph?
**Ans:** Our model is slightly in the underfitting zone.

* **Income Regressor (REALINCTOT):** The PCA reduced the feature space to just 3 components capturing only 51.99% of the variance. With a Random Forest trained on such information-sparse features, the model almost certainly achieves a training R² that is modest and a test R² that is only marginally lower — both values will be low in absolute terms. That flat gap between train and test performance (both mediocre) is a classic underfitting signature: the model isn't complex enough or informative enough to learn the true signal.
  
* **Education Classifier (EDUC):** The PCA retained 4 components explaining 64.57% of the variance. A Random Forest with numTrees=30, maxDepth=12 has significant capacity, but again it's working from compressed, lossy features. Expect moderate accuracy with a small train/val gap — the bottleneck is not model complexity but feature information loss, which again points toward underfitting.

In both cases, the dominant cause of poor performance is the PCA bottleneck, not overfitting. The models are not memorizing noise — they're failing to capture the true complexity of the target variables because too much information was discarded during dimensionality reduction.

---

### What are potential future improvements or next models?
**Ans:**

#### Feature Engineering
* Retain more PCA components. The elbow method selected 3–4, but given that cumulative explained variance is only ~52–65%, we could reasonably try 6–8 components and observe whether validation metrics improve meaningfully.
* Consider alternative dimensionality reduction techniques like truncated SVD or UMAP, which may capture non-linear structure that PCA misses.

#### Model Improvements
* Gradient Boosted Trees (GBT) in PySpark tend to outperform Random Forests on tabular data, especially for regression tasks like income prediction where outliers and skew are present.
* Hyperparameter tuning via CrossValidator or TrainValidationSplit on numTrees, maxDepth, and minInstancesPerNode — the current model uses fixed hyperparameters.
* For the classification task, experimenting with Gradient Boosted Classifier or a Multilayer Perceptron could improve F1 on minority education categories.

#### Data Improvements
* Re-introduce the OCC1990 occupation column with hierarchical grouping (e.g., collapsing ~400 occupations into ~15 broad sectors), which is likely one of the strongest predictors of income and education.
* Include interaction or polynomial features on AGE (age-squared is a classic predictor of income in economics/labor literature).
   
#### Target Variable
* The income regressor predicts raw REALINCTOT, which still has a heavy right skew even after log-transforming REALINCTOT_LOG for the features. Consider predicting REALINCTOT_LOG as the target (and inverting at evaluation time) to reduce the influence of extreme outliers on RMSE.

---

### How does dimensionality reduction affect your results compared to the full feature set?
**Ans:** The effects are clearly negative in terms of raw predictive power.

#### Information Loss is Significant
* **For Income:** 3 PCA components → 52% variance explained — nearly half the feature signal is discarded before the model even trains.
* **For Education:** 4 PCA components → 64.6% variance explained — better, but still a substantial loss.

#### Why PCA Underperforms Here
The feature matrix is a mix of sparse one-hot encodings and dense scaled scalars. PCA on this kind of mixed-type, high-cardinality sparse matrix tends to absorb most variance into the state/geographic dimensions rather than the more predictive demographic and economic variables. The principal components may not align well with income or education signal.


<img width="747" height="338" alt="Screenshot 2026-05-30 at 4 06 56 PM" src="https://github.com/user-attachments/assets/74166e5f-d553-4d04-bad2-56fd7953b454" />

Bottom line: Dimensionality reduction via PCA hurt predictive accuracy in exchange for a simpler, faster-to-train model. Given that the original dataset has many one-hot-encoded sparse features, PCA is not the ideal choice for this data structure.

---

# Conclusion

> **[View the Conclusion on GitHub Pages →](https://jedwin4321.github.io/dsc232r-group-project/conclusion/)**

## Conclusion

### What We Learned About Big Data Processing

Honestly, the infrastructure lessons ended up being just as 
valuable as the modeling ones. Managing memory across 7 executors, 
hunting down 9999999.0 missing value flags hidden across 238 
columns, and figuring out how to actually get jobs running on 
Expanse — that is what working with big data looks like in 
practice. Spark's lazy evaluation was a lifesaver here. Being 
able to iterate on 67 million rows without re-reading the file 
every single time made the whole project actually feasible.

One thing we genuinely underestimated early on was how badly 
the one-hot encoding of STATENAME would hurt us. Creating a 
51-dimensional sparse vector for every single record, then 
scaling that across 67 million rows, ate up way more memory 
than we expected during training. In hindsight, a target encoding 
or regional grouping would have been a much smarter choice.

### How Distributed Computing Changed Our Approach

Without distributed computing, this project basically would not 
have been possible in the timeframe we had. Running a Random 
Forest on 67 million rows on a single machine would take hours 
per iteration, which makes hyperparameter tuning pretty much 
off the table. With 7 executors on Expanse, we could actually 
try different configurations like 20 trees vs 30 trees, depth 
10 vs 12, and compare results without waiting forever. It 
genuinely changed how we thought about the problem. Instead 
of having to commit to one setup upfront, we had the freedom 
to experiment.

The Spark vs Ray comparison drove this home pretty clearly. 
Spark averaged 1.81s on the group-by aggregation after warmup 
while Ray took 86.82s, which is about 48x slower. For a 
pipeline that needs to run on 67 million rows repeatedly, 
that kind of gap is the difference between actually being 
able to iterate and just sitting there waiting.

### What We Would Explore With More Time and Resources

If we had more time and resources, the first thing we would 
do is bring back OCC1990 occupation data. We dropped it 
because grouping 400+ occupation codes into broad sectors 
takes a lot of careful manual work, but honestly occupation 
is probably the single strongest predictor of income that 
we left on the table entirely.

We would also switch to predicting REALINCTOT_LOG as the 
target instead of raw income. That one change alone would 
likely cut RMSE significantly just by reducing how much 
the extreme high-income outliers pull the error up. Our 
RMSE ended up at $31,560, which is largely a consequence 
of a handful of multi-million dollar cases skewing 
everything. And with a bigger compute budget, cross-validation 
instead of a fixed train/val/test split would give us much 
more reliable performance estimates across the full dataset.

## Second Model Conclusion

### Model 1

The Random Forest Classifier for education prediction hit 
~47.8% accuracy across 12 classes. That sounds bad at first, 
but honestly it makes sense when you think about it. Trying 
to distinguish between "1 year of college" and "2 years of 
college" using just age, income, race, sex, and state is 
genuinely a hard and noisy problem. The Macro-F1 dropped to 
0.39, which shows the model really struggled with minority 
education categories. The majority classes like High School 
and 4-year College dominated everything, and we never got 
around to adding class weighting to fix that.

The income regressor landed at R² = 0.254 and RMSE = $31,560. 
An R² around 0.25 is actually pretty standard in social 
science modeling since income depends on so many things we 
simply did not have access to: industry, job tenure, family 
wealth. The bigger issue was RMSE. Because we predicted raw 
income instead of log-income, a few million-dollar outliers 
dragged the error way up for everyone else.

### Model 2

PCA reduced the feature space to 3 components for income 
(52% variance kept) and 4 components for education (64.6% 
variance kept). Both models ended up underfitting. The gap 
between train and test was small, but both numbers were low. 
The bottleneck was not model complexity at all — it was that 
we threw away too much information before training even started.

The trade-off was real. Model 2 was faster and simpler to 
train, but predictive performance clearly dropped compared 
to Model 1. For a feature matrix that mixes 51 one-hot 
state columns with dense scaled scalars, PCA just is not 
the right tool. It absorbed most of the variance into the 
geographic dimensions instead of the more predictive 
economic and demographic signal.

To improve Model 2, the three most impactful changes would be:

- Keep more PCA components. The elbow method pointed to 3-4, 
  but with only 52-65% variance captured, trying 6-8 
  components would likely help without much extra compute cost.
- Switch to truncated SVD instead of PCA for the sparse 
  one-hot features, which is much better suited for this 
  kind of matrix.
- Try Gradient Boosted Trees instead of Random Forest, which 
  generally outperforms on tabular regression tasks like 
  income prediction.

### Final Thoughts

The models are imperfect, but they tell an honest story. 
Higher education correlates strongly with higher income, 
with EDUC 11 averaging around \$92k compared to just \$19k 
at EDUC 0. The gender income gap shows up clearly at every 
education level. Some race categories consistently earn 
significantly less than others. The data confirmed what we 
expected going in, and the models captured the broad trends 
even if they could not nail the fine-grained details.

---

# Statement of Collaboration

> **[View the Statement of Collaboration on GitHub Pages →](https://jedwin4321.github.io/dsc232r-group-project/collaboration/)**

## Edwin Vargas Navarro
**Team Coordinator, Data, & Modeling**

We didn't have a leader per se, but after each deadline I would copy and paste the milestone specs into our group chat, and depending on availability we would pick which part we can work on. It felt like we were a pretty solid team, meeting all the requirements in a timely manner. Then after we all did our parts, we left 1-2 days for revisions.

In our initial brainstorming of ideas, we opted in picking IPUMS / census data, where I was able to figure out on how to load the data into expanse - properly linking column names from `usa_00001.xml` and the original `dat` file. 

When it came time to train our first model, we ran into some out of memory issues - where I figured we can save compute by saving our data-preprocessed dataframe as a parquet file. Where, instead of computing the pre-processing steps again and again, we can load the new parquet file.

Then finally, I worked on the extra credit, learning how to do all the ssh setup and creating a shell script to run the commands. Since I also did the speedup analysis, this was intuitive - just needed to use ray. All in all, I did coding, wrote about the sections I worked on the README / jupyterbook, and offered feedback during our revision stages.

## Evan Lim
**Data Exploration, Preprocessing, & Modeling**

I think everyone contributed to the project in a meaningful way.

My primary responsibility was on programming. I'll break down my contributions by milestone.

Milestone 1: I helped look for various datasets on Kaggle, HuggingFace, and other dataset aggregation websites. I put forward some datasets that we might have found interesting/easy to work with.

Milestone 2: I completed the Data Exploration section, writing code to show the columns, rows, aggregations, categorical/continuous variables, checking for missing data, and checking for duplicate data. I also did most of the write up for this section.

Milestone 3: I completed the Data Preprocessing section, implementing the preprocessing plan in the previous milestone. I normalized numeric columns, applied one hot encoding to categorical columns, removed missing values, and neatly packaged the data for the next person (Edwin) to train the first model.

Milestone 4: I trained the second models with PCA with some help from Edwin. I did another round of preprocessing to add extra columns, applied PCA to these columns, and trained the new models with these principle components. I outputted graphs and metrics for PCA and the final models.

I checked and gave minor feedback on final READMEs and made small changes where necessary.

## Jiamin Wu
**Writer & Conclusions**

Everyone contributed consistently throughout the project 
and we made sure to leave time at the end for revisions 
as a team.

My primary role was as the team writer. In Milestone 2, 
I wrote explanations for the exploratory visualizations, 
helping connect the figures around income, education, 
gender, race, and state-level differences back to our 
core research question. In Milestone 3, I wrote the 
conclusion for Model 1, summarizing the Random Forest 
classifier and regressor results, walking through the 
fitting analysis, and laying out improvement suggestions 
such as reintroducing occupation data and switching to 
log-income as the regression target. For the final 
submission, I authored the Conclusion section, which 
required reading through and synthesizing content from 
every part of the project, the data exploration findings, 
preprocessing decisions, Model 1 classifier and regressor 
results, Model 2 PCA analysis, the Spark vs Ray comparison, 
and the Discussion section, and pulling it all together 
into a cohesive narrative that connected back to our 
original research question about how education and income 
vary across demographics, regions, and time in the US.

## Noopur Chowdary
**Exploration, Results, & Write-up**

Milestone 1: For Milestone one, I actively took part in discussions to decide which dataset to choose for the project. Each member proposed their choice of datasets. After considering the pros and cons of each dataset, we collectively decided to go with the IPUMS / Census dataset.

Milestone 2: Created data plots using Spark to explore and visualize the dataset.

Milestone 3: Performed fitting analysis for Model 1, evaluating its performance across training and validation data.

Milestone 4: Compiled all the results and completed the final write-up in collaboration with Carmen.

---

# Extra Credit: Spark vs Ray

> **[View the Extra Credit on GitHub Pages →](https://jedwin4321.github.io/dsc232r-group-project/extra-credit/)**

For the extra credit task we ran the same data task in Spark and Ray, timed both, and compared the results. Our project already runs on Spark end to end, so seeing the differences between these two frameworks will be compelling. We follow a similar structure as speedup-analysis.ipynb with the warmup convention (run 1 discarded, avg runs 2-3). The code can be found in [framework-comparison.ipynb](framework-comparison.ipynb).

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

> [!NOTE]
> Timing convention matches speedup-analysis.ipynb: run 1 is warmup (first load on the node) and is discarded; reported times are the average of runs 2 and 3.

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

> [!IMPORTANT]
> All runs used the same Expanse setup (8 CPUs, 128 GB, shared partition). Spark's faster repeat runs also reflect OS page cache after the first read; Ray stayed near ~88 s each run.

## Analysis

### 1. Which framework was faster? By how much?

Spark was faster. On avg runs 2-3, Spark was about 38x faster (2.33 s vs 87.98 s). After the first read, Spark dropped to about 2 seconds on runs 2 and 3 because the parquet was cached on the node. Ray stayed around 87 seconds each run.

### 2. Which was easier to implement? Why?

Spark was slightly easier (4/5 vs 3/5). The aggregation matches data-plots and the rest of our pipeline. Ray needed ray.init and ray.shutdown each timed run on top of the Ray Data API. Spark matched what we already had in the project.

### 3. For your specific use case, which would you choose?

Spark for the pipeline we built - extraction, preprocessing, modeling, and speedup analysis on 67M rows. This group-by also ran faster on Spark in our timed runs.

Ray could still make sense for modeling experiments like hyperparameter tuning or many parallel training trials. It's worth exploring a hybrid approach in future iterations of this project.
