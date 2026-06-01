# US Census Income and Education Analysis

Group project for DSC 232R: Big Data Analytics Using Spark

![GitHub last commit](https://img.shields.io/github/last-commit/jedwin4321/dsc232r-group-project)
![GitHub repo size](https://img.shields.io/github/repo-size/jedwin4321/dsc232r-group-project)

> [!IMPORTANT]
> **[Read the full project report here](https://jedwin4321.github.io/dsc232r-group-project/)**  
> Navigable write-up with Methods, Results, Discussion, and notebooks. This README is the same content.

## Dataset Linkage

- Primary dataset: [IPUMS USA](https://usa.ipums.org/usa/)
- Data access portal: [IPUMS USA Extract System](https://usa.ipums.org/usa-action/variables/group)
- Citation: Steven Ruggles, Sarah Flood, Matthew Sobek, Daniel Backman, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, Renae Rodgers, Jonathan Schroeder, and Kari C.W. Williams. *IPUMS USA: Version 16.0* [dataset]. Minneapolis, MN: IPUMS, 2025. [https://doi.org/10.18128/D010.V16.0](https://doi.org/10.18128/D010.V16.0)

## Abstract

In this project, we will analyze data from the [IPUMS USA dataset](https://usa.ipums.org/usa/), which provides harmonized U.S. census and survey data across multiple years. We will construct a dataset spanning 2001 to 2024 that includes variables such as total income, educational attainment, geographic region or state, survey year, age, sex, and employment status, with a total size exceeding 65 GB with millions of records. Our research investigates how the relationship between education and income varies across regions and time, and to what extent education predicts income across different geographic regions. Due to the large scale and complexity of the data, which includes millions of records across multiple years, this analysis cannot be efficiently performed on a standard laptop with limited memory and computational power. We will use distributed computing frameworks such as Spark to process and analyze the data at scale.

---

## Milestone 2

## SDSC Expanse Environment Setup 

Notebook: [`expanse-env.ipynb`](./expanse-env.ipynb)

For our setup, we requested `8` cores and `128GB` total memory.

![jupyter-session](images/jupyter-session.png)

Allowing us to do:

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

## Data Exploration using Spark

Notebook: [`data-exploration.ipynb`](./data-exploration.ipynb)

All data exploration in this section was done using Spark DataFrames.

### Number of Columns and Rows

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

Due to the large size of the dataset, it's difficult to look for duplicate rows on all rows. Instead, we will rely on the PERNUM column which uniquely identifies a person. We will combine this with YEAR (since the same person can respond multiple times across years) to identify potential duplicates. Also, as advised by the IPUMS website: "When combined with SAMPLE and SERIAL, PERNUM uniquely identifies each person within the IPUMS." As a safety precaution, we will use all 4 columns to uniquely identify a person's survey response in order to identify duplicates.

| Metric | Value |
|---|---:|
| Unique (`YEAR`,`PERNUM`,`SAMPLE`,`SERIAL`) | 67,125,780 |
| Duplicates | 0 |

There are no duplicates.

### Counting Nulls

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
There are code scheme defined codes for missing data in the EDUC (code 99), SEX (code 9), and STATEFIP (code 99) columns. We checked if there are any instances of this form of missing data using `.groupBy()` and `.count()`, but the tables in [`data-exploration.ipynb`](./data-exploration.ipynb) reveal that these codes were not used. All data points of interest are present within these columns.

## Data Plots

Notebook: [`data-plots.ipynb`](./data-plots.ipynb)

Visualizations in this section are generated from Spark DataFrame aggregations and then plotted with `matplotlib`.

### Plot 1: Income vs Education

![Income vs Education](images/income-education-barchart.png)

The chart shows a strong positive relationship between education level and average income, where earnings generally increase as education rises. Lower education levels (around 0–5) are associated with relatively low incomes (under ~20k), but there is a noticeable jump starting around mid-level education, and incomes increase sharply at higher levels, reaching above 60k–90k for the highest categories. This suggests that higher education significantly boosts earning potential, with the largest gains occurring at advanced levels rather than early stages of education.

### Plot 2: Income Trend Over Time (2001-2024)

![Income Trend Over Time](images/income-year-lineplot.png)

The chart shows a clear long-term upward trend in average income from 2001 to 2024, rising from around 29k to nearly 55k, indicating steady economic growth over time. There is a noticeable dip around 2009–2011, likely reflecting an economic downturn, after which income resumes a consistent upward trajectory. Growth appears to accelerate after about 2015, with especially strong increases in the most recent years, suggesting improving economic conditions or rising wages, although the sharp rise toward the end could also reflect inflation or other external factors rather than purely real income growth.

### Plot 3: Top 10 States by Average Income

![Top 10 States by Average Income](images/top10-state-incomes.png)

The chart shows that among the top 10 states, average income is relatively high but not evenly distributed—one state clearly leads (around ~63k), while the rest cluster in a slightly lower band (~43k–52k). This suggests a small number of states have a stronger concentration of high-paying industries or economic opportunities, creating a noticeable gap even within the top tier. Overall, it highlights that high income in the U.S. is concentrated in a few leading states rather than being uniformly spread across all top performers.

### Plot 4: Income Trends by Education Level

![Income Trends by Education Level](images/income-years-education-multi-lineplot.png)

The chart shows that average income rises over time for all education levels, but the increase is much stronger at higher levels of education, leading to a widening gap between low- and high-educated groups. Lower education categories (EDUC 0–3) remain in the lower income range (roughly ~8k–17k) with only modest growth, while higher categories (like EDUC 7–10) show steady and much larger increases, reaching significantly higher income levels over time. This highlights that higher education not only leads to higher earnings but also benefits more from economic growth over time. In IPUMS, EDUC values represent attainment levels: for example, EDUC 0 = no schooling/N/A, 1 = elementary (up to ~4th grade), 2 = middle school (5th–8th), 3 = early high school (around 9th grade), meaning these lower codes correspond to relatively low levels of formal education.

### Plot 5: Income by Race

![Income by Race](images/income-race.png)

The chart shows noticeable differences in average income across race categories, with some groups earning significantly higher (around ~45k–50k) while others are clustered much lower (around ~24k–27k), indicating clear income disparities across racial groups. A few categories stand out as top earners, while others consistently lag behind, suggesting unequal economic outcomes that may reflect differences in access to education, occupations, or systemic factors. In the IPUMS dataset, race is coded numerically, where common categories include 1 = White, 2 = Black/African American, 3 = American Indian/Alaska Native, 4 = Chinese, 5 = Japanese, 6 = Other Asian or Pacific Islander, 7 = Other race, 8 = Two major races, 9 = Three or more races, meaning each bar represents one of these racial groups rather than a continuous scale.

### Plot 6: Education vs Income by Gender

![Education vs Income by Gender](images/education-income-gender-multi-lineplot.png)

The chart shows that income increases with education for both males and females, but males consistently earn more at every education level, and the gap widens as education increases.

## Preprocessing Plan 

For preprocessing, we will clean and prepare the dataset before using it for analysis or modeling. Since this dataset is very large (around 67 million rows and 238 columns), all steps will be performed using Spark rather than local tools.

### 1. Handling Missing Values

Some variables use special values to represent missing data. For example, INCTOT has values such as 9999999, which do not represent real income.

For numerical variables such as AGE and INCTOT, we will:

- Replace these special values with null
- Then fill missing values using mean or median if needed

For categorical variables such as SEX, RACE, and EDUC, we will:

- Treat invalid or unknown codes as null
- Either keep them as null or replace with the most common category depending on the use case

### 2. Handling Data Imbalance

We will check if certain categories are imbalanced, especially for variables like SEX, RACE, and EDUC.

If some categories are much more frequent than others, we may:

- Use sampling methods
- Or consider class weighting if we build models later

### 3. Transformations

For numerical features like AGE and INCTOT:

- We will apply scaling (normalization or standardization)

For categorical features like SEX, RACE, EDUC, and STATEFIP:

- We will encode categories into model-ready numeric representations (for example, index encoding and one-hot style vectors when appropriate)

For feature engineering:

- We will create cleaned income features (for example, excluding special-code values from numeric summaries)
- We will prepare derived grouping features for year and geography to support regional/time-based modeling
- We will map state codes (STATEFIP values such as 1-56, including 1-50 for U.S. states) to readable state names/labels for geographic visualization (e.g., choropleth maps)
- We will create an inflation-adjusted income feature (for example, `INCTOT_adjusted`) by joining annual inflation/CPI values by `YEAR` and scaling `INCTOT` into comparable dollars

### 4. Spark Operations Planned for Preprocessing

The preprocessing steps will be implemented with Spark DataFrame and Spark ML operations, including:

- `withColumn`, `when`, `otherwise` to replace special codes with null
- `filter`, `na.fill`, and summary statistics for null handling decisions
- `groupBy().count()` and ratio checks to measure category imbalance
- sampling operations to rebalance categories when needed
- Spark ML transformers for categorical encoding and numeric scaling
- join operations (`join` on `YEAR`) with external inflation/CPI reference data
- mapping/state-label transformations for `STATEFIP` before choropleth plotting

---

## Milestone 3 

## Complete Preprocessing using Spark 

Notebook: [`data-preprocessing.ipynb`](./data-preprocessing.ipynb)


### Models Used in This Study:


1)Random Forest Classifier (Multiclass Education Prediction)->We used a Random Forest Classifier to predict multiclass education levels (EDUC) using demographic and socioeconomic features such as income, age, sex, race, and state information

 2) Random Forest Regressor-->We used a Random Forest Regressor to predict continuous income values (REALINCTOT) using demographic and socioeconomic variables such as age, education, sex, race, and state information. Random Forest Regression is an ensemble learning method that builds multiple decision trees and averages their predictions




## `RandomForestClassifier` (multiclass `EDUC`)

Notebook: [`data-modeling.ipynb`](./data-modeling.ipynb)


| model | split | accuracy | f1 | weightedPrecision |
|:--|:--|--:|--:|--:|
| RF `numTrees=20` `maxDepth=10` | train | 0.446404 | 0.333050 | 0.414931 |
| RF `numTrees=20` `maxDepth=10` | val | 0.446472 | 0.333084 | 0.415042 |
| RF `numTrees=20` `maxDepth=10` | test | 0.446635 | 0.333245 | 0.414820 |
| RF `numTrees=30` `maxDepth=12` | train | 0.478052 | 0.389883 | 0.434884 |
| RF `numTrees=30` `maxDepth=12` | val | 0.478075 | 0.389845 | 0.434680 |
| RF `numTrees=30` `maxDepth=12` | test | 0.478180 | 0.389950 | 0.435532 |


### `RandomForestRegressor` (`REALINCTOT`)

Notebook: [`data-modeling-income.ipynb`](./data-modeling-income.ipynb)

| model | split | rmse | mae | r2 |
|:--|:--|--:|--:|--:|
| RF `numTrees=20` `maxDepth=10` | train | 31627.08 | 15340.43 | 0.251201 |
| RF `numTrees=20` `maxDepth=10` | val | 31647.34 | 15340.85 | 0.251349 |
| RF `numTrees=20` `maxDepth=10` | test | 31620.07 | 15330.54 | 0.251243 |
| RF `numTrees=30` `maxDepth=12` | train | 31565.51 | 15258.63 | 0.254113 |
| RF `numTrees=30` `maxDepth=12` | val | 31587.00 | 15260.15 | 0.254201 |
| RF `numTrees=30` `maxDepth=12` | test | 31559.95 | 15249.53 | 0.254087 |


## Fitting Analyis
### 1)Where does your model fit in the fitting graph (underfitting vs. overfitting)?
Ans: To see if our model is underfitting or overfitting , we need to compare the performance metrics of training set and validation set.

a) Random Forest Classifier(multiclass EDUC prediction)->The evaluation metrics included accuracy, F1-score, and weighted precision. For the baseline model, we selected the Random Forest configuration with numTrees=20 and maxDepth=10. From the table above, we can observe that the training, validation, and test metrics were nearly identical across accuracy, F1-score, and weighted precision. This indicates that the model generalizes well to unseen data and does not show significant signs of overfitting or underfitting. However, the overall metric values are still relatively modest, with accuracy and F1-scores remaining below 50%. This suggests that the model may not be capturing enough predictive signal from the selected features, or that additional feature engineering and more informative variables may be required to improve multiclass education classification performance.

b) RandomForestRegressor` (`REALINCTOT`)-->For this model, the performance metrics included RMSE, MAE and R2. For the baseline model e selected the RandomForestRegressor configuration with numTrees=20 and maxDepth=10. From the table above, the training, validation, and test results are nearly identical for both model configurations,indicating that the model generalizes consistently to unseen data and does not exhibit significant overfitting or underfitting. However, the relatively low R² values (approximately 0.25) suggest that the model explains only a limited portion of the variance in income. This indicates that the model may not be capturing enough predictive signal from the available features, or that the selected variables have limited explanatory power for income prediction.


### 2)Build at least one model with different hyperparameters and compare results
Ans:
a)Random Forest Classifier(multiclass EDUC prediction)-For the Random Forest Classifier, we created another model using different hyperparameters: numTrees=30 and maxDepth=12. When compared with the baseline model (numTrees=20, maxDepth=10), the new model showed improved performance across all evaluation metrics. The baseline model achieved an accuracy of 44.6%, while the updated model achieved an accuracy of 47.8%. Similar improvements were also observed in F1-score and weighted precision.

b) RandomForestRegressor`-For the Random Forest Regressor, we trained another model using different hyperparameters: numTrees=30 and maxDepth=12, and compared its performance with the baseline model (numTrees=20, maxDepth=10). The updated model showed slightly better performance across all regression metrics. The RMSE decreased from approximately 31,620 to 31,560, while the MAE decreased from about 15,330 to 15,249. Additionally, the R² score improved from 0.251 to 0.254. 

### 3)Which model performs best and why?
Ans- In both cases, the hyperparameter configuration with numTrees=30 and maxDepth=12 produced better results compared to the baseline model. This improvement can be attributed to the increased number of trees and greater tree depth, which allowed the Random Forest models to capture more complex patterns and relationships within the data. As a result, the models achieved improved performance in both income prediction and multiclass education classification tasks.


### 4)What are the next models you are thinking of for Milestone 4 and why?
Ans:As seen from the current results, although the models show stable generalization with no major signs of overfitting or underfitting, they still achieve relatively modest prediction and classification performance. For Milestone 4, we plan to explore more advanced models such as Gradient Boosted Trees (GBTClassifier and GBTRegressor) to better capture complex nonlinear relationships in the data. We also plan to improve feature engineering by adding more informative variables and interaction features, since the current results suggest that the existing features may not provide enough predictive signal for strong classification and income prediction performance.

## Conclusion

### 1)What is the conclusion of your 1st model?

We trained two types of Random Forest models on over 67 million records of U.S. census data spanning 2001 to 2024: a Random Forest Classifier to predict multiclass education levels (EDUC) using features such as inflation-adjusted income (REALINCTOT_Z), age (AGE_Z), state (STATE_OH), sex (SEX_OH), and race (RACE_OH), and a Random Forest Regressor to predict real income (REALINCTOT) using education (EDUC), age, state, sex, and race as inputs. Both models demonstrated stable generalization, with training, validation, and test metrics remaining nearly identical, for example, the classifier achieved 47.8% accuracy on train, 47.8% on val, and 47.8% on test, while the regressor showed an R² of 0.254 across all three splits — indicating that we are not overfitting. However, the relatively modest absolute performance (classifier F1 ~0.39, regressor R² ~0.25) suggests that we are underfitting, meaning the current feature set does not carry enough predictive signal to fully explain either education level or income on its own.

### 2)What can be done to possibly improve it?

We believe there are several directions we can explore to improve model performance. First, we plan to expand our feature set by incorporating additional variables from the IPUMS dataset such as occupation, hours worked per week, and marital status, which are likely to have stronger correlations with income than the demographic variables we currently use. Second, since REALINCTOT is heavily right-skewed, we plan to apply a log transformation to income before regression, which should allow the model to capture patterns across the full income range better. Third, we noticed that the EDUC label distribution is uneven across categories, so we plan to experiment with class weighting to give the model a more balanced view of minority education levels during training. Finally, rather than manually comparing two hyperparameter configurations as we did in this milestone ( numTrees=20/maxDepth=10 vs. numTrees=30/maxDepth=12), we plan to run a proper cross-validated grid search to more systematically identify the best model settings.

### 3)How did distributed computing help with this task?

Distributed computing was essential for this project given the scale of our dataset, which contains over 67 million records across 238 columns and exceeds 65 GB in size. During development, we found that attempting to run preprocessing and model training locally caused the server to crash repeatedly due to memory limitations, which is why we moved to saving the final preprocessed data as a Parquet file and loading it directly for modeling. By running on SDSC Expanse with 7 executor instances each allocated 18 GB of memory (totaling 126 GB across executors), we were able to hold the full dataset in distributed memory and train our Random Forest models, for example, fitting the Random Forest Regressor with numTrees=30 and maxDepth=12 across the full training split, in a reasonable amount of time that would not have been possible on a single machine.


## MileStone 4

## Speedup Analysis

Notebook: [`speedup-analysis.ipynb`](./speedup-analysis.ipynb)

Here, we run the RF classifier on the training data found in `data-modeling.ipynb` three times for each executor proccess. As mentioned in the Speedup Measurement Guide, we ignore the first time (t1) as it's treated as a JVM warmup for the configuration and average t2 and t3. 

We yield the following results on 1 exectutor (baseline) and 7 executors.

| Executors | Time (sec) | Speedup | Efficiency |
|---|---:|---:|---:|
| 1 | 7593.4 | 1.00x | 100% |
| 7 | 1025.7 | 7.40x | 105.8% |

**Metrics:** 

* T_1 = 7593.41s 
* T_7 = 1025.67s
* speedup = T_1/T_7 = **7.40×**
* efficiency = speedup/7 = **105.8%**

**Amdahl:** We get our estimated parallelizable fraction p = 7 × 6.40 / (7.40 x 6) = 44.8 / 44.4 ≈ **1** (from measured speedup). This leads to a theoretical speedup at n = 7 with this p is **≈ 7.40×** and we achieved esentially 100% of that limit. Training time dropped from ~2.1 hours (1 executor) to ~17 minutes (7 executors) which goes to show the tree building benefits from distributed Spark executors on this dataset.


## Model 2 (PCA)

We built two PCA-enhanced Random Forest models using U.S. Census microdata (IPUMS), predicting real income (**REALINCTOT**) and education level (**EDUC**). The core idea was to apply dimensionality reduction via PCA before training, and compare its performance against a non-PCA baseline model.

---

## Feature Expansion & Missing Data Imputation

Because Model 2 leverages dimensionality reduction (PCA), the feature space was expanded by extracting additional categorical columns from the original dataset, including **EMPSTAT, CITIZEN, WKSWORK1, MARRINYR, and HISPAN**. This enrichment was intended to provide PCA with a richer representation of underlying structure.

Before transformation, placeholder values representing missing flags (such as 0 for employment and marriage-related variables) were explicitly set to `None`. Missing entries in categorical attributes were imputed using their statistical mode (e.g., most frequent category such as 1 for employment status and 2 for citizenship status). Continuous variables (e.g., WKSWORK1) were imputed using their mean values.

---

## Categorical Encoding & Scaled Transformations

To prepare the dataset for PCA, numerical variables with different scales were normalized using **MinMaxScaler**. Ordinal variables such as education level (**EDUC**) were encoded directly, preserving their inherent ranking.

For nominal categorical variables (STATEFIP, SEX, RACE, and HISPAN), a preprocessing pipeline using **StringIndexer** and **OneHotEncoder** was applied to avoid introducing false ordinal relationships.

Additionally, because the target variable (**REALINCTOT**) was heavily right-skewed, a signed logarithmic transformation (**REALINCTOT_LOG**) was applied prior to Z-score normalization.

---

## Dimensionality Reduction via PCA

All processed numerical features and high-dimensional one-hot encoded vectors were combined into a single dense representation using a **VectorAssembler**. A PCA model was then fitted on the training data to identify orthogonal components capturing maximum variance.

An initial evaluation up to **k = 10 components** showed:

- PC1 explained **30.68%** of variance  
- PC2 explained **14.00%**  
- PC3 explained **7.31%**

Using the elbow method on the scree plot, the feature space was reduced to the top **3 principal components**, capturing a cumulative **51.99%** of total variance.

---

## Baseline Model Training (Random Forest)

Using the compressed PCA features, a **RandomForestRegressor** was trained to predict real income. The model consisted of **30 decision trees (numTrees = 30)** with a maximum depth of **12 (maxDepth = 12)**.

---

## Performance Evaluation & Error Diagnosis

Model performance was evaluated across training, validation, and test splits using:

- Root Mean Squared Error (RMSE)  
- Mean Absolute Error (MAE)  
- Coefficient of Determination (R²)

The model achieved a stable **R² ≈ 0.235** across all splits. While this consistency suggests strong generalization and minimal overfitting, the overall performance was limited due to information loss from aggressive dimensionality reduction.

To further analyze errors, an absolute error tracking column was introduced to identify extreme prediction outliers.

---

## Results

For the income (**REALINCTOT**) model, PCA was initially evaluated with 10 components. The elbow method selected **3 components**, which explained only **51.99%** of total variance:

- PC1: 30.68%  
- PC2: 14.00%  
- PC3: 7.31%

For the education (**EDUC**) model, **4 components** were selected, explaining **64.57%** of variance:

- PC1: 24.63%  
- PC2: 23.44%  
- PC3: 10.84%  
- PC4: 5.66%

In both cases, the explained variance was relatively low, indicating that PCA was not highly effective for capturing predictive structure.

---

## Fitting Analysis & Conclusion

Both models fall into an **underfitting regime**, not due to insufficient model complexity, but because PCA removed too much predictive information.

With only 3 components (~52% variance) for income and 4 components (~64.6% variance) for education, the Random Forest models were trained on overly compressed feature representations. This resulted in low training and test performance with minimal gap between them — a classic sign of underfitting.

### Future Improvements

- Retain more PCA components (e.g., 6–8)  
- Use Gradient Boosted Trees for stronger tabular performance  
- Reintroduce structured features such as OCC1990 (grouped into occupation sectors)  
- Predict log-transformed income directly to reduce skew effects  

In summary, dimensionality reduction was the primary bottleneck. PCA on mixed sparse and dense features concentrated variance into a small number of components that did not align well with the most predictive demographic and economic signals.



  
  

## Team Contact

For project questions, reach out to:

- Edwin Vargas Navarro: [evargasnavarro@ucsd.edu](mailto:evargasnavarro@ucsd.edu)
- Evan Lim: [e2lim@ucsd.edu](mailto:e2lim@ucsd.edu)
- Jiamin Wu: [jiw294@ucsd.edu](mailto:jiw294@ucsd.edu)
- Noopur Chowdary: [nchowdary@ucsd.edu](mailto:nchowdary@ucsd.edu)
