'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is for addons
'''
import sys
import os
import global_variable
import requests
from packaging import version
import platform
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp
from kivy.uix.popup import Popup

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
#End def get_resource_path


def check_github_updates(current_version, repo_name):
    url = f"https://api.github.com/repos/{repo_name}/releases/latest"
    os_name = platform.system()
    estensione_cercata = ".exe" if os_name == "Windows" else ".deb"
    
    try:
        response = requests.get(url)
        if response.status_code == 200: #Everything is OK
            data = response.json()
            last_version = data["tag_name"]
            if version.parse(last_version) > version.parse(current_version):
                return True
                    
    except Exception as e:
        print(f"Errore: {e}")
    
    return False
#End def check_github_updates

class CustomPopup(BoxLayout):
        custom_font_size = NumericProperty(18)
        icon_type = StringProperty("info")
        message_text = StringProperty("")
        bg_hex = StringProperty("#ffffff")
        text_hex = StringProperty("#000000")
        custom_font = StringProperty("Roboto")
        custom_font_size = NumericProperty(15)
        btn_width = NumericProperty(0.3)
        btn_height = NumericProperty(0.8)
   
        def Get_icon(self, icon_name):
                if icon_name == "info":        return "information"
                elif icon_name == "warning":   return "alert"
                elif icon_name == "usb error": return "usb"
                elif icon_name == "donation":  return "hand-heart"
                elif icon_name == "account":   return "account-question"

        def On_ok_pressed(self): self.popup_instance.dismiss()
#End class custom popup

def Show_popup(title_, text_, icon_type_="info", hex_bg="#ffffff",width_=400, height_=250, f_size=14, btn_width_=0, btn_height_=0):
        content = CustomPopup(message_text=text_, icon_type=icon_type_, bg_hex=hex_bg, custom_font_size=f"{f_size}sp", btn_width = dp(btn_width_), btn_height=dp(btn_height_))
        
        pop = Popup(title=title_, content=content, size_hint=(None, None), size=(dp(width_), dp(height_)), auto_dismiss=False if icon_type_ == "error usb" else True)
        
        content.popup_instance = pop
        pop.open()
#End def show popup
    
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
