#!/bin/bash

(python -m flask --app main run) & (cd loki || exit; npm start)