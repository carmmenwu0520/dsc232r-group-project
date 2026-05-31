# Conclusion

## Conclusion (3 points)

This is where you share your opinions and possible future directions. What would you have done differently? Close with final thoughts about:

## What We Learned About Big Data Processing

The infrastructure lessons were just as real as the modeling ones. 
Managing memory across 7 executors, dealing with 9999999.0 missing 
value flags hidden across 238 columns, and coordinating cluster 
jobs on Expanse taught us what working with big data actually 
looks like in practice. Spark's lazy evaluation meant we could 
iterate on 67 million rows without re-reading the file every time, 
which made the whole project possible.

One thing we underestimated early on was how much the one-hot 
encoding of STATENAME would hurt us. Creating a 51-dimensional 
sparse vector for every single record, then scaling that across 
67 million rows, dramatically increased memory requirements during 
training. A target encoding or regional grouping would have been 
smarter.

## How Distributed Computing Changed Our Approach

On a single machine, running a Random Forest on 67 million rows 
would take hours per iteration, making hyperparameter tuning 
basically impossible. With 7 executors on Expanse, we could try 
multiple configurations (20 trees vs 30 trees, depth 10 vs 12) 
and compare results in a reasonable amount of time. It changed 
how we thought about the problem. Instead of committing to one 
model setup upfront, we could actually experiment.

The Spark vs Ray comparison made this concrete. Spark averaged 
1.81s on the group-by aggregation after warmup. Ray took 86.82s, 
which is about 48x slower. For a pipeline that needs to run on 
67 million rows repeatedly, that gap is the difference between 
being able to iterate and being stuck waiting.

## What We Would Explore With More Time and Resources

With more executors and memory, we would bring back OCC1990 
occupation data. We dropped it because grouping 400+ occupation 
codes into broad sectors takes careful manual work, but occupation 
is probably the single strongest predictor of income that we left 
out entirely.

We would also predict REALINCTOT_LOG as the target instead of raw 
income. That one change would likely cut RMSE significantly by 
reducing the influence of the extreme high-income outliers that 
pulled our error to $31,560. And with a bigger compute budget, we 
would use cross-validation instead of a fixed train/val/test split 
to get more reliable performance estimates across the full dataset.

## Second model conclusion (from Second Model instructions)

## What is the conclusion of your 2nd model? What can be done to improve it?

## Model 1

The Random Forest Classifier for education prediction hit ~47.8% 
accuracy across 12 classes. That sounds bad, but it makes sense. 
Trying to tell apart "1 year of college" vs "2 years of college" 
using just age, income, race, sex, and state is genuinely noisy. 
The Macro-F1 dropped to 0.39, which shows the model struggled with 
minority education categories. The majority classes like High School 
and 4-year College dominated everything, and we never added class 
weighting to fix that.

The income regressor got R² = 0.254 and RMSE = $31,560. An R² 
around 0.25 is normal in social science since income depends on 
things we didn't have: industry, job tenure, family wealth. The 
bigger problem was RMSE. Because we predicted raw income instead of 
log-income, a few million-dollar outliers dragged the error way up 
for everyone else.

## Model 2: Second Model Conclusion

PCA reduced the feature space to 3 components for income (52% 
variance kept) and 4 components for education (64.6% variance 
kept). Both models ended up underfitting. The gap between train 
and test was small, but both were low. The bottleneck was not model 
complexity, it was throwing away half the information before 
training even started.

The trade-off was real. Model 2 was faster and simpler to train, 
but predictive performance dropped compared to Model 1. For a 
mixed sparse-dense feature matrix with 51 one-hot state columns, 
PCA is not the right tool. It absorbed most variance into the 
geographic dimensions instead of the more predictive economic 
signal.

To improve Model 2, the three most impactful changes would be:

- Keep more PCA components. The elbow method selected 3-4, but 
  with only 52-65% variance captured, trying 6-8 components would 
  likely help without much extra compute cost.
- Switch to truncated SVD instead of PCA for the sparse one-hot 
  features, which handles this kind of matrix better.
- Use Gradient Boosted Trees instead of Random Forest, which tends 
  to outperform on tabular regression tasks like income prediction.

## Final Thoughts

The models are imperfect, but they tell an honest story. Higher 
education correlates strongly with higher income, with EDUC 11 
averaging around $92k compared to $19k at EDUC 0. The gender 
income gap persists at every education level. Some race categories 
consistently earn significantly less than others. The data 
confirmed what we expected going in, and the models captured the 
broad trends even if they could not nail the fine-grained details.

*Note: The conclusion should be its own independent section. Methods will have models 1 and 2, Conclusion will have results and discussion for both.*
