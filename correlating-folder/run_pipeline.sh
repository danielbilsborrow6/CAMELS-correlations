#!/bin/bash

# Loop through desired range to create multiple config files and execute the pipeline
for i in {0..29}; do
    # Replace placeholder in config file
    sed "s/\${MY_VARIABLE}/$i/g" CAMELS_config.ini > CAMELS_config$i.ini
    
    # Execute the pipeline with the new config file
    python w_pipeline1.py CAMELS_config$i.ini
    
    echo $i
done


