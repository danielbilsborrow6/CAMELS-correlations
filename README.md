# Intrinsic Alignments in CAMELS

Code repository for the detection of model parameter dependence in intrinsic alignments of galaxies in the CAMELS simulations, read paper here: ... . 

This code utilises simulation data avalable at https://users.flatironinstitute.org/~camels/ , galaxy data obtained via SUBFIND (~camels/FOF_Subfind/IllustrisTNG/LH/) and dark matter density obtained via snapshots (~camels/Sims/IllustrisTNG/LH/) at z=0. Storage is needed to download simulation data.

Pipeline to find correlation functions from ellipticities is build ontop of Harry Johnston's work (https://github.com/harrysjohnston/2ptPipeline)

### Submodule information
- `obtain-ellipticities-notebooks`
    - Download SUBFIND catalogues, filter galaxies and obtain ellipticities
- `ellipticities_LHsim`
    - projected ellipticity data for each LH sim in the IllustrisTNG suite of CAMELS. Each .pkl file contains data +x, +y and +z ellipticity projections for that sim.
- `correlating-folder`
    - pipeline inputs
    - notebooks that split galaxy catalgues and create RA DEC pipeline inputs.
- `correlatingDM-folder`
    - `run_pipelines.sh` `CAMELS_configDM-forall.ini` and calculates correlation functions for all 18 samples. `run_pipeline.sh` and `CAMELS_configDM.ini` for just 1 sample of 1000 sims.
    - `OUTPUT_CAMELS_DM_LH_x` and others are outputs of pipeline
    - notebooks collect outputs into condensed correlation function data
    - `get_DM.py` downloads snapshot then extracts DM data before deleting snapshot
- `test-dependence-folder`
    - analysis on correlation functions

