#!/usr/bin/env python3
#
# analyze.py
# 0. Create an empty results array
# 1. For each .tgz file in /results followed by each file the current directory,
#   a. Unzip the .tgz file to overwrite reports in /results
#   b. Add the data from each report to results[] an array of dictionaries,
#      each holding summary data from one report, identified by the
#      pool version and config name.
# 2. Write a summary report to /results/summary.csv

# To process a single report in 2a, look at the file name, e.g,
#     pool2-version-2.10.0-sample-GKOP.log
# 
# Each file creates a record with the following keys:
#
#   pool_version         : the version of the pool 2.10.0 for the example above)
#   config_name          : the configuration of the pool (sample-GKOP for the example above)
#   latency_mean         : the mean latency across all client threads
#   latency_stddev       : the standard deviation of the latency across all client threads
#   on_time_startup_rate : the proportion of clients that started on time
#   id                   : a unique long integer id for the record
#   
# Start by storing all records in an array of dictionaries, one for each report.

# Loop over files in /results, reading each as a text file,
# First set pool-version and config-name based on the file name.
# Then look for the end block in the input file:
#
# Overall summary statistics (all threads combined) LATENCY
# StatisticalSummaryValues:
# n: 1000000
# min: 0.0011900000972673297
# max: 363.2711181640625
# mean: 0.019214021268693867
# std dev: 0.6825760452893023
# 
# Set latency_mean to the value of mean: in the block above.
# Similarly, set latency_stddev to the value of std dev: in the block above.

# To set on_time_startup_rate, search for the following block in the input file:
#
# Overall summary statistics (all threads combined) ON TIME STARTUP RATE
# StatisticalSummaryValues:
# n: 1000000
# min: 0.0
# max: 1.0
# mean: 0.9998920000000002
# std dev: 0.01039174884167453
# 
# Set on_time_startup_rate to the value of mean: in the block above.
#
# Finally, add a dictionary to the results array with the keys and values set above.\
# 
#

import os
import random

results = []
# loop over files in /results
# Use absolute path to /results
HOME_PATH = os.path.expanduser('~')
RESULTS_PATH = HOME_PATH + "/commons-performance/src/pool/pool-performance/results"
OUTPUT_PATH = HOME_PATH + "/commons-performance/src/pool/pool-performance/summary.csv"
count = 0
def process_files():
    global count
    for file in os.listdir(RESULTS_PATH):
        print("Processing file " + file)
        record = {}
        # use the name of the file to set pool_version and config_name
        name_tokens = file.split("-")
        # name is like pool2-version-2.10.0-sample-GKOP.log
        #                0      1       2       3      4
        if "SNAPSHOT" in file:
            record["pool_version"] = name_tokens[2] + "-" + name_tokens[3]
            record["config_name"] = name_tokens[4] + "-" + name_tokens[5][:-4]
        else:
            record["pool_version"] = name_tokens[2]
            record["config_name"] = name_tokens[3] + "-" + name_tokens[4][:-4]

        # Set ID to the next sequential integer
        record["id"] = count;

        # open the file
        with open(RESULTS_PATH + "/" + file) as f:
            # read the file into a lines array
            lines = f.readlines()
            # loop over lines, looking for overall LATENCY and ON TIME STARTUP RATE blocks
            for i in range(len(lines)):
                if "Overall summary statistics (all threads combined) LATENCY" in lines[i]:
                    # look for the next line that contains "mean:"
                    for j in range(i, len(lines)):
                        if "mean:" in lines[j]:
                            # set latency_mean to the value of mean:
                            record["latency_mean"] = float(lines[j].split(":")[1])
                            break
                    # look for the next line that contains "std dev:"
                    for j in range(i, len(lines)):
                        if "std dev:" in lines[j]:
                            # set latency_stddev to the value of std dev:
                            record["latency_stddev"] = float(lines[j].split(":")[1])
                            break
                # if the line contains "ON TIME STARTUP RATE", look for the next line that contains "mean:"
                if "Overall summary statistics (all threads combined) ON TIME STARTUP RATE" in lines[i]:
                    for j in range(i, len(lines)):
                        if "mean:" in lines[j]:
                            # set on_time_startup_rate to the value of mean:
                            record["on_time_startup_rate"] = float(lines[j].split(":")[1])
                            break
        print ("Finished processing file " + file + " with record " + str(record))
        # add the record to the results array
        results.append(record)
        count += 1

# Process the files in /results
process_files()
# For each file named *.tgz in HOME_PATH + "/commons-performance/src/pool/pool-performance/
#  a. Unzip the .tgz file to overwrite reports in /results
#  b. Process the files in /results
#
# loop over files in HOME_PATH + "/commons-performance/src/pool/pool-performance/
for file in os.listdir(HOME_PATH + "/commons-performance/src/pool/pool-performance/"):
    # if the file name ends with .tgz
    if file.endswith(".tgz"):
        # unzip the file to overwrite reports in /results
        os.system("tar -xzf " + file + " -C " + RESULTS_PATH)
        # process the files in /results
        process_files()
        print("Finished processing file " + file)

# Display the count of files processed
print("Processed " + str(count) + " files")

print("Analyzing results")
#
# create output array of dicts
# out has records averaged across version-config pairs
out = []

# For each version-config pair, 
# compute the mean of the means and the mean of the standard deviations of latency_mean
# and the mean of on_time_startup_rate, and add a record to out with the
# following keys and values:
#   pool_version : the version of the pool
#   config_name : the configuration of the pool
#   latency_mean : the mean of the means of latency_mean across all reports
#   latency_stddev : the mean of the standard deviations of latency_mean across all reports
#   on_time_startup_rate : the mean of the means of on_time_startup_rate across all reports
#   num_reports : the number of reports used to compute the means above

# loop over versions
# First search results to build a list of unique versions
versions = []
for record in results:
    if record["pool_version"] not in versions:
        versions.append(record["pool_version"])

# Do the same for config names
configs = []
for record in results:
    if record["config_name"] not in configs:
        configs.append(record["config_name"])

# Now loop over versions and configs to create output records
for version in versions:
    for config in configs:
        # create a record with the keys and values described above
        print("Analyzing version " + version + " config " + config)
        record = {}
        record["pool_version"] = version
        record["config_name"] = config
        num_reports = 0
        # loop over records in results, looking for records with matching
        # version and config_name
        latency_means = []
        latency_stddevs = []
        on_time_startup_rates = []
        for rec in results:
            if rec["pool_version"] == version and rec["config_name"] == config:
                print("Found matching record " + str(rec) + " config " + config + " version " + version)
                if "latency_mean" in rec and "latency_stddev" in rec and "on_time_startup_rate" in rec:
                    latency_means.append(rec["latency_mean"])
                    latency_stddevs.append(rec["latency_stddev"])
                    on_time_startup_rates.append(rec["on_time_startup_rate"])
                    num_reports += 1
        # compute the mean of the means and the mean of the standard deviations
        # of latency_mean and the mean of on_time_startup_rate
        if len(latency_means) > 0 and len(latency_stddevs) > 0 and len(on_time_startup_rates) > 0:
            record["latency_mean"] = sum(latency_means) / len(latency_means)
            record["latency_stddev"] = sum(latency_stddevs) / len(latency_stddevs)
            record["on_time_startup_rate"] = sum(on_time_startup_rates) / len(on_time_startup_rates)
            record["num_reports"] = num_reports
            # add the record to out
            out.append(record)
        else :
            print("No good matching records for config " + config + " version " + version)
        print("Finished analyzing version " + version + " config " + config)
        print(str(record))
    # write out the results
    with open(OUTPUT_PATH, "w") as f2:
        f2.write("pool_version,config_name,latency_mean,latency_stddev,on_time_startup_rate,num_reports\n")
        for record in out:
            out_str = record["pool_version"] + "," + record["config_name"] + \
            "," + str(record["latency_mean"]) + "," + str(record["latency_stddev"]) + \
            "," + str(record["on_time_startup_rate"]) + \
            "," + str(record["num_reports"]) + "\n"
            f2.write(out_str)



