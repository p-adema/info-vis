#!/usr/bin/env bash

ROOT_DIR=$(cd "$(dirname "$0")/.."; pwd -P)

python3 $ROOT_DIR/scripts/remove_code_input_cells.py

rm -rf $ROOT_DIR/_build/
jupyter-book build $ROOT_DIR/notebooks/story.ipynb
ghp-import -n -p -f $ROOT_DIR/_build/_page/notebooks-story/html
