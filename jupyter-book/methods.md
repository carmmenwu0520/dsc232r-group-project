# Methods

# Data Exploration

  *Number of Columns and Rows*

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
The full dataset contains 238 columns, and complete descriptors for all variables are available in both [`usa_00001.xml`](./usa_00001.xml) and the [IPUMS variable documentation website](https://usa.ipums.org/usa-action/variables/group).

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



There are code scheme defined codes for missing data in the EDUC (code 99), SEX (code 9), and STATEFIP (code 99) columns. We checked if there are any instances of this form of missing data using `.groupBy()` and `.count()`, but the tables in [`data-exploration.ipynb`](./data-exploration.ipynb) reveal that these codes were not used. All data points of interest are present within these columns.



# Preprocessing Plan

Before analysis and modeling, the dataset was cleaned and transformed to improve data quality and prepare the data for machine learning and visualization tasks. Because the dataset contained approximately 67 million records and 238 variables, all preprocessing operations were performed using Spark.

### 1. Handling Missing Values

### For numerical variables such as AGE and INCTOT:

Special missing-value codes were identified and replaced with null values.
The proportion of missing values was examined for each variable.
Missing values were imputed using appropriate summary statistics when necessary.
Variables with excessive missingness were evaluated before further analysis.

### For categorical variables such as SEX, RACE, EDUC, and MARST:

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


# Model-1( first distributed model)

As an initial modeling approach, Random Forest algorithms were applied to both classification and regression tasks to establish strong baseline models and evaluate the predictive power of the demographic and socioeconomic features available in the dataset. Random Forest was selected because it is a robust ensemble learning technique that can capture complex, non-linear relationships while remaining relatively resistant to overfitting.

To investigate the impact of model complexity, two versions of Random Forest were trained for each task. The first model used numTrees=20 and maxDepth=10, while a second model with tuned hyperparameters used numTrees=30 and maxDepth=12. Performance was evaluated on training, validation, and test datasets.

## Random Forest Classifier (Multiclass Education Prediction)-
We used a Random Forest Classifier to predict multiclass education levels (EDUC) using demographic and socioeconomic features such as income, age, sex, race, and state information
 Classification performance was evaluated using:
 1-Accuracy: The proportion of correctly classified observations.
 2-F1 Score: The harmonic mean of precision and recall, providing a balanced measure of classification performance.
 3- Weighted Precision: Precision averaged across all classes while accounting for class frequencies.

 Classification Results


 | model | split                        | accuracy | f1 | weightedPrecision |
|:--|:--|--:|--:|--:|
| RF `numTrees=20` `maxDepth=10` | train | 0.446404 | 0.333050 | 0.414931 |
| RF `numTrees=20` `maxDepth=10` | val | 0.446472 | 0.333084 | 0.415042 |
| RF `numTrees=20` `maxDepth=10` | test | 0.446635 | 0.333245 | 0.414820 |
| RF `numTrees=30` `maxDepth=12` | train | 0.478052 | 0.389883 | 0.434884 |
| RF `numTrees=30` `maxDepth=12` | val | 0.478075 | 0.389845 | 0.434680 |
| RF `numTrees=30` `maxDepth=12` | test | 0.478180 | 0.389950 | 0.435532 |

 ## Random Forest Regressor-->We used a Random Forest Regressor to predict continuous income values (REALINCTOT) using demographic and socioeconomic variables such as age, education, sex, race, and state information. Random Forest Regression is an ensemble learning method that builds multiple decision trees and averages their predictions

 Regression performance was evaluated using:

  1-Root Mean Squared Error (RMSE): Measures the average prediction error while giving greater weight to larger errors.
  2-Mean Absolute Error (MAE): Measures the average absolute difference between predicted and actual income values.
  3-R² (Coefficient of Determination): Represents the proportion of variance in income explained by the model.

Regression Results

| model | split                          | rmse    | mae |     | r2 |
|:--|:--|--:|--:|--:|
| RF `numTrees=20` `maxDepth=10` | train | 31627.08 | 15340.43 | 0.251201 |
| RF `numTrees=20` `maxDepth=10` | val | 31647.34 | 15340.85 | 0.251349 |
| RF `numTrees=20` `maxDepth=10` | test | 31620.07 | 15330.54 | 0.251243 |
| RF `numTrees=30` `maxDepth=12` | train | 31565.51 | 15258.63 | 0.254113 |
| RF `numTrees=30` `maxDepth=12` | val | 31587.00 | 15260.15 | 0.254201 |
| RF `numTrees=30` `maxDepth=12` | test | 31559.95 | 15249.53 | 0.254087 |


## Step1-Supervised Feature Assembly & Dataset Splitting

For Model 1, the target parameter was defined by mapping the educational column (EDUC) to a double precision label layout. Key independent features capturing scaled financial metrics, z-score scaled demographics, and one-hot encoded vector spaces (REALINCTOT_Z, AGE_Z, STATE_OH, SEX_OH, and RACE_OH) were isolated and combined into a singular unified sparse matrix via PySpark's VectorAssembler.Once assembled, the rows were distributed randomly into distinct processing subsets for training (70%), validation (15%), and testing (15%) splits leveraging a constant evaluation seed.

```python


# Format target label structure and select independent components
ml_df = df.select(F.col("EDUC").cast("double").alias("label"), "REALINCTOT_Z", "AGE_Z", "STATE_OH", "SEX_OH", "RACE_OH", "EDUCNAME")

# Structural consolidation of dimensions into a unified dense features column
assembler = VectorAssembler(inputCols=["REALINCTOT_Z", "AGE_Z", "STATE_OH", "SEX_OH", "RACE_OH"], outputCol="features")
ml_df = assembler.transform(ml_df)

# Perform distributed random splits across fixed random boundaries
train_df, val_df, test_df = ml_df.randomSplit([0.70, 0.15, 0.15], seed=SEED)

```
## Step2 Baseline Random Forest Classifier Training
A distributed RandomForestClassifier was initialized to serve as the initial pipeline baseline model. The model configuration constructed 20 distinct decision trees (numTrees=20) allowed to branch out to a localized vertical deep bound limit of 10 (maxDepth=10). This configuration provides a stable baseline for evaluating multiclass prediction capability across the transformed feature matrices.

```python
# Initialize and train the baseline Random Forest Classifier
rf = RandomForestClassifier(labelCol="label", featuresCol="features", predictionCol="prediction", numTrees=20, maxDepth=10, seed=SEED)
model_baseline = rf.fit(train_df)
```
## Step3 Hyperparameter Optimization
To optimize classification accuracy and control tree variance, a second, deeper model variant was initialized. The random forest configuration was manually optimized by scaling the ensemble size up to 30 decision trees (numTrees=30) and adjusting the information threshold boundaries down to an expanded structural maximum depth of 12 (maxDepth=12). This structural expansion allows individual nodes to form more precise non-linear decision splits.

```python
# Scale model hyperparameters to improve multi-class boundary limits
rf2 = RandomForestClassifier(labelCol="label", featuresCol="features", predictionCol="prediction", numTrees=30, maxDepth=12, seed=SEED)
model_rf_hp = rf2.fit(train_df)
```

## Step4 Distributed Multiclass Evaluation Matrix
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

 ### Random Forest Regressor-->
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



    
- **Model 2** (PCA/SVD + clustering or supervised)


## Feature Expansion & Missing Data Imputation
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

## Categorical Encoding & Scaled Transformations
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

## Dimensionality Reduction via PCA
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

## Baseline Model Training (Random Forest)
Using the compressed feature representations obtained from the 3 principal components, a RandomForestRegressor was established as the baseline supervisor to predict the real income target. The model was configured as an ensemble of 30 independent decision trees (numTrees=30), allowing each tree to grow to a maximum depth of 12 (maxDepth=12) to map non-linear relationships within the low-dimensional PCA projections.

```python
# Isolate the top 3 principal components from the PCA vector output
train_final_df = train_final_df.withColumn("pca_features_3", array_to_vector(F.slice(vector_to_array("pca_features"), 1, 3)))

# Initialize and train the Random Forest Regressor
rf = RandomForestRegressor(labelCol="label", featuresCol="pca_features_3", predictionCol="prediction", numTrees=30, maxDepth=12, seed=42)
model_baseline = rf.fit(train_final_df)

```
## Performance Evaluation & Error Diagnosis
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
