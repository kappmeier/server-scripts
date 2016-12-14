#!/usr/bin/env bash
# © Jan-Philipp Kappmeier

if [[ $EUID -ne 0 ]]; then
    echo "Needs elevated rights to mount and start/stop service, use 'sudo ${0}' instead" 1>&2
    exit 1
fi

echo "Stopping Samba service smbd"
service smbd stop

echo "Loading partition info and searching drives"
# If parse_partitions.py is not found, make sure the path is available to sudo
# Example call is 'sudo "PATH=$PATH" ./mount_shares.sh'
cat /proc/partitions | grep sd | parse_partitions.py --datafile partitions.txt |
    while IFS= read -r cmd; do
        echo "Mounting with: $cmd"
        eval $cmd
done 

echo "Starting Samba service smbd"
service smbd start

