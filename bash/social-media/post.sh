#!/bin/bash

################################################
# post.sh                                      #
# Post a msg from $sender to $receiver's wall  #
# syntax:                                      #
# ./post.sh receiver sender msg                #
################################################

# Check correct number of arguments are present
if [ $# -ne 3 ]; then
	echo "Error: parameters problem" >&2
	exit 2
fi

# Process arguments
receiver="$1"
sender="$2"
message="$3"

if ! [ -d "$receiver" ]; then
	echo "Error: Receiver does not exist" >&2
	exit 3
elif ! [ -d "$sender" ]; then
	echo "Error: Sender does not exist" >&2
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
	if ! grep -qx "$sender" "$receiver/friends"; then
		echo "Error:  Sender is not a friend of receiver" >&2
		exit 4
	else
		if echo "$sender: $message" >> "$receiver/wall"; then
			echo "OK: Message posted to wall"
			exit 0
		fi
	fi
} 200>"./.lockfiles/users/$receiver.lock"

echo "Error: Some other problem" >&2
exit 1
