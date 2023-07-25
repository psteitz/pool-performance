# process-configs.sh 
#
# Usage: process-configs.sh <version>
# <version> is the version number of the pool jar to be used in the tests.
#
# Requires xmllint, ant, sed, mvn to be installed and on the path.
#
# This sript has to be executed from the /src/pool directory of a local svn checkout
# of commons-performance.
#-----------------------------------------------------------------------------
# 1. Update the pool jar to be used in the tests with $1. 
#    a. If the jar is not in the local maven repo, download it.
#    b. Execute sed to update the version number in build.properties
# 2. For each config in ./configs
#    a. Replace config-pool.xml with a copy of config
#    b. ant
#    c. move renamed log file to ./results
# 3. Display summary table showing key test metrics.
# -----------------------------------------------------------------------------
# Start with default build properties
cp build.properties.sample build.properties

# Replace the version number in build.properties with $1
# On MacOS, sed if borked, so use gsed instead (needs brew install gnu-sed)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sed -i "s/commons-pool2\/2.2\/commons-pool2-2.2.jar/commons-pool2\/$1\/commons-pool2-$1.jar/g" build.properties 
elif [[ "$OSTYPE" == "darwin"* ]]; then
    gsed -i "s/commons-pool2\/2.2\/commons-pool2-2.2.jar/commons-pool2\/$1\/commons-pool2-$1.jar/g" build.properties
else
    echo "Unsupported OS"
fi
echo "Processing configs with pool version $1"
cat build.properties

# Make sure version $1 of the pool jar is in the local maven repo
mvn -DgroupId=org.apache.commons -DartifactId=commons-pool2 -Dversion=$1 dependency:get

# Loop over files in ./configs
#   1. Copy config to config-pool.xml
#   2. ant
#   3. Move log file to ./results
base_path=${HOME}/commons-performance/src/pool/pool-performance
for f in ${base_path}/configs/*; do    
    cp $f config-pool.xml
    name=$(xmllint --xpath '//configuration/name/text()' config-pool.xml)
    echo "Processing $name"
    ant
    mkdir -p ${base_path}/results
    mv ${HOME}/performance0.log.0 ${base_path}/results/pool2-version-$1-${name}.log
    echo "Processing completed for $name"
done
echo "Processing completed for all configs, pool version $1"