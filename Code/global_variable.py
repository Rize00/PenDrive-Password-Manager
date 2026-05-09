'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is for the global variables inside other modules. 
'''

import platform
import ctypes

#----------- GUI ----------#
color_bg_interface =  0.15, 0.15, 0.15, 1
color_text_settings = 1,1,1,1 #Color for settings
color_text_info = "black"
color_bg_selection = [1, 1, 1, 0.3]
color_text_selection = [0, 0, 0, 1.0]
color_default_text_selection = [1, 1, 1, 1]
color_bg_default_selection = [0, 0, 0, 0]
color_menu_voice = [1.0, 0.843, 0.0]
#---------- Variables ----------#
KeyString = ""
current_path = ""
remove_line_value = None
CheckUSBFlag = False


#--------- CONSTANT ---------#
data_language = {}
language = ""
main_filename_application = ".PasswordManagment.txt"
main_filename_backup_application = ".configPPM.dll"
hash_filename_application = ".HashPasswordManagment.txt"
title = "PenDrive-Password-Manager"
flag_update = False
sourceforge_url = "https://sourceforge.net/projects/pendrive-password-manager/"
