#!/usr/bin/env python3
# coding: utf-8
# © Jan-Philipp Kappmeier

r""" Mounts partitions from usb drives defined by their partition sizes.

Reads a set of partitions to be mounted, including their mount points from a
configuration file and parses the output from the disk info tool to detect
under which names the drives are accessible by the system.
"""

from argparse import ArgumentParser, FileType
from collections import defaultdict
import sys

def main():
    """Entry point for partition parsing tool.

    Parses command line, loads partition data from the file system and maps to mount points.
    """
    parser = specify_parser()
    args = parser.parse_args()

    mapping = init_data(args.datafile[0])
    loaded_data = read(args.input)

    mount(mapping, loaded_data)

def specify_parser():
    """Specifies the argument parser for parse_partitions.

    Required parameters are a 'datafile' containing information of the partitions to be loaded and
    input stream of partition data from /proc/partitions
    """
    parser = ArgumentParser()

    parser.add_argument('input', nargs='?', type=FileType('r'), default=sys.stdin)
    parser.add_argument('--datafile', dest="datafile", required=True, nargs=1, type=FileType('r'))
    return parser


def init_data(partitions_file):
    """Loads data from the partition information file.

    The file contains information about file sizes of partitions to be loaded. For each drive two
    lines describe the size of the drive and the sizes of the partitions on that drive.

    Drive information is formatted as 'drive:<size>', while partition information is formatted as
    <size>:<mount point>;<size>:<mount point>;... for example

    drive:2930264064
    2930263040:/mnt/data/
    drive:2930264064
    1953503748:/mnt/more_data/;976752000:/scratch/
    """
    mapping = []

    drive_size = None
    for line in partitions_file:
        if drive_size is None:
            drive_size = parse_drive_size(line.rstrip())
        else:
            partitions_list = parse_partitions(line.rstrip())
            mapping.append((drive_size, partitions_list))
            drive_size = None

    return mapping

def parse_drive_size(line):
    """Parses a drive line in the partition information file.
    """
    parts = line.split(":")
    if len(parts) != 2 or parts[0] != "drive":
        raise ValueError("Drive size line format is 'drive:<size>'")
    return parts[1]

def parse_partitions(line):
    """Parses a partitions line in the partition information file.
    """
    return [parse_partition(entry) for entry in line.split(";")]

def parse_partition(partition):
    """Parses one parttiion tuple consisting of size and mount point.
    """
    partition_data = partition.split(":")
    if len(partition_data) != 2:
        raise ValueError("Partitions line parts format is 'size:mount'")
    return partition_data

def read(inputstream):
    """Reads data coming from the input stream coming from /proc/partitions.

    Example input:
        8        0  976762584 sda
        8        1     242688 sda1
        8        2          1 sda2
        8        5  976517120 sda5
        8       48 2930264064 sdb
        8       49 2930263040 sdb1
        8       32 2930264064 sdc
        8       33 1953503748 sdc1
        8       34  976752000 sdc2
    """
    current = None
    mapping = defaultdict(list)
    current_partitions = None
    for line in inputstream:
        # capacity = 2
        # name = 3
        line_parts = line.split()
        capacity = line_parts[2]
        name = line_parts[3]

        if len(name) == 3:
            current = capacity
            current_partitions = []
            mapping[current].append(current_partitions)
        else:
            current_partitions.append((capacity, name))
    return mapping

def mount(mapping, loaded_data):
    """Finds the partittions in the loaded partition data fitting to the expected drive/partitons.
    """
    for drive_size, partition_infos in mapping:
        mount_single(partition_infos, loaded_data[drive_size])

def mount_single(partition_size, drives):
    """Searches for a drive fitting to given expected parttiions and prints the command.
    """
    for drive_list in drives:
        if are_equal(drive_list, partition_size):
            for drive_info, partition_info in zip(drive_list, partition_size):
                mount_pattern = "mount -t ntfs -o uid=1000,gid=1000,umask=0002 /dev/{} {}"
                mount_cmd = mount_pattern.format(drive_info[1], partition_info[1])
                print(mount_cmd)

def are_equal(drive_list, partition_infos):
    """Checks whether partitions in a drive fit to the expected partition infos.
    """
    if len(drive_list) == len(partition_infos):

        for drive_info, partition_info in zip(drive_list, partition_infos):
            if drive_info[0] != partition_info[0]:
                return False
        return True
    return False

if __name__ == '__main__':
    main()

