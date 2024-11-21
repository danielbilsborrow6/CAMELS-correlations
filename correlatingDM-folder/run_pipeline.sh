#!/bin/bash

mkdir -p CAMELS_CONFIGSDM

# Generate a list of numbers and pass them to xargs to execute in parallel
seq 500 504| xargs -n 1 -P 1 -I {} bash -c '
    # Record the start time
    START=$(date +%s)
    
    # Replace placeholder in config file
    sed "s/\${MY_VARIABLE}/$1/g" CAMELS_configDM.ini > CAMELS_CONFIGSDM/CAMELS_configDM$1.ini
    
    # Execute the pipeline with the new config file
    python w_pipeline1.py CAMELS_CONFIGSDM/CAMELS_configDM$1.ini
    
    # Record the end time
    END=$(date +%s)
    
    # Calculate and display the duration
    DURATION=$((END - START))
    echo "Task $1 completed in $DURATION seconds"
' _ {}