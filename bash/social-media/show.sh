#!/bin/bash

################################################
# show.sh                                      #
# Shows the contents of a $user's wall         #
# ./show.sh user                               #
################################################

# Check correct number of arguments are present
if [ $# -ne 1 ]; then
	echo "Error: parameters problem" >&2
	exit 2
fi

# Process argument
user="$1"

if ! [ -d "$user" ]; then
	echo "Error: user does not exist" >&2
	exit 3
fi

# Create lockfile dir if non-existant.
# Allows server-independent use of base-command scripts.
if [ ! -d .lockfiles/users ]; then mkdir -p .lockfiles/users; fi
if [ ! -d .lockfiles/clients ]; then mkdir -p .lockfiles/clients; fi

{
	# Get a lock on $user lock file
	flock -x 200
	# Enter critical section
	wall="$(cat "$user/wall")"
	# if [ -n "$wall" ]; then
		 echo
	   echo "$wall"
	# else
	# 	echo "Wall empty. Nothing to show."
	# fi
	echo
	exit 0
} 200>"./.lockfiles/users/$user.lock"

echo "Error: Some other problem" >&2
exit 1
