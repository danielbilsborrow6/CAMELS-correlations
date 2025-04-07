#!/bin/bash

CONFIG_TEMPLATE="CAMELS_configDM-forall.ini"
mkdir -p CAMELS_CONFIGSDM

# Array of "folder:coord:output"
DATA_CATEGORIES=(
  "RADEC:x:OUTPUT_CAMELS_DM_LH_x"
  "RADEC:y:OUTPUT_CAMELS_DM_LH_y"
  "RADEC:z:OUTPUT_CAMELS_DM_LH_z"
  "RADEC_ellipticals:x:OUTPUT_CAMELS_DM_ELL_LH_x"
  "RADEC_ellipticals:y:OUTPUT_CAMELS_DM_ELL_LH_y"
  "RADEC_ellipticals:z:OUTPUT_CAMELS_DM_ELL_LH_z"
  "RADEC_spirals:x:OUTPUT_CAMELS_DM_SPI_LH_x"
  "RADEC_spirals:y:OUTPUT_CAMELS_DM_SPI_LH_y"
  "RADEC_spirals:z:OUTPUT_CAMELS_DM_SPI_LH_z"
  "RADEC_noMAG:x:OUTPUT_CAMELS_DM_NOMAG_LH_x"
  "RADEC_noMAG:y:OUTPUT_CAMELS_DM_NOMAG_LH_y"
  "RADEC_noMAG:z:OUTPUT_CAMELS_DM_NOMAG_LH_z"
  "RADEC_noMAG_ellipticals:x:OUTPUT_CAMELS_DM_NOMAG_ELL_LH_x"
  "RADEC_noMAG_ellipticals:y:OUTPUT_CAMELS_DM_NOMAG_ELL_LH_y"
  "RADEC_noMAG_ellipticals:z:OUTPUT_CAMELS_DM_NOMAG_ELL_LH_z"
  "RADEC_noMAG_spirals:x:OUTPUT_CAMELS_DM_NOMAG_SPI_LH_x"
  "RADEC_noMAG_spirals:y:OUTPUT_CAMELS_DM_NOMAG_SPI_LH_y"
  "RADEC_noMAG_spirals:z:OUTPUT_CAMELS_DM_NOMAG_SPI_LH_z"
)

# Loop over data categories
for entry in "${DATA_CATEGORIES[@]}"; do
  IFS=":" read -r CATEGORY COORD OUTPUT <<< "$entry"
  mkdir -p "$OUTPUT"

  echo "Running for $CATEGORY ($COORD) -> $OUTPUT"

  # Loop over 0–1000
  for i in $(seq 0 1000); do
    START=$(date +%s)

    CONFIG_OUT="CAMELS_CONFIGSDM/CAMELS_configDM_${CATEGORY}_${COORD}_${i}.ini"

    # Generate new config with substituted variables
    sed -e "s|\${CATEGORY}|${CATEGORY}|g" \
        -e "s|\${COORD}|${COORD}|g" \
        -e "s|\${MY_VARIABLE}|${i}|g" \
        -e "s|\${OUTPUT_FOLDER}|${OUTPUT}|g" \
        "$CONFIG_TEMPLATE" > "$CONFIG_OUT"

    # Run the pipeline
    python w_pipeline1.py "$CONFIG_OUT"

    END=$(date +%s)
    echo "[$CATEGORY $COORD #$i] Done in $((END - START))s"
  done
done

