# Dataset and preprocessing

At first, we decided that each team member has to find at least one dataset of
interest with sufficient data from which at least two perspectives can be
induced. During the first team call, every dataset was discussed along with
possible correlations. In the end, we chose the 2014-2022 datasets from the
[Stack Overflow Annual Developer Survey](https://insights.stackoverflow.com/survey),
as these datasets have correlations that could be of use for a potential topic.
After some brainstorming during team meetings, we decided to dive into the world
of gender pay gaps, as the dataset contains sufficient variables that can be
used for two perspectives.

## Cleaning

Each Stack Overflow dataset contains at least some changes compared to other
years, such as column renaming or structural changes. We had to go through two
phases in order to clean everything properly. The first phase is where columns
are renamed and restructured in order to merge them together. Columns have been
manually merged by inspecting them one by one and merging the ones containing
roughly the same name or content in terms of what they represent. Columns that
were not of use were immediately excluded during this process.

The second phase involves normalising the data. In general, this has been done
by thoroughly inspecting the unique values for each column and combine values
that represent similar meaning.

Finally, we have decided to use parquet `.pq` as the file type for our final
dataset. This allows us to specify the datatype for each column and decrease the
overall file size of the final dataset with additional gzip compression. This
resulted in a 7.2MB parquet file, rather than a 145MB CSV file.

After all, a total of 955 columns spanning 9 datasets have been reduced to a
single dataset containing 19 columns and 535,759 rows.

## Variable descriptions

In terms of variable type and measurement scale, the variables in the final
dataset can be classified under several combinations:

- Continuous / Ratio variables: `YearsCode`, `YearsCodePro`, `Salary`
- Discrete / Ordinal variables: `JobSat`
- Discrete / Nominal variables: `Education`, `OrgSize`, `LastNewJob`,
  `Employment`, `RespondentType`, `JobSeek`, `Gender`, `Student`, `Country`,
  `CodingActivities`, `DevType`, `LearnCodeFrom`, `LangPresent`
- Discrete / Interval variables: `Year`
- Discrete / Ratio variables: `Age`

Variables that are currently being used are: `Year`, `Salary`, `YearsCodePro`,
`Age`, `Education`, `RespondentType`, `Gender`, `Country` and `DevType`.

## Aggregations

In general, most aggregations happen for calculating the salary gap between men
and women relative to men. This is done by taking the mean salary for both men
and women, subtracting these means and finally divide the total by the mean
salary for men. In mathematical notation, this is defined as:

$$\textrm{SalaryGap} = \frac{S_{\textrm{man}} - S_{\textrm{woman}}}{S_{\textrm{man}}}$$

In most graphs a percentage is being used, which is the above salary gap formula
multiplied by 100.

**Example:** Let's say in the Netherlands the average annual salary for men is
&euro;80,000 and for women &euro;60,000. Then the salary gap will be 25% using
the aforementioned calculation. If women are the ones making &euro;80,000 per
year and men make &euro;60,000 per year, then the salary gap will be -33%. We
call the percentage outcome a *male-favoured gap* if the percentage is positive.
When the outcome is negative, it is considered a *female-favoured gap*.
