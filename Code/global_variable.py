'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Version: 0.1
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is for the global variables inside other modules. 
'''

import platform
import ctypes

#----------- GUI ----------#
color_canvas =  "#848884" #"yellow" for debug   
color_text_info = "black"
color_bg_selection = [1, 1, 1, 0.3]
color_text_selection = [0, 0, 0, 1.0]
color_default_text_selection = [1, 1, 1, 1]
color_bg_default_selection = [0, 0, 0, 0]
color_menu_voice = [1.0, 0.843, 0.0]
#---------- Variables ----------#
KeyString = ""
data_language = {}
language = ""
main_filename_application = ".PasswordManagment.txt"
title = "PenDrive-Password-Manager"
current_path = ""
remove_line_value = None
CheckUSBFlag = False

