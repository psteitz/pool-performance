#!/usr/bin/env python3
#
# analyze.py
# 0. gzip the files in /results and move the .tgz to ~
# 1. For each file in /results 
#      Add the data from each report to results[] an array of dictionaries,
#      each holding summary data from one report, identified by the
#      pool version and config name.
# 2. For each .tgz in POOL_PERFORMACE_PATH
#      Unzip the file, over-writing /results and repeat 1.
# 3. Analyze the data in the aggregated results[] array and write 
#    output csv to OUTPUT_PATH
# 4. Copy gzip created in 0. back to HOME_PATH + POOL_PERFORMACE_PATH,
#    and unzip it to restore /results
#
#   Records in results[] inclue
#
#   pool_version         : the version of the pool (e.g. 2.10.0, 2.12.0-SNAPSHOT)
#   config_name          : the value of the <name> element in commons-performance xml file used iin the run
#   latency_mean         : the mean latency across all client threads
#   latency_stddev       : the standard deviation of the latency across all client threads
#   on_time_startup_rate : the proportion of clients that started on time
#   id                   : a unique long integer id for the record
#   

import os
import random

HOME_PATH = os.path.expanduser('~')
POOL_PERFORMACE_PATH = "/commons-performance/src/pool/pool-performance"
RESULTS_PATH = HOME_PATH + POOL_PERFORMACE_PATH + "/results"
OUTPUT_PATH = HOME_PATH + POOL_PERFORMACE_PATH + "/summary.csv"

# Create orig.tgz containing the contents of RESULTS_PATH and move it to ~
os.chdir(HOME_PATH + POOL_PERFORMACE_PATH)
os.system("tar -czf orig.tgz .")
os.system("mv orig.tgz ~")

results = []

# Build a string with the remaining tokens starting at the given index
# in tokens, re-inserting "-" and removing the last 4 characters.
# So for example remaining_minus_suffix(pool2-version-2.10.0-sample-GKOP.log)
def remaining_minus_suffix(index, tokens):
    out = ""
    for i in range(index, len(tokens) - 1):
        out = out + tokens[i] + "-"
    out = out + tokens[len(tokens) - 1][:-4]
    return out

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
            record["config_name"] = remaining_minus_suffix(4, name_tokens)
        else:
            record["pool_version"] = name_tokens[2]
            record["config_name"] = remaining_minus_suffix(3, name_tokens)

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
os.chdir(HOME_PATH + POOL_PERFORMACE_PATH)
for file in os.listdir(HOME_PATH + POOL_PERFORMACE_PATH):
    # if the file name ends with .tgz
    if file.endswith(".tgz"):
        # unzip the file to overwrite reports in /results
        os.system("tar -xzf " + file)
        # process the files in /results
        process_files()
        print("Finished processing tgz file " + file)

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

# Restore state of /result to original
os.chdir(HOME_PATH + POOL_PERFORMACE_PATH)
os.system("mv ~/orig.tgz .")
os.system("tar -xzf orig.tgz")
os.system("rm orig.tgz")




