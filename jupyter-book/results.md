# Results

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


```{note}
State medians use raw personal income for all adult residents (including part-time workers, students, and retirees), so values run lower than headlines focused on full-time or household earnings.
```

### Relative Income by state


<img width="1000" height="364" alt="Screenshot 2026-05-31 at 8 43 28 PM" src="https://github.com/user-attachments/assets/cdff9e74-cfd9-4b22-84e8-c56738e3b504" />







## Model-1

```{warning}
Model metrics below describe predictive fit on census microdata. They are associations, not proof that changing education or location causes income to change.
```

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






