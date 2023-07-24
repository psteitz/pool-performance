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
cp ./build.properties.sample ./build.properties

# Replace the version number in build.properties with $1c
sed -i "s/commons-pool2\/2.2\/commons-pool2-2.2.jar/commons-pool2\/$1\/commons-pool2-$1.jar/g" ./build.properties 
echo "Processing configs with pool version $1"
cat build.properties

# Make sure version $1 of the pool jar is in the local maven repo
mvn -DgroupId=org.apache.commons -DartifactId=commons-pool2 -Dversion=$1 dependency:get

# Loop over files in ./configs
#   1. Copy config to config-pool.xml
#   2. ant
#   3. Move log file to ./results
for f in ./configs/*; do    
    cp $f config-pool.xml
    name=$(xmllint --xpath '//configuration/name/text()' config-pool.xml)
    echo "Processing $name"
    ant
    mv ${HOME}/performance0.log.0 ./results/pool2-version-$1-${name}.log
    echo "Processing completed for $name"
done
echo "Processing completed for all configs, pool version $1"