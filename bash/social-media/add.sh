#!/bin/bash

################################################
# add.sh                                       #
# Adds the user $friend to $users friend list  #
# ./add.sh user friend                         #
################################################

# Check correct number of arguments are present
if [ $# -ne 2 ]; then
	echo "Error: parameters problem" >&2
	exit 2
fi

# Process arguments
user="$1"
friend="$2"

if ! [ -d "$1" ]; then
	echo "Error: user does not exist" >&2
	exit 3
elif ! [ -d "$2" ]; then
	echo "Error: friend does not exist" >&2
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
	if grep -qx "$friend" "$user/friends"; then
		echo "Error: user already friends with this user" >&2
		exit 4
	else
		if echo "$friend" >> "$user/friends"; then
			echo "OK: friend added"
			exit 0
		fi
	fi
} 200>"./.lockfiles/users/$user.lock"

echo "Error: Some other problem" >&2
exit 1
