# Results

## Results Section (5 points)

Present the results from your methods. Include figures about your results. No exploration or interpretation here—this is mainly a summary of your results. Sub-sections should mirror your Methods section.

Include: accuracy metrics, confusion matrices, explained variance plots, clustering visualizations, etc.

### Data Plots from phase Data Exploration

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





### Model-1

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





