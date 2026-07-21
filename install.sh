#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install --quiet --upgrade pip

pip3 install setuptools==82.0.0 

# pip3 install --quiet "setuptools<81"
# pip3 install --quiet 'urllib3<2.0' 
pip3 install --quiet -e /Volumes/GitHub/tm2p
pip3 install --quiet black isort ipykernel

# pip3 install "nbformat>=4.2.0"

python3 -m spacy download en_core_web_lg
python3 -m nltk.downloader averaged_perceptron_tagger
python3 -m nltk.downloader punkt
