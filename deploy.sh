#!/usr/bin/env bash

rm -rf _build/
jupyter-book build ./notebooks/story.ipynb
ghp-import -n -p -f _build/_page/notebooks-story/html
