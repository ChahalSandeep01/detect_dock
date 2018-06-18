#!/usr/bin/env python

# Copyright 2015 Fetch Robotics Inc.
# Author: Sandeep Chahal

## @file

from tag_operations import TagOperations
import sys


class DockSurvillianceOperations:
    def __init__(self):
        self.Tg_Op = TagOperations()
        self.env_file = "env_info.json"

    """to set up any environment only by information of camera
    lim : no extra tag should be present except the tags on the docks
    """
    def setup_my_env(self, cam_file=None):
        if cam_file:
            self.Tg_Op.setup_env_from_cams(cam_file)  # one optional argument, default = "cam_address.txt"
        else:
            self.Tg_Op.setup_env_from_cams()  # one optional argument, default = "cam_address.txt"

        print "Congratulations.......\n" \
              "Your environment is set up"

    def free_docks(self, dock_number=None, cam_number=None):
        # return if a dock is available in a cam
        # return if a dock is available or busy
        # returns all the docks available and all functions available

        # answers the question if the dock is free, given cam number and dock number
        if dock_number and cam_number:
            # read cam  and determine all the available docks
            docks_found_from_cam = self.Tg_Op.finding_docks_all_cams(cam_number)

            for docks_found in docks_found_from_cam:
                if dock_number == int(docks_found["tag_id"]):
                    print dock_number, " is available"
                    return True  # return dock is available
            print "dock is not available"
            return False

        elif dock_number and not cam_number:
            cam_to_be_read = []  # cameras to be read

            # as we have docks and their respective camera number lets smartly look only at those camera
            all_docks_info = self.Tg_Op.read_env_file()

            # get the camera belongs to particular dock
            for dock_info in all_docks_info:
                if dock_info["tag_id"] == dock_number:
                    cam_to_be_read = dock_info["cam_no"]

            docks_found_from_cam = self.Tg_Op.finding_docks_all_cams(cam_to_be_read)

            for docks_found in docks_found_from_cam:
                if dock_number == int(docks_found["tag_id"]):
                    print dock_number, " is available"
                    return True  # return dock is available
            print "dock is not available"
            return False

        elif cam_number is None and dock_number is None:

            cam_to_be_read = []   # cameras to be read
            all_docks = []
            available_docks = []

            # as we have docks and their respective camera number lets smartly look only at those camera
            all_docks_info = self.Tg_Op.read_env_file()

            # get the list lis cameras to be read and docks(as all the docks are unique in file)
            for dock_info in all_docks_info:
                all_docks.append(dock_info["tag_id"])
                if not cam_to_be_read:
                    cam_to_be_read.append(dock_info["cam_no"])
                else:
                    if dock_info not in cam_to_be_read:
                        cam_to_be_read.append(dock_info["cam_no"])

            # read camera if dock is available put them in dock
            docks_found_from_cam = self.Tg_Op.finding_docks_all_cams(cam_to_be_read)

            # available dock
            for tags_found in docks_found_from_cam:
                if tags_found["tag_id"] in all_docks:
                    available_docks.append(tags_found["tag_id"])

            # busy docks
            busy_docks = list(set(all_docks) - set(available_docks))
            return available_docks, busy_docks

    def add_dock(self, dock_number=None, cam_number=None):

        if dock_number and cam_number:  # add dock by given camera and dock information

            docks_in_this_cam = []
            # changes to be made here , i.e new dock is added here
            env_info = self.Tg_Op.read_env_file()

            # get a list of docks in the given cam
            for docks_found in env_info:
                if cam_number == int(docks_found["cam_no"]):  # all docks present in this cam
                    docks_in_this_cam.append(docks_found["tag_id"])

            if not docks_in_this_cam:
                docks_in_this_cam = self.Tg_Op.docks_found_in_cam(cam_number)  # returns all tags in this

                for docks in docks_in_this_cam:
                    if docks["tag_id"] == dock_number:
                        env_info.append(docks)
                        self.Tg_Op.write_env_file(env_info)
                        print("new dock found")
                        print docks
                        print("dock added successfully")

                print("Dock could not be found")

            else:
                for old_docks in docks_in_this_cam:
                    if old_docks == dock_number:
                        print "CouldNotAddDock : dock_number ", dock_number, "is already in the env on this cam"
                        sys.exit(1)
                docks_in_this_cam = self.Tg_Op.docks_found_in_cam(cam_number)
                for docks in docks_in_this_cam:
                    if docks["tag_id"] == dock_number:
                        env_info.append(docks)
                        self.Tg_Op.write_env_file(env_info)
                        print("new dock found")
                        print docks
                        print("dock added successfully")
                    print("Dock could not be found")

        else:  # need work extra functionality can be added like if
            # only dock_number is provided, only cam number is provided, nothing is provided
            print "please provide dock number and camera number"

    def remove_docks(self, dock_number=None):
        found_dock = False
        if dock_number:
            env_info = self.Tg_Op.read_env_file()
            for docks_found in env_info:
                if dock_number == int(docks_found["tag_id"]):  # all docks present in this cam
                    found_dock = True
                    env_info.remove(docks_found)
            if found_dock:
                self.Tg_Op.write_env_file(env_info)
                print "dock has been removed"
            else:
                print "could not locate dock"

