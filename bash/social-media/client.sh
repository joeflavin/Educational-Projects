#!/bin/bash

################################################
# client.sh                                    #
# Social Media Application Client              #
# ./client.sh [-m] clientId request [args]     #
################################################

# Set multi-message mode. Default is false, multi-mode is EXPERIMENTAL!!
multimode='false'
while getopts "m" opt; do
  case $opt in
    m) echo "multi-mode set to true" ; multimode='true' ; shift ;;
    *) echo "Invalid option flag given" >&2 ; shift ;;
  esac
done
#echo "multi-mode is $multimode"

# Set the field separator for outgoing messages
sep='¬'

# Check minimal arguments are present
if [ $# -lt 2 ]; then
	echo "Error: Client.sh Parameters problem" >&2
	exit 2
fi

# Check server is online and awaiting input (implies .lockfiles dir exists)
if [ ! -p server.pipe ]; then
	echo "Error: Server not running" >&2
	exit 10
fi

#echo "PID is $$"

# Process initial arguments
clientId="$1"
req="$2"
shift 2

# Check clientId for validity
if [ -z "$clientId" ]; then
 	echo "Error: client.sh Client ID invalid" >&2
 	exit 11
fi

{
 # Get lock on client input pipe to avoid potential conflicts
 flock -x 200 	# && echo "$$ aquired a lock"
 # echo "$$ in critical section"
 # Create input pipe if non-existant
 if [ ! -p "$clientId.pipe" ]; then mkfifo "$clientId.pipe"; fi

 # Process remaining arguments based on $req and take appropriate action
	case "$req" in
	   create)
	      # echo "Request is create"
	      if [ $# -eq 1 ]; then
			     echo "$clientId$sep$req$sep$1" > server.pipe
		    else
			     echo "Error: client.sh Parameters issue" >&2
					 # Clean up and exit with error code
					 rm "$clientId.pipe"
					 exit 22
		    fi
	      while read -r response; do
					 echo
			     echo "$response"
	      done < "$clientId.pipe"
	      ;;
	   add)
	      # echo "Request is add"
		    if [ $# -eq 2 ]; then
			     echo "$clientId$sep$req$sep$1$sep$2" > server.pipe
	      else
			     echo "Error: client.sh Parameters issue" >&2
					 rm "$clientId.pipe"
					 exit 22
		    fi
		    while read -r response; do
					 echo
			     echo "$response"
		    done < "$clientId.pipe"
	      ;;
	   post)
	      # echo "Request is post"
				case "$multimode" in
					true)
					# Experimental Multi-Message Mode
					mode=1
					if [ ! $# -lt 3 ]; then
						 receiver="$1"
						 sender="$2"
						 shift 2
						 msgforpiping=""
						 for arg in "$@"; do
								msgforpiping+="$arg"
								msgforpiping+="$sep"
						 done
						 # Strip final sep char from msg to avoid potential null argument
						 msgforpiping="${msgforpiping::-1}"
					else
						 echo "Error: client.sh Parameters issue" >&2
						 rm "$clientId.pipe"
						 exit 22
					fi
					echo "$clientId$sep$req$sep$mode$sep$receiver$sep$sender$sep$msgforpiping" > server.pipe
					flag="true"
					while [ "$flag" == "true" ]; do
						if read -r response; then
							if [ -z "$response" ]; then
								flag="false"
							else
								echo "$response"
							fi
						fi
					done < "$clientId.pipe"
					;;
					*)
					# Default Single-Message Mode
					mode=0
					if [ $# -eq 3 ]; then
						receiver="$1"
						sender="$2"
						msg="$3"
						echo "$clientId$sep$req$sep$mode$sep$receiver$sep$sender$sep$msg" > server.pipe
					else
						 echo "Error: client.sh Parameters issue" >&2
						 rm "$clientId.pipe"
						 exit 22
					fi
					while read -r response; do
					   echo "$response"
					done < "$clientId.pipe"
					;;
				esac
	      ;;
	   show)
	      # echo "Request is show"
		    if [ $# -eq 1 ]; then
			     echo "$clientId$sep$req$sep$1" > server.pipe
	      else
			     echo "client.sh Parameters issue" >&2
					 rm "$clientId.pipe"
					 exit 22
		    fi
		    while read -r response; do
					 echo "$response"
		    done < "$clientId.pipe"
		    ;;
	   shutdown)
	      # echo "Request is shutdown"
		    echo "$clientId$sep$req" > server.pipe
				while read -r response; do
					 echo "$response"
				done < "$clientId.pipe"
	      ;;
	   *)
	      echo "Error: client.sh Bad request"
	      rm "$clientId.pipe"
				exit 1
	esac
	# echo "$$ about to exit critical section"
	# Clean up before exiting
	rm "$clientId.pipe"
	exit 0
} 200>"./.lockfiles/clients/$clientId.lock"
