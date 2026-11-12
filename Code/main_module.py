# -*- coding: utf-8 -*-
'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Copyright © 2026

License: GNU GPL v3 (General Public License)
'''

'''
No donazioni
Aggiunte voci nelle impostazioni (CSV,QR)
Aggiunto un timer affinchè dopo aver copiato le password, gli appunti vengano cancellati
QR è solo error correction L
Rimossi lingua francese e spagnolo
Il tasto per cancellare ora è CANC e non backspace
'''


CURRENT_VERSION = "V0.2.2"
REPO_NAME = "Rize00/PenDrive-Password-Manager"

from utility_class_and_functions import * #Module for get resource path and others
#-------------------------------------------    Python modules    -------------------------------------#
import platform
import os
import getpass
from pathlib import Path
import sys
import threading
import time
import webbrowser

from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand') #Disable multitouch

if platform.system() == "Linux":
        Config.set('kivy', 'window_icon', get_resource_path('assets/logo.png'))
elif platform.system() == "Windows":
        Config.set('kivy', 'window_icon', get_resource_path('assets/logo.ico'))
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton, ActionGroup
import kivy.utils as utils
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton
from kivymd.uix.slider.slider import MDSlider
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox 
#---------------------------- Application modules ------------------------#
import crypting
import global_variable
from pen_drive import USBRecursiveScanner

def Get_os_language():
        try:
                import locale

                lang = None
                if platform.system() == "Windows":
                        import ctypes
                        windll = ctypes.windll.kernel32
                        language = windll.GetUserDefaultUILanguage()
                        lang = locale.windows_locale.get(language)
                elif platform.system() == "Linux":
                        lang, _ = locale.getlocale()
                        
                if not lang: return "en"
                
                lang_lower = lang.split('_')[0].lower()
                available = ["en", "it", "ru", "de"]

                return lang_lower if lang_lower in available else "en"

        except Exception as e: return "en"  # Fallback
#End def Get_os_language

global_variable.language = Get_os_language() #Set default language in this application
global_variable.flag_update = check_github_updates(CURRENT_VERSION,REPO_NAME) #Checks update"

USB = USBRecursiveScanner() #Instanziate the class
#--------------------------------------------------------------------------------------------------#
try:
        Builder.load_file(get_resource_path('GUI_option_linux.kv')) #Load GUI file
        Builder.load_file(get_resource_path('settings_interface.kv')) #Load settings file
        Builder.load_file(get_resource_path('change_keys_settings_interface.kv'))
        Builder.load_file(get_resource_path('csv_settings_interface.kv'))
except Exception as e:
    print(f"\nERROR FILE KV: \n{e}\n")

def Show_update_dialog():
        app = MDApp.get_running_app()
        font_size_title = int(sp(48)) 
        font_size_text = int(sp(40))
        width_ = 0.9

        def Update():
                try:
                        webbrowser.open(global_variable.sourceforge_url)
                        os._exit(0)
                except Exception as e: pass

        try:
                app.update_dialog = MDDialog(title=f"[size={font_size_title}]{Language._('update true')}[/size]", text=f"[size={font_size_text}]{Language._('update true msg')}[/size]",
                                             auto_dismiss=False, size_hint=(width_, None),
                                             buttons=[
                                                     MDFlatButton(text=Language._("update no"),font_size=sp(40), on_release=lambda x: app.update_dialog.dismiss()),
                                                     MDFlatButton(text=Language._("update yes"),font_size=sp(40),theme_text_color="Custom",text_color=app.theme_cls.primary_color,
                                                                  on_release=lambda x: Update() ) ],
                                             )
                app.update_dialog.open()
        except Exception as e: pass
        
#End def show update dialog

class GUI_option_linux(FloatLayout):
        def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.selection = None
        
        def SetKey(self): #SetKey button Command
                key = self.ids.key_input.text
                if len(key) == 16 and self.ids.key_input.readonly==False:
                        self.DisableSetKey()
                        global_variable.KeyString = key #Set the global variable
                        #Remove the voice inside the list box
                        voices = self.ids.passwordlistbox.ids.container
                        voices.clear_widgets()
                        #Update the list box of password
                        self.ShowPasswordList()
                        
                elif self.ids.key_input.readonly==True: #if the input box is disabled
                        self.EnableSetKey()
                        global_variable.KeyString = ""
                        if self.selection: #Show selection
                                self.selection.background_color = global_variable.color_bg_default_selection
                                self.selection.color = global_variable.color_default_text_selection
                                self.selection = None
                        #Append to clipboard
                        from kivy.core.clipboard import Clipboard
                        Clipboard.copy(" ")
                else:
                        #Show some errors
                        Show_popup(title_=Language._("key error"), text_=Language._("key len error msg"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                   height_=dp(global_variable.popup_height), f_size=sp(28),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
        #End def setkey
        
        def ShowPasswordList(self):
                try:
                        aviable_list = USB.PasswordListUpdate() #Take the list
                        if aviable_list: #if there is something
                                aviable_list.sort() #Sort the list in alphabetic order
                                for i in range(len(aviable_list)):
                                        #Make a new visual button
                                        new_voice = Button(text=aviable_list[i], background_color=global_variable.color_bg_default_selection,
                                                           background_normal='', color=global_variable.color_default_text_selection,
                                                           size_hint_y=None, height=dp(40),
                                                           halign='left', valign='center', font_size='50dp')
                                        new_voice.bind(on_release=self.CopyPassword)
                                        self.ids.passwordlistbox.ids.container.add_widget(new_voice)
                                Window.bind(on_key_down=self.DeleteVoice) #Enable BACKSPACE
                        else:
                                Window.unbind(on_key_down=self.DeleteVoice) #Disable BACKSPACE
                except Exception as e: pass
        #end def showpassword

        def CopyPassword(self, instance):
                if global_variable.KeyString != "": #Check if key string is inserted
                        if self.selection:
                                #Return to normal visual effects
                                self.selection.background_color = global_variable.color_bg_default_selection
                                self.selection.color = global_variable.color_default_text_selection

                        self.selection = instance #Save the istance
                        #Add visual effects
                        self.selection.background_color = global_variable.color_bg_selection
                        self.selection.color = global_variable.color_text_selection

                        #Now the magic, copy the password
                        prefix = crypting.crypt_aes(self.selection.text) #Crypt the selection
                        row = USB.row_filtrer_beginning(global_variable.main_filename_application, prefix.hex())[0] #Find the row
                        password = row.split('|')[1].strip() #Take the crypted password
                        password = crypting.decrypt_aes(password) #Decrypt it
                        #Append to clipboard
                        from kivy.core.clipboard import Clipboard
                        Clipboard.copy(password)
                        Clock.schedule_once(lambda dt: Clipboard.copy(" "), global_variable.time_to_copy) #Delete clipboard
                else:
                        #Append to clipboard the empty string
                        from kivy.core.clipboard import Clipboard
                        Clipboard.copy(" ")
                        Show_popup(title_=Language._("key error"), text_=Language._("key set msg"),icon_type_="warning",
                                   width_=dp(global_variable.popup_width), height_=dp(global_variable.popup_height), f_size=sp(24),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
        #end copypassword

        def DeleteVoice(self, window, key, *args):
                from kivy.core.window import Keyboard
                
                if key == Keyboard.keycodes['delete'] and self.selection: #If backspace and selection
                        #remove the voice
                        self.ids.passwordlistbox.ids.container.remove_widget(self.selection)
                        #Selection reset
                        self.selezionato = None
                        USB.RemoveLine(self.selection.text) #Remove the username
                        self.RemoveAllInPasswordBox() #Clear list
                        self.ShowPasswordList() #Update the list
                        return True
                return False
        #end deletevoice
                
        def DisableSetKey(self):
                self.ids.key_input.readonly=True
                self.ids.key_input.text_color_normal= 0, 1, 0, 1
                self.ids.key_input.line_color_normal= 0, 1, 0, 1
                self.ids.key_input.password = True

        def EnableSetKey(self):
                self.ids.key_input.readonly=False
                self.ids.key_input.text = ""
                self.ids.key_input.text_color_normal= 0, 0.6, 0.6, 1
                self.ids.key_input.line_color_normal= 1, 1, 1, 1
                self.ids.key_input.password = False

        def ReturnEntries(self):
                first_entry = self.ids.first_entry.text
                second_entry = self.ids.second_entry.text
                try:
                        if global_variable.current_path and global_variable.KeyString:
                                if first_entry != "" and second_entry != "":
                                        #if all values is inserted
                                        first_entry_crypt = crypting.crypt_aes(first_entry)
                                        founded_row_first_entry = USB.row_filtrer_beginning(global_variable.main_filename_application, first_entry_crypt.hex())
                                        if not founded_row_first_entry:
                                                try:
                                                        #If there is no match inside the file
                                                        second_entry_crypt = crypting.crypt_aes(second_entry)
                                                        new_line_to_file = first_entry_crypt.hex() + " | " + second_entry_crypt.hex()
                                                        #Write to file
                                                        USB.update_file_compact(global_variable.main_filename_application,new_line_to_file,None)
                                                        #Reset the entries
                                                        self.ids.first_entry.text = ""
                                                        self.ids.second_entry.text = ""

                                                        #Update the box
                                                        self.RemoveAllInPasswordBox()
                                                        self.ShowPasswordList()
                                                except Exception as e: pass
                                        else:
                                                #if there is a match
                                                Show_popup(title_=Language._("form error"), text_=Language._("form error msg username"),
                                                           icon_type_="warning", width_=dp(global_variable.popup_width),
                                                           height_=dp(global_variable.popup_height), f_size=sp(24),
                                                           btn_width_=dp(0.5), btn_height_=dp(0.5)) 
                                else:
                                        #One entry is missing
                                        Show_popup(title_=Language._("form error"), text_=Language._("form error msg miss key-username"),
                                                   icon_type_="warning", width_=dp(global_variable.popup_width),
                                                   height_=dp(global_variable.popup_height), f_size=sp(24),
                                                   btn_width_=dp(0.5), btn_height_=dp(0.5))   
                        else:
                                #No current path and no key
                                if global_variable.current_path == "": #if no path
                                        Show_popup(title_=Language._("error path"), text_=Language._("error path msg"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                                   height_=dp(global_variable.popup_height),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                if global_variable.KeyString == "": #if no key
                                        Show_popup(title_=Language._("key error"), text_=Language._("key error msg"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                                   height_=dp(global_variable.popup_height), f_size=sp(30),
                                                   btn_width_=dp(0.5), btn_height_=dp(0.5)) 
                except Exception as e: pass
        #end return entries
                
        def RemoveAllInPasswordBox(self):
                self.ids.passwordlistbox.ids.container.clear_widgets()

        def GeneratePassword(self):
                try:
                        len = int(MDApp.get_running_app().lenght_gen_variable) #Take the shared variable
                        my_wished_password_array = MDApp.get_running_app().array_gen_variable #Take the second shared variable

                        import random, string
                        
                        true_values = [flag_true for flag_true, _ in enumerate(my_wished_password_array) if _] #Check index with true values
                        strings_array = [string.ascii_uppercase, string.ascii_lowercase, string.punctuation, string.digits] #Take an eye on this array
                        user_choose = [strings_array[i] for i in true_values] #Take the associated index
                        user_choose_string = "".join(user_choose) #Do one string
                        user_password = ''.join(random.choice(user_choose_string) for _ in range(len)) #Do the password
                        self.ids.second_entry.text = user_password #Set the second entry
                except Exception as e:
                        pass
     
                
#End class GUI_option_linux
                
class ReadOnlyBox(BoxLayout):
        base_scale = NumericProperty(1.0)

        def ChangeText(self, dir_path, space):
                try:
                        self.ids.id_r2.text = Language._("path") + str(dir_path)
                        self.ids.id_r3.text = Language._("info free space") + str(space[0]) + "Gb"
                        self.ids.id_r4.text = Language._("info total space") + str(space[1]) + "Gb"
                except Exception as e: pass
        def RemoveText(self):
                self.ids.id_r2.text = "Path: "
                self.ids.id_r3.text = Language._("info free space")
                self.ids.id_r4.text = Language._("info total space")
                
#End class ReadOnlyBox
class PasswordListBox(FloatLayout):  pass
#--------------------------------- SETTINGS CLASS ------------------------------------------------------------#
class SettingsScreen(Screen):
        def __init__(self, **kwargs):
                super().__init__(**kwargs)

        def CheckHash(self):
                if global_variable.current_path != "" and global_variable.KeyString != "":
                        '''
                        Here I assume that there is a key, path, hash file, backup file.
                        Problem 1: The key is a real key -> Ok, no problem. We check the main file and create a text with differences
                        Problem 2: The key is not a real key -> We check only if the file is ok
                        Problem 3: If something will change the main file -> Create a file with relative username
                        Problem 4: If the main file does not exist -> Restore from backup
                        Problem 5: If there is nothing saved on pen drive -> Show an error
                        Problem 6: If something will delete hash file or backup file -> Show an error
                        '''
                        if os.path.exists(global_variable.hash_filename_application):
                                actual_hash = USB.CountHash() #Take the hash
                                registry = USB.GetHash_registry()
                                with open(registry, "r") as f:
                                        salved_hash = f.read().strip()
                                        if actual_hash == salved_hash:
                                                Show_popup(title_=Language._("success"), text_=Language._("success msg hash"),icon_type_="warning",
                                                           width_=dp(500),height_=dp(450), f_size=sp(28),
                                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
                                        else:
                                                self.CheckFile_differences()
                        else:
                                Show_popup(title_=Language._("error"), text_=Language._("error hash"),icon_type_="warning", width_=dp(500),height_=dp(450),
                                           f_size=sp(28),btn_width_=dp(0.5), btn_height_=dp(0.5))
                else:
                        #No current path and no key
                        if global_variable.current_path == "": #if no path
                                Show_popup(title_=Language._("error path"), text_=Language._("error path msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        if global_variable.KeyString == "": #if no key
                                Show_popup(title_=Language._("key error"), text_=Language._("key error msg"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                           height_=dp(global_variable.popup_height), f_size=sp(30),
                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
        #End check hash

        def CheckFile_differences(self):
                try:
                        import difflib
                        flag1 = os.path.exists(global_variable.main_filename_application)
                        flag2 = os.path.exists(global_variable.main_filename_backup_application)
                        
                        if flag1 and flag2: #if the main file and backup exists
                                Show_popup(title_=Language._("warning"), text_=Language._("warning hash"),icon_type_="warning",width_=dp(550), height_=dp(450),
                                           f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                with open(global_variable.main_filename_application, "r", encoding="utf-8") as f1, open(global_variable.main_filename_backup_application, "r", encoding="utf-8") as f2:
                                        current_file = f1.readlines() #get the lines
                                        backup_file = f2.readlines() #get the lines

                                        diff = difflib.unified_diff(backup_file, current_file, fromfile='Backup', tofile='Current') #find the differences

                                        with open("report.txt", "w", encoding="utf-8") as f: #create a file
                                                import datetime
                                                f.write("Pendrive Password Manager File: " + str(datetime.datetime.now()) + "\n") #info
                                                f.write("Corrupted password with username:\n") #info
                                                for row in diff:
                                                        if row.startswith("-") and not row.startswith("---"):
                                                                row_ = row[1:].strip() #Delete the - from backup file
                                                                row_ = row_.split(" | ")[0] #Take the username
                                                                row_ = crypting.decrypt_aes(row_) #Decryptit
                                                                f.write(row_) #write down
                        else:
                                if not flag1: #if no main file
                                        Show_popup(title_=Language._("restore"), text_=Language._("restore msg"),icon_type_="warning", width_=dp(550),height_=dp(500),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                        import shutil
                                        from pathlib import Path
                                        path1 = Path(global_variable.current_path)
                                        #Restore from backup
                                        shutil.copy2(path1 / global_variable.main_filename_backup_application, path1 /global_variable.main_filename_application)
                                if not flag2: #no backup file
                                        Show_popup(title_=Language._("error"), text_=Language._("error hash"),icon_type_="warning", width_=dp(550),height_=dp(500),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))                                        
                                                
                except Exception as e: print(e)
        #End check hash differences

        def Backup(self, to_button, from_button):
                try:
                        if to_button and global_variable.current_path != "" and os.path.exists(global_variable.main_filename_application):
                                '''
                                I assume that you are the owner of main file
                                '''
                                import shutil
                                import platform
                                hidden_file = global_variable.main_filename_application
                                new_name = hidden_file[1:].strip() #No dot mask
                                actual_path = Path.cwd() #get working directory
                                #Go in home
                                if platform.system() == "Linux": dest_path = Path.home()
                                elif platform.system() == "Windows": dest_path = Path.home() / "Desktop"

                                shutil.copy2(actual_path / hidden_file, dest_path / new_name) #Copy the file

                                windows_set_visible_file(dest_path / new_name)  # for windows

                                Show_popup(title_=Language._("success"), text_=Language._("success backup"),icon_type_="warning", width_=dp(550),height_=dp(500),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        elif from_button and global_variable.current_path != "":
                                '''
                                I assume that you are the owner of main file
                                '''
                                import shutil
                                import platform

                                new_name = global_variable.main_filename_application
                                old_name = new_name[1:].strip()
                                dest_path = Path.cwd() #get working directory
                                
                                if platform.system() == "Linux": source_path = Path.home()
                                if platform.system() == "Windows": source_path = Path.home() / "Desktop"
                                if os.path.exists(source_path / old_name):
                                        try:
                                                windows_set_visible_file(dest_path / new_name) #for windows

                                                shutil.copy2(source_path / old_name, dest_path / new_name)

                                                windows_set_hidden_file(dest_path / new_name) #for windows
                                                #Good ending
                                                Show_popup(title_=Language._("success"), text_=Language._("success restore backup"),icon_type_="warning", width_=dp(550),height_=dp(500),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                        except Exception as e: pass
                                else:
                                        Show_popup(title_=Language._("error"), text_=Language._("no success restore backup"),icon_type_="warning", width_=dp(550),height_=dp(500),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))

                                #Clear
                                try:
                                        set_default_state_main_window(App.get_running_app()) #Empty some widgets in main screen
                                except Exception as e: print(e)
                                #end if
                        else: #no path
                                Show_popup(title_=Language._("error path"), text_=Language._("error path msg"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                           height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                except Exception as e: print(e)
        #end def Backup
        def QR(self,to_flag, from_flag):
                '''
                This function make the QR password.
                It will crypt the data respect to a fernet key!
                For now is only error correction L: invalid when the angles are painted or when more than 7% of area is painted.
                If at least one one angle is painted -> InvalidToken
                If area is under 7% or not angles, the passwords will not have problems
                L should be used only for Desktop, do not print and scan
                '''
                user_fernet_key = self.ids.qr_radio.ids.fernet_key.text

                import qrcode
                from cryptography.fernet import Fernet, InvalidToken
                from qrcode.exceptions import DataOverflowError
                
                if to_flag and global_variable.current_path != "":
                        import qrcode
                        try:
                                Window.set_system_cursor('wait')
                                
                                fernet_key = Fernet.generate_key() #Generate a fernet key
                                chiper = Fernet(fernet_key)
                                show_fernet_key_to_user = fernet_key.decode()
                                
                                with open(global_variable.main_filename_application, "r", encoding='utf-8') as f:
                                        lines = f.read()

                                text_to_hide = lines.encode()
                                crypted_text_to_hide = chiper.encrypt(text_to_hide)
                                
                                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
                                try:
                                        qr.add_data(crypted_text_to_hide)
                                        qr.make(fit=True)
                                        img = qr.make_image(fill_color="black", back_color="white")
                                        
                                        import platform
                                        if platform.system() == "Linux": dest_path = Path.home()
                                        elif platform.system() == "Windows": dest_path = Path.home() / "Desktop"
                                        
                                        img.save(dest_path / global_variable.qr_filename)

                                        with open (global_variable.qr_key_file, "w", encoding="utf-8") as f:
                                                f.write("PenDrive-Password-Manager QR fernet key: " + show_fernet_key_to_user)
                                                
                                        msg = Language._("qr fernet key value add string") + show_fernet_key_to_user
                                        Show_popup(title_=Language._("success"), text_=msg,icon_type_="warning", width_=dp(global_variable.popup_width),
                                                   height_=dp(global_variable.popup_height),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))

                                except qrcode.exceptions.DataOverflowError as e:
                                        #data too big
                                        Show_popup(title_=Language._("error"), text_=Language._("qr data too big"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                                   height_=dp(global_variable.popup_height),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                
                        except FileNotFoundError as e:
                                Show_popup(title_=Language._("error"), text_=Language._("main file not found"),icon_type_="warning", width_=p(global_variable.popup_width),
                                           height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        except Exception as e:
                                Show_popup(title_=Language._("error"), text_=Language._("error msg"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                           height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))

                        Window.set_system_cursor('arrow')
                                
                elif user_fernet_key != "" and from_flag and global_variable.current_path != "":
                        import qrcode
                        try:
                                import platform
                                from pyzbar.pyzbar import decode
                                from PIL import Image
                                Window.set_system_cursor('wait')
                                
                                if platform.system() == "Linux": from_path = Path.home()
                                elif platform.system() == "Windows": from_path = Path.home() / "Desktop"
                                else: from_path = Path.home() #Last case

                                qr_full_path = from_path / global_variable.qr_filename
                                img = Image.open(qr_full_path)
                                if img is not None:
                                        data = decode(img)
                                        if data:
                                                data = data[0].data.decode("utf-8")
                                                try:
                                                        chiper = Fernet(user_fernet_key.strip().encode())
                                                        data_bytes = chiper.decrypt(data.encode())
                                                        lines = data_bytes.decode("utf-8") #QR solved
                                        
                                                        with open(global_variable.main_filename_application, "w", encoding="utf-8") as f:
                                                                f.write(lines)

                                                        Show_popup(title_=Language._("success"), text_=Language._("success restore backup"),
                                                                   icon_type_="warning", width_=dp(global_variable.popup_width),
                                                                   height_=dp(global_variable.popup_height),
                                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                except InvalidToken:
                                                        Show_popup(title_=Language._("error"), text_=Language._("qr invalid read"),icon_type_="warning",
                                                                   width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                except ValueError as e:
                                                        Show_popup(title_=Language._("error"), text_=Language._("qr fernet wrong len"),icon_type_="warning",
                                                                   width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                except Exception as e:
                                                        Show_popup(title_=Language._("error"), text_=Language._("error msg"),icon_type_="warning",
                                                                   width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                        else:
                                                print("No Data inside QR code")
                                else:
                                        Show_popup(title_=Language._("error"), text_=Language._("qr read false"),icon_type_="warning",
                                                   width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        except FileNotFoundError as e:
                                Show_popup(title_=Language._("error"), text_=Language._("qr no file"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        except Exception as e:
                                Show_popup(title_=Language._("error"), text_=Language._("error msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))

                        Window.set_system_cursor('arrow')
                else:
                        if global_variable.current_path == "":
                                Show_popup(title_=Language._("error path"), text_=Language._("error path msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        else:
                                Show_popup(title_=Language._("error"), text_=Language._("qr no key"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                        
        #end def QR

        def RadioPress(self,widget, state):
                if widget.name == "tobackup_button":
                        Show_popup(title_="Info", text_=Language._("choose1 desktop backup info"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                   height_=dp(global_variable.popup_height),
                                   f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
                elif widget.name == "frombackup_button":
                        Show_popup(title_="Info", text_=Language._("choose2 desktop backup info"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                   height_=dp(global_variable.popup_height), f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
                elif widget.name == "fromqr_button":
                        Show_popup(title_="Info", text_=Language._("choose2 qr image info"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                   height_=dp(global_variable.popup_height), f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
                else:
                        Show_popup(title_="Info", text_=Language._("choose1 qr image info"),icon_type_="warning",
                                   width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
        #end radio press button popup
                
#End class settings screen
#--------------------------------------- for Change keys settings -----------------------------------#
class KeysListBox(BoxLayout): pass
class ChangeKey(Screen):
        def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.selected_button = None  # Tiene traccia del pulsante selezionato

        def select_voice(self, instance):
                if self.selected_button:
                        self.selected_button.background_color = global_variable.color_bg_default_selection
                        self.selected_button.color = global_variable.color_default_text_selection
                        Window.unbind(on_key_down=self.DeleteVoice)
                        
                instance.background_color = global_variable.color_bg_selection
                instance.color = global_variable.color_text_selection
                
                self.selected_button = instance
                Window.bind(on_key_down=self.DeleteVoice)

        def Insert_old(self):
                kstring = self.ids.old_key_input.text
                container = self.ids.keyslistbox.ids.container
                flag = check_duplicates(kstring,container)
                if len(kstring) == 16 and flag:
                        new_voice = Button(text=kstring, background_normal='', size_hint_y=None, height=dp(40), halign='left', valign='center', font_size='36dp')
                        new_voice.background_color = global_variable.color_bg_default_selection
                        new_voice.bind(on_release=self.select_voice)
            
                        container.add_widget(new_voice)
                        self.ids.old_key_input.text = ""
                else:
                        #Key lenght is insufficent or there is a match
                        if not flag:
                                Show_popup(title_=Language._("form error"), text_=Language._("duplicate key"),
                                           icon_type_="warning", width_=dp(popup_width),height_=dp(global_variable.popup_height), f_size=sp(24),
                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
                        elif len(kstring) != 16:
                                Show_popup(title_=Language._("key error"), text_=Language._("key len error msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(28),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
        
        def DeleteVoice(self, window, key, *args):
                if key == 8 and self.selected_button: #If backspace and selection
                        #remove the voice
                        self.ids.keyslistbox.ids.container.remove_widget(self.selected_button)
                        #Selection reset
                        self.selected_button = None
                        return True
                return False
        #end deletevoice
        
        def Insert_new(self):
                kstring = self.ids.new_key_input.text
                container = self.ids.keyslistbox.ids.container
                if global_variable.current_path != "" and len(kstring) == 16 and len(container.children): #if there is a string and keys in the box
                        #Check how many keys we have
                        n_keys = []
                        for i in range(len(container.children)):
                                n_keys.append(container.children[i].text)
                        
                        set_default_state_main_window(App.get_running_app()) #Empty some widgets in main screen
                        
                        try:
                                Window.set_system_cursor("wait")
                                import time
                                for n in n_keys:
                                        global_variable.KeyString = n
                                        #Get the list username
                                        return_values_respect_to_n_key = USB.GetList()
                                        for r in return_values_respect_to_n_key:
                                                global_variable.KeyString = n
                                                r_crypt = crypting.crypt_aes(r) #crypt the username with key n
                                                try:
                                                        row = USB.row_filtrer_beginning(global_variable.main_filename_application, r_crypt.hex() )[0] #get the row of n
                                                        
                                                        USB.update_file_compact(global_variable.main_filename_application, new_line=None, remove_line = row) #remove the row of n
                                                        #old_password = crypting.decrypt_aes(row.split(" | ")[1]) #decrypt the password
                                                        global_variable.KeyString = kstring #set the new key
                                                        new_line_ = crypting.crypt_aes(r).hex() + " | " + crypting.crypt_aes(kstring).hex() #new line in file
                                                        USB.update_file_compact(global_variable.main_filename_application, new_line = new_line_, remove_line=None) #Update the file
                                                        time.sleep(0.01)
                                                except Exception as e:
                                                        pass
                                
                                global_variable.KeyString = ""
                                self.ids.new_key_input.text = ""
                                try:
                                        self.ids.keyslistbox.ids.container.clear_widgets() #Clear the n_keys
                                except Exception as e:
                                        pass
                                Show_popup(title_=Language._("success"), text_=Language._("success change key"),
                                           icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(24),
                                           btn_width_=dp(0.5), btn_height_=dp(0.5))

                        except Exception as e:
                                Show_popup(title_=Language._("error"), text_=Language._("error msg"),
                                           icon_type_="warning", width_=dp(550), height_=dp(500),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        Window.set_system_cursor("arrow")
                else:
                        if len(kstring) != 16:
                                Show_popup(title_=Language._("key error"), text_=Language._("key len error msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(28),
                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
                        elif global_variable.current_path == "":
                                Show_popup(title_=Language._("error path"), text_=Language._("error path msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
        
#end class change key screen
#----------------------------------------------------------------------------------------------------#
#---------------------- CSV SETTINGS -------------------#
class CSV_settings(Screen):
        def __init__(self, **kwargs):
                super().__init__(**kwargs)

        def RadioPress(self,widget, state):
                label_prompt = self.ids.csv_textinput.ids.cvstextinput_label
                field_prompt = self.ids.csv_textinput.ids.csvtextinput

                if widget.name == "send_button":
                        Show_popup(title_="Info", text_=Language._("csv into desktop"),icon_type_="warning",
                                   width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        field_prompt.max_text_length = 17
                        label_prompt.text = "Inserirci MAC:"
                elif widget.name == "from_button":
                        Show_popup(title_="Info", text_=Language._("csv from desktop"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                   height_=dp(global_variable.popup_height), f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        field_prompt.max_text_length = 16
                        label_prompt.text = "Inserisci la chiave:"
                else:
                        Show_popup(title_="Info", text_=Language._("csv info msg"),icon_type_="warning", width_=dp(global_variable.popup_width),
                                   height_=dp(global_variable.popup_height), f_size=sp(28), btn_width_=dp(0.5), btn_height_=dp(0.5))
                        field_prompt.max_text_length = 16
                        label_prompt.text = "Inserisci tutte le chiavi:"
#end radio press button popup

        def InsertKey(self):
                string = self.ids.csv_textinput.ids.csvtextinput.text
                container = self.ids.csv_allkeyslistbox.ids.container_csv
                flag = check_duplicates(string,container)

                radio1 = self.ids.csv_button_radio.ids.to_button.active
                radio2 = self.ids.csv_button_radio.ids.send_button.active
                radio3 = self.ids.csv_button_radio.ids.from_button.active
                
                if len(string) == 16 and flag and (radio1 or radio3) or (len(string)==17 and flag and radio2):
                        new_voice = Button(text=string, background_normal='', size_hint_y=None, height=dp(40), halign='left', valign='center', font_size='36dp')
                        new_voice.background_color = global_variable.color_bg_default_selection
            
                        container.add_widget(new_voice)
                        self.ids.csv_textinput.ids.csvtextinput.text = ""
                else:
                        #Key lenght is insufficent or there is a match
                        if not flag:
                                Show_popup(title_=Language._("form error"), text_=Language._("duplicate key"),
                                           icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(24),
                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
                        elif (radio1 or radio3) and len(string) != 16:
                                Show_popup(title_=Language._("key error"), text_=Language._("key len error msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(28),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
                        elif (radio2) and len(string) != 17:
                                Show_popup(title_=Language._("error"), text_=Language._("csv mac format error msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(28),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))                              

        def Process_csv(self):
                radio1 = self.ids.csv_button_radio.ids.to_button.active
                radio2 = self.ids.csv_button_radio.ids.send_button.active
                radio3 = self.ids.csv_button_radio.ids.from_button.active
                text = self.ids.csv_textinput.ids.csvtextinput.text
                container = self.ids.csv_allkeyslistbox.ids.container_csv
                csv_first_row = ["Title", "URL", "Username", "Password", "Notes"]
                
                if radio1 and global_variable.current_path != "": #add keys
                        import csv
                        csv_array = []
                        if len(container.children): #if there is a string and keys in the box
                                #Check how many keys we have
                                n_keys = []
                                for i in range(len(container.children)): n_keys.append(container.children[i].text)
                                try:
                                        Window.set_system_cursor("wait")
                                        import time
                                        for n in n_keys:
                                                global_variable.KeyString = n
                                                #Get the list username
                                                return_values_respect_to_n_key = USB.GetList()
                                                for r in return_values_respect_to_n_key:
                                                        r_crypt = crypting.crypt_aes(r) #crypt the username with key n
                                                        row = USB.row_filtrer_beginning(global_variable.main_filename_application, r_crypt.hex() )[0] #get the row of n
                                                        password = crypting.decrypt_aes(row.split(" | ")[1]) #decrypt the password
                                                        csv_array.append(["","", r, password, ""]) #String for ISO CSV in password manager

                                        #Now we make a CSV file in destkop
                                        if platform.system() == "Linux": to_path = Path.home()
                                        elif platform.system() == "Windows": to_path = Path.home() / "Desktop"
                                        new_path = to_path / global_variable.csv_filename
                                        
                                        with open(new_path, mode = "w", newline = "", encoding="utf-8") as csv_file:
                                                f = csv.writer(csv_file, delimiter = ",", quoting=csv.QUOTE_MINIMAL)
                                                f.writerow(csv_first_row)
                                                f.writerows(csv_array) #Write in
                                                
                                        container.clear_widgets() #Clear the n_keys
                                        Show_popup(title_=Language._("success"), text_=Language._("csv make file"),
                                                   icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(32),
                                                   btn_width_=dp(0.5), btn_height_=dp(0.5))

                                        set_default_state_main_window(App.get_running_app()) #Empty some widgets in main screen
                                        Window.set_system_cursor("arrow")
                                except Exception as e:
                                        print(e)
                                        Show_popup(title_=Language._("error"), text_=Language._("error msg"),
                                                   icon_type_="warning", width_=dp(550), height_=dp(500),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                Window.set_system_cursor("arrow")
                        else:
                                #No len container
                                pass
                #end if radio1
                        pass
                elif radio2 and len(container.children): #Send
                        try:
                                if platform.system() == "Linux":
                                        path = Path.home()
                                        file_path = path / global_variable.csv_filename
                        
                                        if os.path.exists(file_path):
                        
                                                import subprocess
                                                target_mac =  container.children[0].text
                                                if not is_valid_mac(target_mac): return
                                        
                                                try:
                                                        result = subprocess.Popen(
                                                                ["bluetooth-sendto", f"--device={target_mac}", str(file_path)],
                                                                stdout=subprocess.DEVNULL,
                                                                stderr=subprocess.DEVNULL,
                                                                start_new_session=True
                                                        )
                                                        if result:
                                                                Show_popup(title_=Language._("success"), text_=Language._("csv send bluetooth"),
                                                                           icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(32),
                                                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                        else:
                                                                Show_popup(title_=Language._("error"), text_=Language._("csv failed bluetooth"),
                                                                           icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(32),
                                                                           btn_width_=dp(0.5), btn_height_=dp(0.5))

                                                except FileNotFoundError:
                                                        print("\nErrore: Il comando 'bluetooth-sendto' non è installato sul sistema.")
                                                
                                                except subprocess.CalledProcessError as e:
                                                        Show_popup(title_=Language._("error"), text_=Language._("csv error bluetooth"),
                                                                   icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(32),
                                                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                        #End linux
                                        else:
                                                Show_popup(title_=Language._("error"), text_=Language._("csv file missing"),
                                                           icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(32),
                                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
                                elif platform.system() == "Windows":
                                        pass
    
                                #end if radio2
                        except Exception as e:
                                print(e)
                elif radio3 and global_variable.current_path != "" and len(container.children): #Restore

                        if platform.system() == "Linux": from_path = Path.home()
                        elif platform.system() == "Windows": from_path = Path.home() / "Desktop"
                        file_path = from_path / global_variable.csv_filename
                        print(file_path)
                        if os.path.exists(file_path):
                                import csv
                                Window.set_system_cursor("wait")
                                global_variable.KeyString = container.children[0].text
                                new_list = []
                                try:
                                        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
                                                read = csv.reader(csv_file, delimiter=',', quotechar="|")
                                                head = next(read) #First line

                                                if head == csv_first_row:
                                                        for row in read:
                                                                if not row: continue
                                                                elif len(row) >= 4:
                                                                        #Debug 
                                                                        username_password = [row[2], row[3]]
                                                                        print(" | ".join(username_password))
                                                                        #---------------------------------
                                                                        username, password = row[2].strip(), row[3].strip()
                                                                        if username and password:
                                                                                username_crypted = crypting.crypt_aes(username)
                                                                                password_crypted = crypting.crypt_aes(password)
                                                                                new_list.append(username_crypted.hex() + " | " + password_crypted.hex())
                                                        #Write it down
                                                        if len(new_list):
                                                                try:
                                                                        with open(global_variable.main_filename_application, "w", encoding="utf-8") as f:
                                                                                for item in new_list:
                                                                                        f.write(f"{item}\n")

                                                                         #Only for parcondicio
                                                                        set_default_state_main_window(App.get_running_app()) #Empty some widgets in main screen
                                                                        Window.set_system_cursor("arrow")

                                                                        Show_popup(title_=Language._("success"), text_=Language._("success restore backup"),
                                                                                   icon_type_="warning", width_=dp(global_variable.popup_width),
                                                                                   height_=dp(global_variable.popup_height), f_size=sp(32),
                                                                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                                        container.clear_widgets() #Clear list box
                                                                        
                                                                except Exception as e: print(e)
                                                        else:
                                                                #no len
                                                                global_variable.KeyString = ""
                                                                set_default_state_main_window(App.get_running_app()) #Empty some widgets in main screen
                                                                Window.set_system_cursor("arrow")

                                                                Show_popup(title_=Language._("error"), text_=Language._("csv wrong strings"),
                                                                           icon_type_="warning", width_=dp(global_variable.popup_width),
                                                                           height_=dp(global_variable.popup_height), f_size=sp(32),
                                                                           btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                else:
                                                        #wrong head
                                                        global_variable.KeyString = ""
                                                        set_default_state_main_window(App.get_running_app()) #Empty some widgets in main screen
                                                        Window.set_system_cursor("arrow")

                                                        Show_popup(title_=Language._("error"), text_=Language._("csv wrong head"),
                                                                   icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(32),
                                                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
                                                        
                                except Exception as e:
                                        print(e)
                                        global_variable.KeyString = ""
                                        set_default_state_main_window(App.get_running_app()) #Empty some widgets in main screen
                                        Window.set_system_cursor("arrow")
                                        Show_popup(title_=Language._("error"), text_=Language._("error msg"),
                                                   icon_type_="warning", width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height), f_size=sp(32),
                                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
                        else:
                                #File does not exits
                                Show_popup(title_=Language._("error"), text_=Language._("csv no file"),
                                           icon_type_="warning", width_=dp(global_variable.popup_width), height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                pass
                        #end if radio3
                else:
                        #some errors
                        if global_variable.current_path == "":
                                Show_popup(title_=Language._("error path"), text_=Language._("error path msg"),icon_type_="warning",
                                           width_=dp(global_variable.popup_width),height_=dp(global_variable.popup_height),
                                           f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))

#end class csv settings
#-------------- main window -------------#
class Interface(MDApp): #Main application window

        lenght_gen_variable = "8" #Shared variable
        array_gen_variable = [True,True,True,True]
        
        def build(self, **kwargs):
                super().__init__(**kwargs)

                self.title = global_variable.title

                self.current_screen = ScreenManager() #Manager for windows

                #------------- MAIN SCREEN -----------#
                main_screen = Screen(name="main_screen")
                self.interface = BoxLayout(orientation='vertical')
                self.GUI = GUI_option_linux()
                self.menu = self.create_menu_bar()
                self.interface.add_widget(self.menu)
                self.interface.add_widget(self.GUI) #Add all GUI
                main_screen.add_widget(self.interface)
                self.current_screen.add_widget(main_screen)
                main_screen.ids["GUI"] = self.GUI #Save the GUI for later use

                #------------ SETTINGS SCREEN --------#
                self.current_screen.add_widget(SettingsScreen(name="settings"))
                self.current_screen.add_widget(ChangeKey(name="change_keys"))
                self.current_screen.add_widget(CSV_settings(name="settings_csv"))

                
                return self.current_screen
        
        def on_start(self):
                # Controlla la flag e avvia la funzione esterna
                if global_variable.flag_update:
                        # Aspetta 0.5 secondi che l'app sia visibile, poi mostra il dialogo
                        Clock.schedule_once(lambda x: Show_update_dialog(), 0.5)
                threading.Thread(target=self.CheckUSB,daemon=True).start()

        def create_menu_bar(self):
                action_bar = ActionBar(pos_hint={'top': 1}, size_hint_y=None, height='80dp') # Main bar
                action_view = ActionView() #Settings in main bar
                
                if platform.system() == "Linux": im_path = "assets/logo.png"
                elif platform.system() == "Windows": im_path = "assets/logo.ico"
                
                action_prev = ActionPrevious(title="", with_previous=False, height='80dp',
                                             app_icon_width=0, app_icon_height=0,
                                             size_hint_x=1, width=0, disabled=True,
                                             app_icon=get_resource_path(im_path))
                action_view.add_widget(action_prev)
                #Add buttons
                self.subvoice = USB.get_writable_and_not_full(10) #Return available usb path
                self.subvoice = [Path(i) for i in self.subvoice] #Define a real path
                
                if not self.subvoice:
                        btn_nopath = ActionButton(text=Language._("no path"), size_hint_x=2, font_size=sp(30), width='20dp',height='22dp', color=global_variable.color_menu_voice)
                        btn_nopath.bind(on_press=lambda x: self.USBListening())
                        action_view.add_widget(btn_nopath)
                else:
                        dropdown_menu = ActionGroup(text=Language._("path list"), mode='spinner', size_hint_x=None, width='400dp',
                                                    dropdown_width='450dp', font_size=sp(30),height='22dp',
                                                    color=global_variable.color_menu_voice)

                        for i in range(len(self.subvoice)): #Temporary group
                                item = ActionButton(text=str(self.subvoice[i]),height='22dp', size_hint_y=None, size_hint_x=None, font_size=sp(30),
                                                    width='400dp', color=global_variable.color_menu_voice)
                                item.bind(on_release=lambda instance, x=i: self.ChangePathMenu(self.subvoice[x]))
                                dropdown_menu.add_widget(item)
                        action_view.add_widget(dropdown_menu)

                btn_settings = ActionButton(text=Language._("settings name"), size_hint_x=2, font_size=sp(30), width=dp(20),height='22dp', color=global_variable.color_menu_voice)
                btn_settings.bind(on_press=lambda x: self.Go_to_settings())
                action_view.add_widget(btn_settings)
                        
                btn_help = ActionButton(text=Language._('help box'), size_hint_x=2, font_size=sp(30), width=dp(20),height='22dp', color=global_variable.color_menu_voice)
                btn_help.bind(on_press=lambda x: self.HowToUse())
                action_view.add_widget(btn_help)

                btn_about = ActionButton(text=Language._('about'), size_hint_x=2, font_size=sp(30), width=dp(20),height='22dp', color=global_variable.color_menu_voice)
                btn_about.bind(on_press=lambda x: self.About())
                action_view.add_widget(btn_about)

                action_bar.add_widget(action_view) #Add all to main bar
                return action_bar
        #end create menu

        def HowToUse(self):
                Show_popup(title_=Language._("how to use menu"), text_=Language._("how to use msg"),icon_type_="info", width_=1200,height_=650, f_size=24,
                           btn_width_=0.5, btn_height_=0.5)

        def About(self):
                if global_variable.language == "ru": height__ = 900
                else: height__ = 800
                Show_popup(title_=Language._("about"), text_=Language._("about msg"),icon_type_="account", width_=800,height_=height__, f_size=24,
                           btn_width_=0.5, btn_height_=0.3)

        def ChangePathMenu(self, subvoice_i):
                try:
                        #Change the working directory
                        os.chdir(subvoice_i)
                        global_variable.current_path = subvoice_i
                        #Change the string variable inside the USB class
                        USB.ChangePath(subvoice_i)
                        #Return the dimension memory of USB
                        space_ = USB.get_space_gb()
                        self.GUI.ids.usb_information.ChangeText(dir_path=subvoice_i, space=space_)
                        USB.PasswordListUpdate() #Update the list respecting to path-key
                        self.GUI.RemoveAllInPasswordBox() #Reset the password box
                        self.GUI.ShowPasswordList() #set new values
                        global_variable.CheckUSBFlag = True #wake up the thread
                except Exception as e:
                        pass
        #end change path menu

        def USBListening(self):
                try:
                        self.interface.clear_widgets()
                        self.GUI = GUI_option_linux()
                        self.menu = self.create_menu_bar()
                        self.interface.add_widget(self.menu)
                        self.interface.add_widget(self.GUI)
                except Exception as e: pass

        def CheckUSB(self):
                time.sleep(2) #Wait more time
                while True:
                        time.sleep(2) #Listening time
                        if global_variable.CheckUSBFlag and not os.path.exists(global_variable.current_path):
                                global_variable.CheckUSBFlag = False
                                Clock.schedule_once(self.ShowErrorUSB)
                                return

        def ShowErrorUSB(self, dt):
                try:
                        main_dir = os.path.dirname(os.path.abspath(__file__)) #Return to a good folder
                        os.chdir(main_dir)
                        Show_popup(title_=Language._("error no pendrive"), text_=Language._("no pendrive"),icon_type_="usb error", width_=dp(670),height_=dp(350), f_size=sp(36),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
                except Exception as e: pass
                Clock.schedule_once(lambda dt: self.USBListening(), 5) #Wait 5 seconds and then re-open

        def Back_to_mainscreen(self, *args):
                self.current_screen.current = "main_screen" #go to main screen
                self.current_screen.transition.direction = "right" #show direction
                
        def Go_to_settings(self, *args):
                self.current_screen.current = "settings"
                self.current_screen.transition.direction = "left"
        def Back_to_settings(self, *args):
                self.current_screen.current = "settings"
                self.current_screen.transition.direction = "right"

        def Go_to_Changekeys(self, *args):
                self.current_screen.current = "change_keys"
                self.current_screen.transition.direction = "left"

        def Go_to_CSV(self, *args):
                self.current_screen.current = "settings_csv"
                self.current_screen.transition.direction = "left"

#End class interface


def main():

        from screeninfo import get_monitors
        monitor = get_monitors()[0] #Get information regarding the monitor

        if ((monitor.width >= dp(800)) and (monitor.height >= dp(600))): #Check min dimensions
                Window.size = (monitor.width * 0.37, monitor.height * 0.45)
                Interface().run() #Create the interface
                sys.exit() #Stop

        else: pass

if __name__ == "__main__":
        main()
