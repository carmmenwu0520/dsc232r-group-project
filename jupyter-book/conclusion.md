# Conclusion

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
with EDUC 11 averaging around $92k compared to just $19k 
at EDUC 0. The gender income gap shows up clearly at every 
education level. Some race categories consistently earn 
significantly less than others. The data confirmed what we 
expected going in, and the models captured the broad trends 
even if they could not nail the fine-grained details.
