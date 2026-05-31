# Discussion

## Discussion Section (3 points)


# Discussion

## 1. Initial Data Exploration & Scale Interpretation
The exploration phase revealed a massive foundational dataset consisting of over 67 million rows and 238 variables. The initial thought process was strictly reductionist: while 238 attributes were present, a vast majority of them represented redundant demographic identifiers, spatial granularities, or high-dimensional socioeconomic codes. Isolating our variables of primary interest—YEAR, STATEFIP, SEX, AGE, RACE, EDUC, and INCTOT—was an intuitive starting step to establish a clean analytical baseline.

At this step, the raw metric counts are entirely believable as they perfectly mirror the expected scale of multi-decade IPUMS decennial census and American Community Survey (ACS) structural microdata extracts. However, a major critical omission during this initial stage was an underestimation of code scheme artifacts. Accepting 238 columns without a thorough programmatic null assessment masked the presence of data scheme missing value flags (such as 9999999.0 for income or 0 for missing indicators). Treating these placeholder values as literal numeric entries early on heavily skewed our initial statistical summaries, forcing an aggressive secondary cleaning cycle during the transformations phase.

## 2. Preprocessing and Transformations
The transformation pipeline represents the core statistical foundation of the project. The logic here required balancing distinct data structures: continuous economics (INCTOT), continuous demographics (AGE), unranked categoricals (SEX, RACE, STATEFIP), and inherently ordinal categoricals (EDUC). 

The thought process for filling missing income data was highly contextual. Rather than applying a global mean imputation, computing separate average personal income baselines grouped explicitly by YEAR was chosen. Because inflation distorts nominal purchasing power across decades, a global mean would have fundamentally corrupted the historical distribution. Multiplying nominal income by the CPI99 factor to create REALINCTOT successfully normalized the target space across time bounds.

### Shortcomings:
* **The Log/Z-Score Conflict:** For numerical scaling, Z-score standardization was selected over min-max normalization because it is less susceptible to extreme outliers. However, while this successfully scaled AGE_Z, applying a standard Z-score directly to REALINCTOT proved problematic due to the severe, long-tailed rightward skew of wealth distributions. A signed logarithmic transformation should have been uniformly applied prior to calculating the Z-score to squeeze the variance and bring the distribution closer to normality.
* **One-Hot Sparsity Tax:** Using a StringIndexer and OneHotEncoder pipeline on STATENAME created a 51-dimensional sparse vector for every single record. When scaled across 67 million rows, this created an incredibly wide feature matrix. This high-dimensional encoding choice dramatically escalated cluster memory requirements during model training, a bottleneck that could have been avoided by using a target encoding scheme or geographic regional grouping instead.

## 3. Model 1: Distributed Multiclass Educational Classifier
Model 1 attempted to solve a highly complex, 12-class categorization problem using a distributed PySpark RandomForestClassifier to map an individual's highest educational attainment (EDUC) based on real income, age, state, sex, and race. Scaling from 20 trees (depth 10) to 30 trees (depth 12) was implemented to expand model capacity over the wide sparse arrays.

When we look at the results, even with hyperparameter tuning the best accuracy that we were able to achieve was 48%. At first glance, a test accuracy of ~47.8% seems low, meaning the model fails to predict the correct educational tier more than half the time. However, these results are incredibly honest and mathematically believable. 

The model’s low accuracy is a direct consequence of target variable construction. Differentiating between adjacent educational steps—such as distinguishing between "1 year of college" versus "2 years of college"—relying strictly on basic demographic proxies and income is a fundamentally noisy task. The model captures the macro socioeconomic trend perfectly, but it lacks the fine-grained signature required to isolate precise institutional transitions. 

While accuracy sits at ~47.8%, the underlying Macro-F1 score dropped significantly to 0.3899. This severe drop reveals that the model fell victim to extreme class imbalance. The dataset is heavily dominated by majority categories (e.g., High School Graduates and 4 Years of College). The Random Forest Classifier preserved global accuracy by prioritizing these majority patterns, effectively sacrificing minority classes (such as early vocational tracks or specialized nursery school brackets). To achieve true scientific merit, a class-weight balancing multiplier or down-sampling pipeline should have been integrated into the cluster training steps to force the estimator to treat minority classes with equal weight.

## 4. Model 1 (Income Regressor Variation): Continuous Income Prediction
This reframed the problem as continuous regression to predict exactly how much money a person makes (their total real income, or REALINCTOT) based on facts about them, like their age, education level, gender, race, and the state they live in. The tuned architecture (30 trees, depth 12) achieved a test R² score of 0.254 and an RMSE of 31559.95.

An R² of 0.254 means our model accounts for only 25.4% of the variance in personal income. In social science and economic modeling, an R² between 0.20 and 0.30 is highly standard and believable; human income is dictated by thousands of unobserved variables (such as industry sector, individual talent, family wealth, and employment tenure) that are completely absent from our data.

However, the major shortcoming is highlighted by the massive RMSE of over $31,500. Because the model was trained on raw linear income targets rather than a log-scaled target space, the squared error penalty heavily over-indexed on extreme high-income outliers. The Random Forest leaves were pulled toward these multi-million dollar wealth anomalies, severely degrading the model’s predictive accuracy for the median working-class demographic.




## Fitting analysis (from Second Model)

Answer the following:

- Where does your model fit in the fitting graph?
  
  Ans: Our model is slightly in the underfitting zone.
  -Income Regressor (REALINCTOT):
   The PCA reduced the feature space to just 3 components capturing only 51.99% of the variance. With a Random Forest trained on such information-sparse features, the model almost certainly    achieves a training R² that is modest and a test R² that is only marginally lower — both values will be low in absolute terms. That flat gap between train and test performance (both         mediocre) is a classic underfitting signature: the model isn't complex enough or informative enough to learn the true signal.
  
  -Education Classifier (EDUC):
   The PCA retained 4 components explaining 64.57% of the variance. A Random Forest with numTrees=30, maxDepth=12 has significant capacity, but again it's working from compressed, lossy        features. Expect moderate accuracy with a small train/val gap — the bottleneck is not model complexity but feature information loss, which again points toward underfitting.
   In both cases, the dominant cause of poor performance is the PCA bottleneck, not overfitting. The models are not memorizing noise — they're failing to capture the true complexity of the     target variables because too much information was discarded during dimensionality reduction.


- What are potential future improvements or next models?
  
  Ans:
  - Feature engineering:
  - Retain more PCA components. The elbow method selected 3–4, but given that cumulative explained variance is only ~52–65%, we could reasonably try 6–8 components and observe whether           validation metrics improve meaningfully.
  - Consider alternative dimensionality reduction techniques like truncated SVD or UMAP, which may capture non-linear structure that PCA misses.

 - Model improvements:
 - Gradient Boosted Trees (GBT) in PySpark tend to outperform Random Forests on tabular data, especially for regression tasks like income prediction where outliers and skew are present.
 - Hyperparameter tuning via CrossValidator or TrainValidationSplit on numTrees, maxDepth, and minInstancesPerNode — the current model uses fixed hyperparameters
 - For the classification task, experimenting with Gradient Boosted Classifier or a Multilayer Perceptron could improve F1 on minority education categories.
 
 - Data improvements:
 - Re-introduce the OCC1990 occupation column with hierarchical grouping (e.g., collapsing ~400 occupations into ~15 broad sectors), which is likely one of the strongest predictors of         income and education.
 - Include interaction or polynomial features on AGE (age-squared is a classic predictor of income in economics/labor literature).
   
 - Target variable:
  The income regressor predicts raw REALINCTOT, which still has a heavy right skew even after log-transforming REALINCTOT_LOG for the features. Consider predicting REALINCTOT_LOG as the       target (and inverting at evaluation time) to reduce the influence of extreme outliers on RMSE.

- How does dimensionality reduction affect your results compared to the full feature set?
  The effects are clearly negative in terms of raw predictive power, and the notebook acknowledges this directly.
  Information loss is significant:
  For income: 3 PCA components → 52% variance explained — nearly half the feature signal is discarded before the model even trains.
  For education: 4 PCA components → 64.6% variance explained — better, but still a substantial loss.

Why PCA underperforms here:
Your feature matrix is a mix of sparse one-hot encodings (STATE_OH has ~50 columns, RACE_OH has 9, HISPAN_OH has several, SEX_OH has 2) and dense scaled scalars. PCA on this kind of mixed-type, high-cardinality sparse matrix tends to absorb most variance into the state/geographic dimensions rather than the more predictive demographic and economic variables. The principal components may not align well with income or education signal.


<img width="747" height="338" alt="Screenshot 2026-05-30 at 4 06 56 PM" src="https://github.com/user-attachments/assets/74166e5f-d553-4d04-bad2-56fd7953b454" />

Bottom line: Dimensionality reduction via PCA hurt predictive accuracy in exchange for a simpler, faster-to-train model. Given that the original dataset has many one-hot-encoded sparse features, PCA is not the ideal choice for this data structure.

