#!/bin/sh
# Prepand copyright header
python -m reformat

black .
