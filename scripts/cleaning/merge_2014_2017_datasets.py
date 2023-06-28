#!/usr/bin/env python3

"""
Merge the 2014-2016 and 2017-2022 datasets together, assuming that the column
names of the 2017-2022 dataset is leading, meaning that this the 2014-2016 dataset
columns will be renamed to those of 2017-2022.

Usage: ./merge_datasets.py

NOTE: This file assumes in the same directory two dataset files:
(1) 2014_2016.csv: pre-cleaned and normalised dataset from 2014-2016.
(2) SO_2_0.pq.gz: pre-cleaned and normalised dataset from 2017-2022.

The output file will be both CSV (SO_2014_2022.csv) and parquet (SO_2014_2022.pq).
The CSV is mainly used for debugging, because it is easy to open in third-pary software.
In practise, the parquet file will be used.
"""

import pandas as pd
import numpy as np
import re

def normalise_coding_activities(value):
    if value is np.nan:
        return value

    return 'hobby' if 'per week' in value else np.nan

def normalise_salary(value):
    if value is np.nan or value in ['Other (please specify)', 'Student / Unemployed', 'Rather not say', 'Unemployed']:
        return np.nan

    # Since we mainly have ranges of 10.000, we take the middle.
    # Example: $100,000 - $110,000 becomes 105.000

    if value == 'Less than $10,000':
        return 5000

    if value in ['Less than $20,000', '<$20,000']:
        return 15000

    if value == '>$140,000':
        return 145000

    if value == 'More than $160,000':
        return 165000

    if value == 'More than $200,000':
        return 205000

    value_reformatted = re.sub(r'\$([0-9]+),([0-9]+) - \$([0-9]+),([0-9]+)', '\\1\\2;\\3\\4', value)
    [range_low, range_high]= map(int, value_reformatted.split(';'))
    diff = range_high - range_low
    new_value = range_low + diff / 2
    return new_value

def normalise_education(row: pd.Series) -> pd.Series:
    edu = row['Education']

    if edu is np.nan or edu is pd.NA:
        return row

    new_row = row.copy()

    if 'PhD' in edu:
        # 'PhD in Computer Science (or related field)',
        new_row['Education'] = 'doctor'
    elif 'Masters Degree' in edu:
        # 'Masters Degree in Computer Science (or related field)',
        new_row['Education'] = 'master'
    elif any([value in edu for value in ['B.A', 'B.S.', 'Bachelor']]):
        # 'B.A. in Computer Science (or related field)',
        # 'B.S. in Computer Science (or related field)',
        # 'Bachelor of Science in Computer Science (or related field)',
        new_row['Education'] = 'bachelor'
    elif 'Some college coursework' in edu:
        # 'Some college coursework in Computer Science (or related field) but no degree',
        # 'Some college coursework in Computer Science (or related field)',
        new_row['Education'] = 'tertiary'
    elif any([value in edu for value in ['program', 'online class', 'training']]):
        # - Full-time, intensive program (e.g. "boot-camp")
        # - Industry certification program
        # - Part-time program (e.g. night school)
        # - Online class (e.g. Coursera, Codecademy, Khan Academy, etc.)
        # - On-the-job training

        if edu == 'On-the-job training':
            new_row['LearnCodeFrom'] = 'On the job training'
        elif 'online class' in edu:
            new_row['LearnCodeFrom'] = 'Other online resources (e.g., videos, blogs, forum)'
        elif 'program' in edu:
            new_row['LearnCodeFrom'] = 'Coding Bootcamp'

        new_row['Education'] = 'secondary'
    else:
        new_row['Education'] = np.nan

    return new_row

def normalise_df2017_lang_present(value):
    if value is np.nan or value is pd.NA:
        return value

    replacements = {
        'Bash/Shell': 'Bash/Shell/PowerShell',
        'PowerShell': 'Bash/Shell/PowerShell',
        'Cobol': 'COBOL',
        'Common Lisp': 'LISP',
        'CSS': 'HTML/CSS',
        'Ocaml': 'OCaml',
        'VB.NET': 'Visual Basic',
        'VBA': 'Visual Basic',
        'Visual Basic 6': 'Visual Basic',
    }

    new_vals = []
    for val in value.split(';'):
        val = val.strip()
        if val in replacements:
            new_vals.append(replacements[val])
        else:
            new_vals.append(val)

    return ';'.join(new_vals)

POPULAR_LANGS = ['ABAP', 'APL', 'Ada', 'Apex', 'Assembly', 'AutoHotkey', 'Awk',
                 'Batch', 'C#', 'C', 'C++', 'COBOL', 'CSS', 'Clojure',
                 'CoffeeScript', 'Common Lisp', 'Crystal', 'D', 'Dart',
                 'Delphi', 'Elixir', 'Erlang', 'F#', 'Forth', 'Fortran', 'Go',
                 'Groovy', 'HTML',  'Haskell', 'Java', 'JavaScript',
                 'Julia', 'Kotlin', 'LISP', 'Logo', 'Lua', 'MATLAB',
                 'Node.js', 'NodeJS', 'OCaml', 'Objective-C', 'PHP', 'SQL',
                 'Perl', 'PowerShell', 'Prolog', 'Python', 'R', 'Racket',
                 'Ruby', 'Rust', 'SAS', 'SQL', 'Scala', 'Scheme', 'Scratch',
                 'Shell', 'Smalltalk', 'Solidity', 'Swift', 'Tcl', 'TypeScript',
                 'VB.NET', 'VBScript', 'Visual Basic', 'WebAssembly', 'Bash']

def normalise_df2014_lang_present(value):
    if value is np.nan or value is pd.NA:
        return value

    replacements = {
        'HTML': 'HTML/CSS',
        'CSS': 'HTML/CSS',
        'NodeJS': 'Node.js',
        'PowerShell': 'Bash/Shell/PowerShell',
        'Bash': 'Bash/Shell/PowerShell',
        'Shell': 'Bash/Shell/PowerShell',
        'VB.NET': 'Visual Basic',
        'VBScript': 'Visual Basic',
    }

    new_vals = []
    for val in value.split(';'):
        val = val.strip()
        for lang in POPULAR_LANGS:
            if lang.lower() in val.lower():
                if lang in replacements:
                    new_vals.append(replacements[lang])
                else:
                    new_vals.append(lang)

    new_vals = list(set(new_vals))

    if len(new_vals) > 0:
        return ';'.join(new_vals)

    return np.nan

def add_student_col(row: pd.Series) -> pd.Series:
    new_row = row.copy()
    new_row['Student'] = 'no'

    if not row['DevType'] is np.nan:
        if not 'developer' in row['DevType'].lower():
            new_row['RespondentType'] = 'non-dev'
        else:
            new_row['RespondentType'] = 'dev'

        if 'student' in row['DevType'].lower():
            new_row['Student'] = 'yes'
            new_row['RespondentType'] = 'stu'

    return new_row

def main():
    df2014 = pd.read_csv('2014_2016.csv')
    df2017 = pd.read_parquet('./SO_2_0.pq.gz')

    # Remove underage people
    df2017 = df2017[df2017['Age'] != '-17']

    df2014_renamed = df2014.rename(columns={
        'survey_year': 'Year',
        'Including bonus, what is your annual compensation in USD?': 'Salary',
        'What best describes your career / job satisfaction?': 'JobSat',
        # '': 'YearsCode',
        'How many years of IT/Programming experience do you have?': 'YearsCodePro',
        'How old are you?': 'Age',
        'Training & Education': 'Education',
        'Which best describes the size of your company?': 'OrgSize',
        'Have you changed jobs in the last 12 months?': 'LastNewJob',
        'Employment Status': 'Employment',
        # '': 'RespondentType',
        'Are you currently looking for a job or open to new opportunities?': 'JobSeek',
        'What is your gender?': 'Gender',
        # '': 'Student',
        'What Country or Region do you live in?': 'Country',
        'How many hours programming as hobby per week?': 'CodingActivities',
        'Which of the following best describes your occupation?': 'DevType',
        # '': 'LearnCodeFrom',
        'Which languages are you proficient in?': 'LangPresent',
        # '': 'LangFuture'
    })[['Year', 'Salary', 'JobSat', 'YearsCodePro', 'Age', 'Education',
        'OrgSize', 'LastNewJob', 'Employment', 'JobSeek', 'Gender', 'Country',
        'CodingActivities', 'DevType', 'LangPresent']]

    df2014_renamed = df2014_renamed.apply(add_student_col, axis=1)

    df2014_renamed = df2014_renamed.apply(normalise_education, axis=1)

    df2014_renamed['Salary'] = df2014_renamed['Salary'].apply(normalise_salary)

    df2014_renamed['JobSat'] = df2014_renamed['JobSat'].replace({
        'I love my job': 5,
        "I'm somewhat satisfied with my job": 4,
        "I'm neither satisfied nor dissatisfied with my job": 3,
        "I'm somewhat dissatisfied with my job": 2,
        'I hate my job': 1,
        'Other (please specify)': np.nan,
    })

    df2014_renamed['YearsCodePro'] = df2014_renamed['YearsCodePro'].replace({
        '6/10/2014': np.nan,
        '2/5/2014': np.nan,
        '11+ years': 12,
        '11': 11,
        '6 - 10 years': 8,
        '2 - 5 years': 4,
        '1 - 2 years': 2,
        '<2': 2,
        'Less than 1 year': 1,
    })

    df2014_renamed['Age'] = df2014_renamed['Age'].replace({
        '< 20': '18-24',
        '20-24': '18-24',
        '25-29': '25-34',
        '30-34': '25-34',
        '35-39': '35-44',
        '40-50': '35-44',
        '40-49': '35-44',
        # '50-59': '45-54',
        # '51-60': '45-54',
        '>60': '65+',
        '> 60': '65+',
    })
    df2017['Age'] = df2017['Age'].replace('65-', '65+')

    for year in sorted(df2014_renamed['Year'].unique()):
        # 40% of 51-60 goes to 45-54 and 60% goes to 55-64
        age_51_60_df = df2014_renamed.query('Age == "51-60"').query(f'Year == {year}')
        upper_part_n_rows = int(len(age_51_60_df) * 0.4)
        bottom_part_n_rows = len(age_51_60_df) - upper_part_n_rows
        age_51_60_first_part = age_51_60_df.head(upper_part_n_rows).replace({'51-60': '45-54'})
        age_51_60_second_part = age_51_60_df.tail(bottom_part_n_rows).replace({'51-60': '55-64'})
        df2014_renamed.update(age_51_60_first_part)
        df2014_renamed.update(age_51_60_second_part)

        # 50% of 50-59 goes to 45-54 and 50% goes to 55-64
        age_50_59_df = df2014_renamed.query('Age == "50-59"').query(f'Year == {year}')
        upper_part_n_rows = int(len(age_50_59_df) * 0.5)
        bottom_part_n_rows = len(age_50_59_df) - upper_part_n_rows
        age_50_59_first_part = age_50_59_df.head(upper_part_n_rows).replace({'50-59': '45-54'})
        age_50_59_second_part = age_50_59_df.tail(bottom_part_n_rows).replace({'50-59': '55-64'})
        df2014_renamed.update(age_50_59_first_part)
        df2014_renamed.update(age_50_59_second_part)

    df2014_renamed['OrgSize'] = df2014_renamed['OrgSize'].replace({
        '1-4 employees': '2 to 9 employees',
        '5-9 employees': '2 to 9 employees',
        '10-19 employees': '10 to 19 employees',
        '20-99 employees': '20 to 99 employees',
        '100-499 employees': '100 to 499 employees',
        '500-999 employees': '500 to 999 employees',
        '1,000-4,999 employees': '1,000 to 4,999 employees',
        '5,000-9,999 employees': '5,000 to 9,999 employees',
        '10,000+ employees': '10,000 or more employees',
        'I am not part of a company': np.nan,
        'I am not sure': np.nan,
        'Other (please specify)': np.nan,
    })

    # Have you changed jobs in the last 12 months? -> Less than a year ago -> LastNewJob
    df2014_renamed['LastNewJob'] = df2014_renamed['LastNewJob'].replace({
        'No': np.nan,
        'Yes': 'Less than a year ago'
    })

    df2014_renamed['Employment'] = df2014_renamed['Employment'].replace({
        "I'm a student": 'notwork',
        'Employed full-time': 'fuilltime',
        'Employed part-time': 'parttime',
        'Freelance / Contractor': 'independent',
        'Other (please specify)': np.nan,
        'Other': np.nan,
        'Prefer not to disclose': np.nan,
        'Retired': 'retired',
        'Self-employed': 'independent',
        'Unemployed': 'searching',
    })

    df2014_renamed['JobSeek'] = df2014_renamed['JobSeek'].replace({
        'No': 'no',
        'Yes': 'yes',
        'I am actively looking for a new job': 'yes',
        'I am open to new job opportunities': 'yes',
        'I am not interested in other job opportunities': 'no',
        'I am not interested in new job opportunities': 'no',
        "I'm not actively looking, but I am open to new opportunities": 'maybe'
    })

    df2014_renamed['Gender'] = df2014_renamed['Gender'].replace({
        'Female': 'female',
        'Male': 'male',
        'Prefer not to disclose': np.nan,
        'Other': np.nan,
    })
    df2017['Gender'] = df2017['Gender'].replace({
        'Man': 'male',
        'Woman': 'female'
    })

    df2014_renamed['Country'] = df2014_renamed['Country'].replace({
        'Antigua & Deps': 'Antigua and Barbuda',
        'Bosnia Herzegovina': 'Bosnia and Herzegovina',
        'Burkina': 'Burkina Faso',
        'Central African Rep': 'Central African Republic',
        'Congo {Democratic Rep}': 'Democratic Republic of the Congo',
        'Ireland {Republic}': 'Ireland',
        'Korea North': 'North Korea',
        'Korea South': 'South Korea',
        'Macedonia [FYROM]': 'Macedonia',
        'Myanmar [Burma]': 'Myanmar',
        'Myanmar, {Burma}': 'Myanmar',
        'Other': np.nan,
        'Other (please specify)': np.nan,
        'Russian Federation': 'Russia',
        'Sao Tome & Principe': 'Sao Tome and Principe',
        'St Kitts & Nevis': 'Saint Kitts and Nevis',
        'Trinidad & Tobago': 'Trinidad and Tobago',
        'Vatican City': 'Vatican',
    })

    df2017['Country'] = df2017['Country'].replace({
        'Russian Federation': 'Russia',
        'Moldavia': 'Moldova',
        'Republic of Moldova': 'Moldova',
        'Korea': 'North Korea',
        'Virgin Islands': 'U.S. Virgin Islands',
        'S. Georgia & S. Sandwich Isls.': 'South Georgia and the South Sandwich Islands',
        'Virgin Islands (British)': 'British Virgin Islands',
        'Reunion (French)': 'Reunion',
        'Vatican City State': 'Vatican',
        'Tadjikistan': 'Tajikistan',
        'Brunei Darussalam': 'Brunei',
        'Zaire': 'Democratic Republic of the Congo',
        'U.S. Minor Outlying Islands': 'United States Minor Outlying Islands',
        'Polynesia (French)': 'French Polynesia',
        'French Guyana': 'Guyana',
        'Pitcairn Island': 'Pitcairn',
        'Macau': 'Macao',
        'Heard and McDonald Islands': 'Heard Island and McDonald Islands',
        'Micronesia, Federated States of...': 'Minor',
        'Congo': 'Democratic Republic of the Congo',
        'Timor-Leste': 'East Timor',
    })

    df2014_renamed['CodingActivities'].apply(normalise_coding_activities)

    df2014_renamed['DevType'] = df2014_renamed['DevType'].replace({
        "I don't work in tech": np.nan,
        'Analyst': 'Data or business analyst',
        'Back-End Web Developer': 'Developer, back-end',
        'Back-end web developer': 'Developer, back-end',
        'Business intelligence or data warehousing expert': 'Data scientist or machine learning specialist',
        'Data scientist': 'Data scientist or machine learning specialist',
        'Database Administrator': 'Database administrator',
        'Desktop Software Developer': 'Developer, desktop or enterprise applications',
        'Desktop developer': 'Developer, desktop or enterprise applications',
        'DevOps': 'DevOps specialist',
        'Developer with a statistics or mathematics background': 'Data or business analyst',
        'Embedded Application Developer': 'Developer, embedded applications or devices',
        'Embedded application developer': 'Developer, embedded applications or devices',
        'Enterprise Level Services': 'Developer, desktop or enterprise applications',
        'Enterprise level services developer': 'Developer, desktop or enterprise applications',
        'Executive (VP of Eng, CTO, CIO, etc.)': 'Senior Executive (C-Suite, VP, etc.)',
        'Executive (VP of Eng., CTO, CIO, etc.)': 'Senior Executive (C-Suite, VP, etc.)',
        'Front-End Web Developer': 'Developer, front-end',
        'Front-end web developer': 'Developer, front-end',
        'Full-Stack Web Developer': 'Developer, full-stack',
        'Full-stack web developer': 'Developer, full-stack',
        'Graphics programmer': 'Developer, game or graphics',
        'Growth hacker': 'Marketing or sales professional',
        'IT Staff / System Administrator': 'System administrator',
        'Machine learning developer': 'Data scientist or machine learning specialist',
        'Manager of Developers or Team Leader': 'Project manager',
        'Mobile Application Developer': 'Developer, mobile',
        'Mobile developer - Android': 'Developer, mobile',
        'Mobile developer - Windows Phone': 'Developer, mobile',
        'Mobile developer - iOS': 'Developer, mobile',
        'Mobile developer': 'Developer, mobile',
        'Other': np.nan,
        'Quality Assurance': 'Developer, QA or test',
        'other': np.nan,
    })

    df2017['LangPresent'] = df2017['LangPresent'].apply(normalise_df2017_lang_present)

    df2014_renamed['LangPresent'] = df2014_renamed['LangPresent'].apply(normalise_df2014_lang_present)

    combined_df = pd.concat([df2017, df2014_renamed]).drop(['LangFuture'], axis=1).sort_values(['Year'], ascending=False).reset_index(drop=True)

    for col in ['Salary']:
        combined_df[col] = combined_df[col].astype(pd.Float64Dtype())

    for col in ['Year', 'YearsCode', 'YearsCodePro']:
        combined_df[col] = combined_df[col].astype(pd.Int32Dtype())

    for col in ['JobSat']:
        combined_df[col] = combined_df[col].astype(pd.Int8Dtype())

    string_dtype_cols = ['Age', 'Education', 'OrgSize', 'LastNewJob',
                         'Employment', 'RespondentType', 'JobSeek', 'Gender',
                         'Student', 'Country', 'CodingActivities', 'DevType',
                         'LearnCodeFrom', 'LangPresent']
    for col in string_dtype_cols:
        combined_df[col] = combined_df[col].astype(pd.StringDtype())

    combined_df['Year'] = pd.Categorical(combined_df['Year'], ordered=True)

    combined_df['Age'] = pd.Categorical(combined_df['Age'],
                                        ordered=True,
                                        categories=['18-24', '25-34', '35-44', '45-54', '55-64', '65+'])

    combined_df['Education'] = pd.Categorical(combined_df['Education'],
                                              ordered=True,
                                              categories=['none',
                                                          'primary',
                                                          'secondary',
                                                          'tertiary',
                                                          'assoc',
                                                          'bachelor',
                                                          'master',
                                                          'professional',
                                                          'doctor'])

    combined_df['OrgSize'] = pd.Categorical(combined_df['OrgSize'],
                                            ordered=True,
                                            categories=['Just me - I am a freelancer, sole proprietor,...',
                                                        '2 to 9 employees',
                                                        '10 to 19 employees',
                                                        '20 to 99 employees',
                                                        '100 to 499 employees',
                                                        '500 to 999 employees',
                                                        '1,000 to 4,999 employees',
                                                        '5,000 to 9,999 employees',
                                                        '10,000 or more employees'])

    combined_df.to_parquet('SO_2014_2022.pq', compression='gzip')
    combined_df.to_csv('SO_2014_2022.csv')

if __name__ == '__main__':
    main()
