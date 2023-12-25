'''  
Function of the script:  
    Datetime-timestamp conversion for easier finding the log data.  

Background:   
    When watching the log video, if we spot the robot is doing a wrong pickup, 
    we will need to check the corresponding log folder to see the affordance and log history.
    However, it can be troublesome to find that log folder,
    because the time shown on the video is human-readable datetime, 
    but the log folder name is a unintuitive timestamp.
    Thus, we need some tool to help us do the timestamp-datetime conversion.

Usage of this script:
1. Convert timestamp to local datetime
    - Example usage: $ python convert_timestamp.py -t 1565385632480

2. Convert local datetime to timestamp
    - Example usage: $ python convert_timestamp.py -t '2019-08-09 17:20:32'

3. Convert all files/folders' timestamps inside a log directory        
    The program creates a output folder `output-dir\`, 
    then for each file/folder in `log-dir\`, the program preappend a timestamp to the file/folder,
    and then create its copy or softlink in `output-dir\'. 
    - Example usage: $ python convert_timestamp.py -i log -o log_timestamped --method copy
    - Example usage: $ python convert_timestamp.py -i log -o log_timestamped --method link

A detailed explanation of the arguments can be viewed by running:
$ python convert_timestamp.py -h
'''

import sys
import time
from datetime import datetime, timedelta
from shutil import copytree
import logging
import os
import argparse
import glob
import subprocess


def datetime_from_utc_to_local(utc_datetime):
    ''' Convert datetime from UTC to local '''
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(
        now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def datetime_to_timestamp(str_local_time):
    ''' Convert local datetime to timestamp '''
    timestamp = time.mktime(datetime.strptime(
        str_local_time, "%Y-%m-%d %H:%M:%S").timetuple())
    str_timestamp = str(int(timestamp) * 1000)  # unit: ms
    return str_timestamp


def timestamp_to_datetime(str_timestamp):
    ''' Convert timestamp to local datetime '''
    ts = int(str_timestamp)
    try:
        utc_datetime = datetime.utcfromtimestamp(ts)
    except ValueError:
        ts /= 1000.0
        utc_datetime = datetime.utcfromtimestamp(ts)
    local_datetime = datetime_from_utc_to_local(utc_datetime)
    str_local_datetime = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return str_local_datetime


def unittest_timestamp_datetime_conversion():
    ''' Unit test of the 2 functions:
            datetime_to_timestamp
            timestamp_to_datetime
        If you run this test in Boston, you should get:
            1565385632480 --> 2019-08-09 17:20:32
            2019-08-09 17:20:32 --> 1565385632000
    '''

    str_timestamp = "1565385632480"

    str_datetime = timestamp_to_datetime(str_timestamp)
    print("%s --> %s" % (str_timestamp, str_datetime))

    str_timestamp = datetime_to_timestamp(str_datetime)
    print("%s --> %s" % (str_datetime, str_timestamp))


def main1_convert_time_of_a_string(args):
    ''' 
    If the input is timestamp, print out its local datetime.
        Example usage: $ python convert_timestamp.py -t 1565385632480
    If the input is local datetime, print out its timestamp.
        Example usage: $ python convert_timestamp.py -t '2019-08-09 17:20:32'
    '''

    str_input = args.time_to_convert

    if len(str_input) > 4 and (2000 <= int(str_input[:4]) <= 2100):
        print("The input is a datetime")
        str_timestamp = datetime_to_timestamp(str_input)
        print("\nResult timestamp:")
        print(str_timestamp)
    else:
        print("The input is a timestamp")
        str_datetime = timestamp_to_datetime(str_input)
        print("\nResult local datetime:")
        print(str_datetime)


def main2_convert_timestamp_of_a_log_dir(args):

    cwd = os.getcwd() + "/"

    # -- parse input
    log_dir = args.log_dir + "/"
    output_dir = args.output_dir + "/"
    use_copy = args.method == "copy"

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # -- Read log-dir
    # log_folders_paths = filter(os.path.isdir, glob.glob(log_dir + "*"))
    log_folders_paths = glob.glob(log_dir + "*")
    print(len(log_folders_paths))

    for log_folder_path in log_folders_paths:

        # read timestamp and convert to readable datetime
        basename = log_folder_path.split('/')[1]
        timestamp = basename.split('_')[0]
        try:
            datetime = "[" + timestamp_to_datetime(timestamp) + "]"
        except:
            print(
                "WARNING: This file doesn't have a prefix timestamp: " + log_folder_path)
            print("         Skip it.")
            continue
        print(datetime)

        # operate
        if use_copy:  # copy
            subprocess.check_output(
                ['cp', '-r', cwd + log_folder_path, output_dir + datetime + basename])
        else:  # create softlink
            subprocess.check_output(
                ['ln', '-s', cwd + log_folder_path, output_dir + datetime + basename])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Two functions:"
        "(1) Change log-dir's timestamp to human-readable datetime and save to output-dir. "
        "(2) Use -t to input a time. The script will do the timestamp-datetime conversion and print the result. "
    )
    parser.add_argument("-i", "--log-dir", type=str, required=False, default="",
                        help="input log folder")
    parser.add_argument("-o", "--output-dir", type=str, required=False, default="",
                        help="rename timestamp to human readable datetime")
    parser.add_argument("-m",  "--method", type=str, required=False, default="link",
                        choices=["copy", "link"],
                        help="choose copy or link")
    parser.add_argument("-t", "--time_to_convert", type=str, required=False,
                        default="",
                        help="If this value is a timestamp, print the corresponding local datetime."
                        "If this value is a local datetime, print the corresponding timestamp.")
    args = parser.parse_args()

    if args.time_to_convert:
        print("Do the timestamp-datetime conversion.")
        main1_convert_time_of_a_string(args)
    else:
        if not args.log_dir or not args.output_dir:
            raise ValueError("You must input log-dir and output-dir")
        main2_convert_timestamp_of_a_log_dir(args)
    # unittest_time_conversion()
