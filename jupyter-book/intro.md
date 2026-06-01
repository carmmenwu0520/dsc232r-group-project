# Introduction

In this project, we analyzed data from the [IPUMS USA dataset](https://usa.ipums.org/usa/), which provides harmonized U.S. census and survey data across multiple years. We then constructed a dataset spanning from 2001 to 2024. The data includes variables such as total income, educational attainment, geographic region or state, survey year, age, sex, and employment status, with a total size exceeding 65 GB with millions of records. **Our research investigates how the relationship between education and income varies across regions and time, and to what extent education predicts income across different geographic regions.**

One of the main reasons we were interested in this project stems from how researchers routinely work with census data to study how education, place, and earnings line up across the country. The models these researchers make are meant to inform people (i.e. lawmakers, school board officials, you, and many more) in making real decisions. A good predictive model could support people make decisions like whether additional education is right for them by comparing if there's an association with higher pay in a given state or year, and where workforce or training efforts should focus when local labor markets look out of step with national trends.

Due to the large scale and complexity of the data, which includes millions of records across multiple years, we relied on Apache Spark on SDSC Expanse (8 cores, 128 GB RAM per job). Even then, full-table preprocessing, feature encoding, and Random Forest training often ran for hours and sometimes failed when memory filled up. A laptop or single-node setup would have been far slower or effectively impossible for the same work at this scale.

```{important}
At this scale, distributed Spark on Expanse was required for full-table pipelines. Jobs could run for hours and still hit memory limits on 128 GB nodes.
```

## Dataset Linkage

- Primary dataset: [IPUMS USA](https://usa.ipums.org/usa/)
- Data access portal: [IPUMS USA Extract System](https://usa.ipums.org/usa-action/variables/group)
- Citation: Steven Ruggles, Sarah Flood, Matthew Sobek, Daniel Backman, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, Renae Rodgers, Jonathan Schroeder, and Kari C.W. Williams. *IPUMS USA: Version 16.0* [dataset]. Minneapolis, MN: IPUMS, 2025. [https://doi.org/10.18128/D010.V16.0](https://doi.org/10.18128/D010.V16.0)

## Team Contact

For project questions, reach out to:

- Edwin Vargas Navarro: [evargasnavarro@ucsd.edu](mailto:evargasnavarro@ucsd.edu)
- Evan Lim: [e2lim@ucsd.edu](mailto:e2lim@ucsd.edu)
- Jiamin Wu: [jiw294@ucsd.edu](mailto:jiw294@ucsd.edu)
- Noopur Chowdary: [nchowdary@ucsd.edu](mailto:nchowdary@ucsd.edu)

<!-- ## Introduction to Your Project (3 points)

Why was this project chosen? Why is it interesting? Discuss the general/broader impact of having a good predictive model. Why is this important?

For DSC 232R, also address: Why did this problem require big data and distributed computing? What would be impossible or impractical without Spark/Ray?

---

## Instructions for Final README

Your final README.md should be a **complete, professional document** that tells the story of your project:

1. A complete introduction explaining your project and its importance
2. All prior milestone submissions integrated into a cohesive narrative
3. All code uploaded as Jupyter notebooks that can be easily followed
4. A written report with all required sections
5. Your final model included in every section (Methods, Results, Discussion)
6. **Your GitHub repo must be made public** by the morning of the next day after the submission deadline -->