# Results

## Results Section (5 points)

Present the results from your methods. Include figures about your results. No exploration or interpretation here—this is mainly a summary of your results. Sub-sections should mirror your Methods section.

Include: accuracy metrics, confusion matrices, explained variance plots, clustering visualizations, etc.

### Data Plots from phase Data Exploration

### Plot-1 Income vs Education

<img width="597" height="459" alt="Screenshot 2026-05-30 at 4 22 12 PM" src="https://github.com/user-attachments/assets/a65312ed-97d5-4dba-9f98-0c9b0b007439" />

### Plot2  Income trend over Time

<img width="616" height="452" alt="Screenshot 2026-05-30 at 4 26 19 PM" src="https://github.com/user-attachments/assets/63dc4a48-280d-4f81-bb92-5bcb3dacd600" />


### Plot3 Income by state- Top 10 state with abg income

<img width="599" height="457" alt="Screenshot 2026-05-30 at 4 27 43 PM" src="https://github.com/user-attachments/assets/fe39cd5b-59a7-4e82-bfd3-aa2ee36eb20a" />

### Plot4 Education vs Income over Time

<img width="616" height="464" alt="Screenshot 2026-05-30 at 4 34 30 PM" src="https://github.com/user-attachments/assets/5e02394b-908c-4365-9aad-e7ab07461c76" />

### Plot5 Income vs Race 

<img width="585" height="453" alt="Screenshot 2026-05-30 at 4 42 03 PM" src="https://github.com/user-attachments/assets/585c3b0a-83de-4a39-b4ee-f4f8390b59e0" />











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

