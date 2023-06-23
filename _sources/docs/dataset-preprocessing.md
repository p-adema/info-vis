# Dataset and preprocessing

This project uses the 2014-2022 datasets listed at
[Stack Overflow Annual Developer Survey](https://insights.stackoverflow.com/survey).

The dataset cleaning task has been divided between Peter and Kim. At first, we
weren't sure which years to include yet. Therefore, Kim did the 2011-2016
datasets and Peter did the 2017-2022 datasets. After we decided that our topic
is related to gender, the datasets from 2011, 2012 and 2013 became useless as
they do not contain the gender of each participant.

Each Stack Overflow dataset contained at least some changes, such as column
renaming or structural changes. Peter and Kim both have manually merged columns
by inspecting them one by one and merge the ones that overlap in the datasets
they were responsible for. Columns that were not of use were immediately
excluded during this process.

After individually merging all columns, data had to be normalised for all years.
This has been done by simply checking the unique values for each column and
combine values with the same meaning.

After both Peter and Kim had successfully cleaned and normalised their datasets,
both datasets from 2014-2016 and 2017-2022 have been merged together into a
single 2014-2022 dataset.

We have decided to use parquet `.pq` as the file type. This allows us to specify
the datatype for each column and decrease the overall file size of the final
dataset with additional gzip compression. This resulted in a 7.2MB parquet file,
rather than a 145MB CSV file.

After all, Peter and Kim together have manually inspected a total of 955 columns
spanning 9 datasets and have reduced this to a total of 19 columns. The final
dataset contains 535,759 rows.
