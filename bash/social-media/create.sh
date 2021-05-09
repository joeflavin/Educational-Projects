#!/bin/bash

##############################################
# create.sh                                  #
# Creates user directory and files for user  #
# ./create.sh user                           #
##############################################

# Check correct number of arguments are present
if [ $# -ne 1 ]; then
	echo "Error: Parameters problem" >&2
	exit 2
fi

# Process argument
user="$1"



# Create lockfile dir if non-existant.
# Allows server-independent use of base-command scripts.
if [ ! -d .lockfiles/users ]; then mkdir -p .lockfiles/users; fi
if [ ! -d .lockfiles/clients ]; then mkdir -p .lockfiles/clients; fi

{
	# Get a lock on $user lock file
	flock -x 200
	# Enter critical section

	if [ -d "$user" ]; then
		echo "Error: The user already exists" >&2
		exit 3
	fi
	if mkdir "$user" && touch "$user"/{friends,wall}; then
		echo "OK: user created"
	  exit 0
	fi
} 200>"./.lockfiles/users/$user.lock"

echo "Error: Something else went wrong" >&2
exit 1
