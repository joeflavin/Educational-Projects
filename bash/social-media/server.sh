#!/bin/bash

################################################
# server.sh                                   #
# Social Media Application Server              #
################################################

# Create infrastructure if not present
if [ ! -p server.pipe ]; then	mkfifo server.pipe; fi
# Use different dirs for user-dir and client-pipe locks
# to avoid potential naming conflicts
if [ ! -d .lockfiles/users ]; then mkdir -p .lockfiles/users; fi
if [ ! -d .lockfiles/clients ]; then mkdir -p .lockfiles/clients; fi

# Listen for input from clients & take appropriate action
# Scripts called as bg processes with stdout & stderr redirected to client pipe
while true; do
   if IFS='¬' read -r -a input < server.pipe; then

   clientId=${input[0]}
   request=${input[1]}

   case "$request" in
      create)
			   user="${input[2]}"
         ./create.sh "$user" > "$clientId.pipe" 2>&1 &
         ;;
      add)
			   user="${input[2]}"
				 friend="${input[3]}"
         ./add.sh "$user" "$friend" > "$clientId.pipe" 2>&1 &
         ;;
	    post)
         mode="${input[2]}"
		     receiver="${input[3]}"
				 sender="${input[4]}"
         # Can restrict posting to one message per request
         # Or can post multiple messages sequentially (experimental!)
         case "$mode" in
           1)
           #echo "multi-mode true"
           for msg in "${input[@]:5}"; do
              ./post.sh "$receiver" "$sender" "$msg" > "$clientId.pipe" 2>&1 &
              sleep 0.25
  				 done
           wait
           echo $'\0' > "$clientId.pipe"
           ;;
           *)
           #echo "multi-mode false"
           msg="${input[5]}"
           ./post.sh "$receiver" "$sender" "$msg" > "$clientId.pipe" 2>&1 &
           ;;
         esac
				 ;;
	   show)
		     user="${input[2]}"
	       ./show.sh "$user" > "$clientId.pipe" 2>&1 &
	       ;;
	   shutdown)
        echo "Server shutting down." > "$clientId.pipe"
		    # Clean up and exit
	      rm server.pipe
        # Check there no active locks before cleaning up lockfiles
        # The following cause shellcheck warnings which according to
        # the shellcheck documentation can be safely ignored
        for lockfile in .lockfiles/users/*; do
          {
            flock -x 151
            rm "$lockfile"
          } 151>"$lockfile"
        done
        for lockfile in .lockfiles/clients/*; do
          {
            flock -x 151
            rm "$lockfile"
          } 151>"$lockfile"
        done
	      exit 0
	      ;;
	   *)
	      echo "Error: bad request" > "$clientId.pipe" 2>&1
	      exit 1
   esac
   fi
done
