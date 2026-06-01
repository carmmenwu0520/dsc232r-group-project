# Statement of Collaboration

<!-- ## Statement of Collaboration (3 points)

This is a statement of contribution by each member. This will be taken into consideration when making the final grade for each member in the group.

Did you work as a team? Was there a team leader? Project manager? Coder? Writer? Please be truthful as this will determine individual grades in participation.

There is no job that is better than the other:

- If you did no code but did the entire write-up and gave feedback during the steps and collaborated—full credit.
- If you only coded but gave feedback on the write-up—full credit.
- If you managed everyone, deadlines, meetings, and communicated with teaching staff—full credit.

**Every role is important as long as you collaborated and were integral to the completion of the project. If a person did nothing, they risk getting a zero.** Just like in any job, if you did nothing, you risk getting fired. Teamwork is one of the most important qualities in industry and academia!

**Format:** Start with `Name: Title: Contribution`. If someone contributed nothing, write: "Did not participate in the project." -->

## Edwin Vargas Navarro
**Team Coordinator, Data, & Modeling**

We didn't have a leader per se, but after each deadline I would copy and paste the milestone specs into our group chat, and depending on availability we would pick which part we can work on. It felt like we were a pretty solid team, meeting all the requirements in a timely manner. Then after we all did our parts, we left 1-2 days for revisions.

In our initial brainstorming of ideas, we opted in picking IPUMS / census data, where I was able to figure out on how to load the data into expanse - properly linking column names from `usa_00001.xml` and the original `dat` file. 

When it came time to train our first model, we ran into some out of memory issues - where I figured we can save compute by saving our data-preprocessed dataframe as a parquet file. Where, instead of computing the pre-processing steps again and again, we can load the new parquet file.

Then finally, I worked on the extra credit, learning how to do all the ssh setup and creating a shell script to run the commands. Since I also did the speedup analysis, this was intuitive - just needed to use ray. All in all, I did coding, wrote about the sections I worked on the README / jupyterbook, and offered feedback during our revision stages.

## Evan Lim
**Data Exploration, Preprocessing, & Modeling**
I think everyone contributed to the project in a meaningful way.

My primary responsibility was on programming. I'll break down my contributions by milestone.

Milestone 1: I helped look for various datasets on Kaggle, HuggingFace, and other dataset aggregation websites. I put forward some datasets that we might have found interesting/easy to work with.

Milestone 2: I completed the Data Exploration section, writing code to show the columns, rows, aggregations, categorical/continuous variables, checking for missing data, and checking for duplicate data. I also did most of the write up for this section.

Milestone 3: I completed the Data Preprocessing section, implementing the preprocessing plan in the previous milestone. I normalized numeric columns, applied one hot encoding to categorical columns, removed missing values, and neatly packaged the data for the next person (Edwin) to train the first model.

Milestone 4: I trained the second models with PCA with some help from Edwin. I did another round of preprocessing to add extra columns, applied PCA to these columns, and trained the new models with these principle components. I outputted graphs and metrics for PCA and the final models.

I checked and gave minor feedback on final READMEs and made small changes where necessary.

## Jiamin Wu
**Writer & Conclusions**

Everyone contributed consistently throughout the project 
and we made sure to leave time at the end for revisions 
as a team.

My primary role was as the team writer. In Milestone 2, 
I wrote explanations for the exploratory visualizations, 
helping connect the figures around income, education, 
gender, race, and state-level differences back to our 
core research question. In Milestone 3, I wrote the 
conclusion for Model 1, summarizing the Random Forest 
classifier and regressor results, walking through the 
fitting analysis, and laying out improvement suggestions 
such as reintroducing occupation data and switching to 
log-income as the regression target. For the final 
submission, I authored the Conclusion section, which 
required reading through and synthesizing content from 
every part of the project, the data exploration findings, 
preprocessing decisions, Model 1 classifier and regressor 
results, Model 2 PCA analysis, the Spark vs Ray comparison, 
and the Discussion section, and pulling it all together 
into a cohesive narrative that connected back to our 
original research question about how education and income 
vary across demographics, regions, and time in the US.

## Noopur Chowdary
**Exploration, Results, & Write-up**

Milestone 1: For Milestone one, I actively took part in discussions to decide which dataset to choose for the project. Each member proposed their choice of datasets. After considering the pros and cons of each dataset, we collectively decided to go with the IPUMS / Census dataset.

Milestone 2: Created data plots using Spark to explore and visualize the dataset.

Milestone 3: Performed fitting analysis for Model 1, evaluating its performance across training and validation data.

Milestone 4: Compiled all the results and completed the final write-up in collaboration with Carmen.
