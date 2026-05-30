# Results

## Results Section (5 points)

Present the results from your methods. Include figures about your results. No exploration or interpretation here—this is mainly a summary of your results. Sub-sections should mirror your Methods section.

Include: accuracy metrics, confusion matrices, explained variance plots, clustering visualizations, etc.

 Classification Results


 | model | split                        | accuracy | f1 | weightedPrecision |
|:--|:--|--:|--:|--:|
| RF `numTrees=20` `maxDepth=10` | train | 0.446404 | 0.333050 | 0.414931 |
| RF `numTrees=20` `maxDepth=10` | val | 0.446472 | 0.333084 | 0.415042 |
| RF `numTrees=20` `maxDepth=10` | test | 0.446635 | 0.333245 | 0.414820 |
| RF `numTrees=30` `maxDepth=12` | train | 0.478052 | 0.389883 | 0.434884 |
| RF `numTrees=30` `maxDepth=12` | val | 0.478075 | 0.389845 | 0.434680 |
| RF `numTrees=30` `maxDepth=12` | test | 0.478180 | 0.389950 | 0.435532 |


Regression Results

| model | split                          | rmse    | mae |     | r2 |
|:--|:--|--:|--:|--:|
| RF `numTrees=20` `maxDepth=10` | train | 31627.08 | 15340.43 | 0.251201 |
| RF `numTrees=20` `maxDepth=10` | val | 31647.34 | 15340.85 | 0.251349 |
| RF `numTrees=20` `maxDepth=10` | test | 31620.07 | 15330.54 | 0.251243 |
| RF `numTrees=30` `maxDepth=12` | train | 31565.51 | 15258.63 | 0.254113 |
| RF `numTrees=30` `maxDepth=12` | val | 31587.00 | 15260.15 | 0.254201 |
| RF `numTrees=30` `maxDepth=12` | test | 31559.95 | 15249.53 | 0.254087 |

