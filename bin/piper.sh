#!/bin/bash 
#------------------------------------------------------------------
# Executes $1 once for each line in $2, providing the values on the 
# line as command line arguments to $1.
# Both $1 and $2 need to be full paths.
# 
# By default, executions are sequential and blocking.  
#
# The -b command line option causes the commands to be 
# executed in parallel (via sh) in the background. 
#
# Example:  piper.sh ${HOME}/bin/mirror.sh ${HOME}/bin/directories.txt
# Lines in directories.txt are local and remote path spec
# which are the command line arguments to mirror.sh
#
# To run the jobs in parallel:
#  piper.sh -b ${HOME}/bin/mirror.sh ${HOME}/bin/directories.txt
#------------------------------------------------------------------
#
# Check arguments and check for -b flag.
#
ARGUMENTS=()
BACKGROUND=false
while [[ $# -gt 0 ]]
do
	token="$1"
	case $token in
	    -b|--background)
	    BACKGROUND=true
	    shift 
	    ;;
	    -v|--verbose)
	    VERBOSE=YES
	    ;;
	    -h|--help)
	    echo "Usage: 
	    echo " piper.sh [options] script arguments"
	    echo "  script is the script/command to execute"
	    echo "  arguments is a file with each line containing"
	    echo "  command line arguments for one execution of"
	    echo "  script."
	    echo "Supported options: "
	    echo " -b or --background
	    echo "   execute the script as a background process"
	    echo " -v or --verbose"
	    exit 0
	    ;;   
	    # 
	    # Add more options here
	    #  
	    *) 
	    ARGUMENTS+=("$1") # Not an option, must be command line argument
	    shift 
	    ;;
	esac
done
set -- "${ARGUMENTS[@]}" # reset arguments, removing option flags

if [ "$#" -ne 2 ]; then
    echo "Usage: piper.sh [options] <command> <arguments> "
    exit 1
fi

# If background flag is set, set up named pipe to track subshells
if [ "$BACKGROUND" = true ];
then 
    echo "Running tasks in background mode"
	trap 'rm commands.fifo' EXIT
	mkfifo commands.fifo
fi

# Loop to start executions. 
# If background flag is set, run jobs in subshells.
# Otherwise, run jobs in the background, but wait for each job to complete
# before starting the next one.
ct=0
processed=0
while read p; do
	if [ -z "$p" ]
    then
    	echo "Skipping blank line at line number $ct"
    else
	    cmd="$1 $p"
		echo "Starting $cmd"
	    if [ "$BACKGROUND" = true ];
	    then 
			echo "Starting background job $cmd"
	    	sh $cmd
			echo $processed >commands.fifo
			echo "Subshell started"
	    else 
	    	$cmd < /dev/null 
	    fi
	    processed=$((processed+1))
		echo "Finished $cmd"
    fi 
    ct=$((ct+1))
	echo "Looping after $ct lines from $2"
done < $2

# If background flag is set, wait for jobs to complete
if [ "$BACKGROUND" = true ];
then 
	for (( i=0;i<$processed;i++ ));
	do 
		echo "waiting on read "
		read out <commands.fifo;
		echo "successfully read $out"
	done
fi

echo "Processed $ct lines from $2"
echo "Executed $processed commands."
