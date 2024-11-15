#!/bin/bash

mkdir -p CAMELS_CONFIGS

# Generate a list of numbers and pass them to xargs to execute in parallel
seq 0 1000 | xargs -n 1 -P 11 -I {} bash -c '
    # Replace placeholder in config file
    sed "s/\${MY_VARIABLE}/$1/g" CAMELS_config.ini > CAMELS_CONFIGS/CAMELS_config$1.ini
    
    # Execute the pipeline with the new config file
    python w_pipeline1.py CAMELS_CONFIGS/CAMELS_config$1.ini
    
    echo "$1"
' _ {}
