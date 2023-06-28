![gender pay gap banner](./static/images/banner.png?)

[Click here to view the data story](https://p-adema.github.io/info-vis/)

# Information Visualisation: Gender Pay Gap

Jupyter Book visualising the gender pay gap for software developers,
using the Stack Overflow Annual Developer Survey data. For more details
regarding the datasets source and the cleaning process, see the
[Dataset and preprocessing](./docs/dataset-preprocessing.md) page.

# Table of Contents

- [Information Visualisation: Gender Pay Gap](#information-visualisation-gender-pay-gap)
- [Table of Contents](#table-of-contents)
- [Getting started](#getting-started)
- [Structure](#structure)
- [Usage](#usage)
- [Deploy](#deploy)
- [Dataset cleaning scripts](#dataset-cleaning-scripts)
- [Authors](#authors)

# Getting started

```
git clone git@github.com:p-adema/info-vis.git
cd info-vis
pip3 install -r requirements.txt
```

Additionally, install `conda` to setup a local environment.
- [MacOS installation instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html)
- [Windows installation instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html)
- [Linux installation instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)

In case you don't have `jupyter` installed locally, simply run `pip3 install jupyter`.

# Structure

```
.
├── LICENSE             # Code license
├── README.md           # General project information and instructions
├── _build              # Jupyter build that will be deployed
├── _config.yml         # Jupyter config file
├── _toc.yml            # Jupyter Table of Contents config file
├── data                # Contains dataset including cleaning scripts
├── docs                # Files to be published on GitHub Pages
├── notebooks           # Contains all notebook graphs used for the data story
├── requirements.txt    # Project dependencies
├── scripts             # Additional scripts used for deployment or cleaning
└── static              # Images, css and js files to be published on GitHub Pages
```

# Usage

Run `jupyter notebook` inside the root of this repository. All notebooks that go
into the data story should be created inside the `notebooks` directory. In order
to keep a maintainable and flexible structure, create one notebook per plot.

The main data story notebook is `./notebooks/story.ipynb`. In between texts, you
can include the results from other plots, simply by adding a new code cell with
the following contents `%run example_plot.ipynb`. Only the result of the last
cell inside `example_plot.ipynb` will be rendered.

# Deploy

In order to deploy to GitHub pages, you can run the following command in a
terminal: `./scripts/deploy.sh`. This will build the project, notebooks and adds
metadata to the `story.ipynb` in order to hide the input cells.

# Dataset cleaning scripts

Click [here](./scripts/cleaning/) to have a look at the scripts that have been
used to clean the datasets prior to the data story development phase.

# Authors
- Peter Adema
- Aize van Basten Batenburg
- Wim Berkelmans
- Kim Koomen
