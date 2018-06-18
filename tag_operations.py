#!/usr/bin/env python

# Copyright 2015 Fetch Robotics Inc.
# Author: Sandeep Chahal

## @file

import sys
import json
import cv2 as cv
import apriltag as aptg
from res_pg import ResizingImagesDetails as Rs


class TagOperations:
    def __init__(self):
        self.dock_file = "dock_tag_numbers.txt"
        self.bot_file = "bot_tag_numbers.txt"
        self.cam_file = "cam_tag_numbers.txt"  # don't need this
        self.cam_first = "rtsp://admin:Robotslikevideo@hik"
        self.cam_last = "/Streaming/Channels/1"
        self.count = 0
        self.frames_to_be_processed = 4

    # reads initial files that contain numbers
    """limit : the file should contains just one number in each line"""
    def rd_init_file(self, my_file):
        my_list = []
        try:
            file_content = open(my_file, 'r')  # opening file in reading mode
        except IOError:
            print "cannot open ", my_file
            sys.exit(1)
        else:
            for line in file_content:  # reading line by line
                self.count += 1
                if line != '\n':  # handling last line or empty line in file

                    # line can't be convert to int then raise exception
                    try:
                        line = int(line)
                    except ValueError:
                        print "Error in line ", self.count, "of", my_file
                        print "Unable to read ", line, "Please enter one int in each line"
                        sys.exit(1)
                    else:
                        my_list.append(line)

            file_content.close()  # closing file
        return my_list

    def docks_found_in_cam(self, camera_number):
        docks = []
        try:
            cap = cv.VideoCapture(self.cam_first + str(camera_number) + self.cam_last)
        except IOError:
            print "unable to connect to hik", camera_number
            return False
        else:
            proceed_framed = 0
            while cap.isOpened() and self.frames_to_be_processed >= proceed_framed:
                ret, frame = cap.read()

                """converting image to gray scale and resizing"""
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                # resizing scale
                gray = Rs(70).rescaling_image(gray)
                """need work here to suppress print"""
                tags_in_image = aptg.Detector().detect(gray)

                """need to fix below statements"""

                # if dock is empty and tags are detected, update them as docks
                if not docks and len(tags_in_image) > 0:
                    for tag in tags_in_image:
                        temp_dict = {"tag_id": tag.tag_id,
                                     "rect_area": [[tag.corners[0][0], tag.corners[0][1]],
                                                   [tag.corners[1][0], tag.corners[1][1]],
                                                   [tag.corners[2][0], tag.corners[2][1]],
                                                   [tag.corners[3][0], tag.corners[3][1]]],
                                     "center": [tag.center[0], tag.center[1]], "cam_no": camera_number}
                        docks.append(temp_dict)

                # if dock is not empty update only when more docks are detected than there already are
                elif docks and len(docks) < len(tags_in_image):
                    docks = []
                    for tag in tags_in_image:
                        temp_dict = {"tag_id": tag.tag_id,
                                     "rect_area": [[tag.corners[0][0], tag.corners[0][1]],
                                                   [tag.corners[1][0], tag.corners[1][1]],
                                                   [tag.corners[2][0], tag.corners[2][1]],
                                                   [tag.corners[3][0], tag.corners[3][1]]],
                                     "center": [tag.center[0], tag.center[1]], "cam_no": camera_number}
                        docks.append(temp_dict)

                proceed_framed += 1
            return docks

    """reads all cameras find tags"""
    def finding_docks_all_cams(self, all_cam):  # returns unique value of tags_found

        docks_found = []  # docks found till now
        for cam in all_cam:
            print("looking from eyes of camera", cam)
            # need work make a list of camera that has not been able to open

            docks = self.docks_found_in_cam(cam)
            if docks and not docks_found:
                # if no dock is found yet in any cam
                for tag in docks:
                    docks_found.append(tag)
            elif docks and docks_found:
                    new_tag = True
                    for new_dock in docks:
                        for founds_dock_tag in docks_found:
                            if new_dock["tag_id"] == founds_dock_tag["tag_id"]:
                                new_tag = False
                        if new_tag:
                            docks_found.append(new_dock)

        return docks_found

    """writes the dock information inro a file"""
    def write_env_file(self, docks_info):
        # writing dock_information to file
        with open("env_info.json", 'w') as outfile:
            json.dump(docks_info, outfile)

    """setup of environment -> calls to read file, read cam find tags, write info in a file"""
    def setup_env_from_cams(self, cam_available="cam_tag_numbers.txt"):

        # loading all the cameras from the file
        cams = self.rd_init_file(cam_available)

        # all available docks and their position
        docks_found = self.finding_docks_all_cams(cams)

        # if docks found in then write their information in file
        if docks_found:
            self.write_env_file(docks_found)
        else:
            print("No Docks were found in env")
            sys.exit(1)

    """reading from file
    -> we can read few prior things like all the information about all docks
    """
    def read_env_file(self, my_file= "env_info.json"):
        # open the file
        with open(my_file) as json_file:
            env_info = json.load(json_file)
        return env_info

