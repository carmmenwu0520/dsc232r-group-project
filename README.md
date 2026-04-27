# dsc232r-group-project
Group project for DSC 232R: Big Data Analytics Using Spark

![GitHub last commit](https://img.shields.io/github/last-commit/jedwin4321/dsc232r-group-project)
![GitHub repo size](https://img.shields.io/github/repo-size/jedwin4321/dsc232r-group-project)

## Dataset Linkage

- Primary dataset: [IPUMS USA](https://usa.ipums.org/usa/)
- Data access portal: [IPUMS USA Extract System](https://usa.ipums.org/usa-action/variables/group)
- Citation: Steven Ruggles, Sarah Flood, Matthew Sobek, Daniel Backman, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, Renae Rodgers, Jonathan Schroeder, and Kari C.W. Williams. *IPUMS USA: Version 16.0* [dataset]. Minneapolis, MN: IPUMS, 2025. [https://doi.org/10.18128/D010.V16.0](https://doi.org/10.18128/D010.V16.0)

## Abstract

In this project, we will analyze data from the IPUMS USA dataset (https://usa.ipums.org/usa/), which provides harmonized U.S. census and survey data across multiple years. We will construct a dataset spanning 2001 to 2024 that includes variables such as total income, educational attainment, geographic region or state, survey year, age, sex, and employment status, with a total size exceeding 10 GB with millions of records. Our research investigates how the relationship between education and income varies across regions and time, and to what extent education predicts income across different geographic regions. Due to the large scale and complexity of the data, which includes millions of records across multiple years, this analysis cannot be efficiently performed on a standard laptop with limited memory and computational power. We will use distributed computing frameworks such as Spark to process and analyze the data at scale.

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

## Data Plots

Notebook: [`data-plots.ipynb`](./data-plots.ipynb)

## Preprocessing Plan 


## Team Contact

For project questions, reach out to:

- Edwin Vargas Navarro: [evargasnavarro@ucsd.edu](mailto:evargasnavarro@ucsd.edu)
- Evan Lim: [e2lim@ucsd.edu](mailto:e2lim@ucsd.edu)
- Jiamin Wu: [jiw294@ucsd.edu](mailto:jiw294@ucsd.edu)
- Noopur Chowdary: [nchowdary@ucsd.edu](mailto:nchowdary@ucsd.edu)