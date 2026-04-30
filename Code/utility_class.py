'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Version: 0.1.3
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is for addons
'''
import sys
import os
import global_variable

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Language():
    '''This class works with json file. It's main purpose is to translate string for the user '''

    def __init__(self):
        import json  # For language translation
        path = get_resource_path('translation.json')
        with open(path, 'r', encoding='utf-8') as f:
            global_variable.data_language = json.load(f)

    def _(key):
        try:
            return global_variable.data_language[global_variable.language].get(key, key)
        except Exception as e:
            pass

    def Load_language(x):
        global_variable.language = x
# End class Language
Language()
