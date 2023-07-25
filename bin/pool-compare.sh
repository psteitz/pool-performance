#!/bin/bash
# -----------------------------------------------------------------------------
# For each pool version number in ./versions.txt and each config file in ./configs
# Run commons-performance pool soak tests and collect results in ./results
# -----------------------------------------------------------------------------
cd ${HOME}/commons-performance/src/pool
bin_path=pool-performance/bin
${bin_path}/piper.sh ${bin_path}/process-configs.sh pool-performance/versions.txt 
# process-configs.sh  
#    * Creates a config for an input version and each run profile in ./configs.
#    * Runs GOP or GKOP tests for each config
#    * Collects renamed log files in ./results

