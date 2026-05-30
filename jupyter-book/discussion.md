# Discussion

## Discussion Section (3 points)

This is where you discuss the "why" and your interpretation—your thought process from beginning to end. Discuss how believable your results are at each step. Discuss any shortcomings.

It's okay to criticize your own work—this shows intellectual merit and scientific thinking. In science we rarely find perfect solutions. If your results seem too good, scrutinize them carefully!

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
  
 Ans:-Feature engineering:
 1) Retain more PCA components. The elbow method selected 3–4, but given that cumulative explained variance is only ~52–65%, we could reasonably try 6–8 components and observe whether          validation metrics improve meaningfully.
 2)Consider alternative dimensionality reduction techniques like truncated SVD or UMAP, which may capture non-linear structure that PCA misses.

 -Model improvements:
 1)Gradient Boosted Trees (GBT) in PySpark tend to outperform Random Forests on tabular data, especially for regression tasks like income prediction where outliers and skew are present.
 2)Hyperparameter tuning via CrossValidator or TrainValidationSplit on numTrees, maxDepth, and minInstancesPerNode — the current model uses fixed hyperparameters.
 3)For the classification task, experimenting with Gradient Boosted Classifier or a Multilayer Perceptron could improve F1 on minority education categories.
 
 -Data improvements:
 1) Re-introduce the OCC1990 occupation column with hierarchical grouping (e.g., collapsing ~400 occupations into ~15 broad sectors), which is likely one of the strongest predictors of         income and education.
 2) Include interaction or polynomial features on AGE (age-squared is a classic predictor of income in economics/labor literature).

-Target variable:
The income regressor predicts raw REALINCTOT, which still has a heavy right skew even after log-transforming REALINCTOT_LOG for the features. Consider predicting REALINCTOT_LOG as the target (and inverting at evaluation time) to reduce the influence of extreme outliers on RMSE.

- How does dimensionality reduction affect your results compared to the full feature set?
  The effects are clearly negative in terms of raw predictive power, and the notebook acknowledges this directly.
  Information loss is significant:
  For income: 3 PCA components → 52% variance explained — nearly half the feature signal is discarded before the model even trains.
  For education: 4 PCA components → 64.6% variance explained — better, but still a substantial loss.

Why PCA underperforms here:
Your feature matrix is a mix of sparse one-hot encodings (STATE_OH has ~50 columns, RACE_OH has 9, HISPAN_OH has several, SEX_OH has 2) and dense scaled scalars. PCA on this kind of mixed-type, high-cardinality sparse matrix tends to absorb most variance into the state/geographic dimensions rather than the more predictive demographic and economic variables. The principal components may not align well with income or education signal.


<img width="747" height="338" alt="Screenshot 2026-05-30 at 4 06 56 PM" src="https://github.com/user-attachments/assets/74166e5f-d553-4d04-bad2-56fd7953b454" />

Bottom line: Dimensionality reduction via PCA hurt predictive accuracy in exchange for a simpler, faster-to-train model. Given that the original dataset has many one-hot-encoded sparse features (especially STATE_OH), PCA is not the ideal choice for this data structure.

