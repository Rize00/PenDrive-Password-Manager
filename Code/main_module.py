# -*- coding: utf-8 -*-
'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Version: 0.1
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is the main interface module. Here, there are classes (Interface, Language) and two functions (Get_language, main). 
'''
#-------------------------------------------    Python modules    -------------------------------------#
import platform
import os
import getpass
from pathlib import Path
import sys
import threading
import time

from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand') #Disable multitouch
Config.set('kivy', 'window_icon', ' ') #No icon

from kivy.app import App
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton, ActionGroup
from kivy.uix.popup import Popup
import kivy.utils as utils
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp, sp
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
                if not lang:
                        return "en"
                lang_lower = lang.split('_')[0].lower()

                available = ["en", "it", "fr", "ru"]

                return lang_lower if lang_lower in available else "en"

        except Exception as e:
                print(e)
                return "en"  # Fallback

#Set default language in this application
global_variable.language = Get_os_language()

from utility_class import Language, get_resource_path
USB = USBRecursiveScanner() #Instanziate the class
#--------------------------------------------------------------------------------------------------#
try:
    Builder.load_file(get_resource_path('GUI_option_linux.kv')) #Load GUI file
except Exception as e:
    print(f"\nERROR FILE KV: \n{e}\n")

class GUI_option_linux(FloatLayout):
        def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.selection = None
        
        def SetKey(self): #SetKey button Command
                key = self.ids.key_input.text
                if len(key) == 16 and self.ids.key_input.readonly==False:
                        self.DisableSetKey()
                        self.ids.key_input.password = True
                        global_variable.KeyString = key #Set the global variable
                        #Remove the voice inside the list box
                        voices = self.ids.passwordlistbox.ids.container
                        voices.clear_widgets()
                        #Update the list box of password
                        self.ShowPasswordList()
                        
                elif self.ids.key_input.readonly==True: #if the input box is disabled
                        self.EnableSetKey()
                        global_variable.KeyString = ""
                        self.ids.key_input.password = False
                        if self.selection: #Show selection
                                self.selection.background_color = global_variable.color_bg_default_selection
                                self.selection.color = global_variable.color_default_text_selection
                                self.selection = None
                        #Append to clipboard
                        from kivy.core.clipboard import Clipboard
                        Clipboard.copy(" ")
                else:
                        #Show some errors
                        Show_popup(title_=Language._("key error"), text_=Language._("key len error msg"),icon_type_="warning", width_=dp(400),height_=dp(400), f_size=sp(28),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))
        def ShowPasswordList(self):
                try:
                        aviable_list = USB.PasswordListUpdate() #Take the list
                        if aviable_list: #if there is something
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
                else:
                        #Append to clipboard the empty string
                        from kivy.core.clipboard import Clipboard
                        Clipboard.copy(" ")
                        Show_popup(title_=Language._("key error"), text_=Language._("key set msg"),icon_type_="warning", width_=dp(400),height_=dp(400), f_size=sp(24),
                                   btn_width_=dp(0.5), btn_height_=dp(0.5))

        def DeleteVoice(self, window, key, *args):
                if key == 8 and self.selection: #If backspace and selection
                        #remove the voice
                        self.ids.passwordlistbox.ids.container.remove_widget(self.selection)
                        #Selection reset
                        self.selezionato = None
                        USB.RemoveLine(self.selection.text) #Remove the username
                        self.RemoveAllInPasswordBox() #Clear list
                        self.ShowPasswordList() #Update the list
                        return True
                return False
                
        def DisableSetKey(self):
                self.ids.key_input.readonly=True
                self.ids.key_input.text_color_normal= 0, 1, 0, 1
                self.ids.key_input.line_color_normal= 0, 1, 0, 1

        def EnableSetKey(self):
                self.ids.key_input.readonly=False
                self.ids.key_input.text = ""
                self.ids.key_input.text_color_normal= 0, 0.6, 0.6, 1
                self.ids.key_input.line_color_normal= 1, 1, 1, 1

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
                                                           icon_type_="warning", width_=dp(400),height_=dp(400), f_size=sp(24),
                                                           btn_width_=dp(0.5), btn_height_=dp(0.5)) 
                                else:
                                        #One entry is missing
                                        Show_popup(title_=Language._("form error"), text_=Language._("form error msg miss key-username"),
                                                   icon_type_="warning", width_=dp(400),height_=dp(400), f_size=sp(24),
                                                   btn_width_=dp(0.5), btn_height_=dp(0.5))   
                        else:
                                #No current path and no key
                                if global_variable.current_path == "": #if no path
                                        Show_popup(title_=Language._("error path"), text_=Language._("error path msg"),icon_type_="warning", width_=dp(400),height_=dp(400),
                                                   f_size=sp(30), btn_width_=dp(0.5), btn_height_=dp(0.5))
                                if global_variable.KeyString == "": #if no key
                                        Show_popup(title_=Language._("key error"), text_=Language._("key error msg"),icon_type_="warning", width_=dp(400),height_=dp(400), f_size=sp(30),
                                                   btn_width_=dp(0.5), btn_height_=dp(0.5)) 
                except Exception as e: pass
                
        def RemoveAllInPasswordBox(self):
                self.ids.passwordlistbox.ids.container.clear_widgets()
                
class PasswordListBox(FloatLayout):  pass
class ReadOnlyBox(BoxLayout):
        base_scale = NumericProperty(1.0)

        def ChangeText(self, dir_path, space):
                try:
                        self.ids.id_r2.text = "Path: " + str(dir_path)
                        self.ids.id_r3.text = Language._("info free space") + str(space[0]) + "Gb"
                        self.ids.id_r4.text = Language._("info total space") + str(space[1]) + "Gb"
                except Exception as e: pass
        def RemoveText(self):
                self.ids.id_r2.text = "Path: "
                self.ids.id_r3.text = Language._("info free space")
                self.ids.id_r4.text = Language._("info total space")
                
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

def Show_popup(title_, text_, icon_type_="info", hex_bg="#ffffff",width_=400, height_=250, f_size=14, btn_width_=0, btn_height_=0):
    content = CustomPopup(message_text=text_, icon_type=icon_type_, bg_hex=hex_bg, custom_font_size=f"{f_size}sp", btn_width = dp(btn_width_), btn_height=dp(btn_height_))
    
    pop = Popup(title=title_, content=content, size_hint=(None, None), size=(dp(width_), dp(height_)), auto_dismiss=False if icon_type_ == "error usb" else True)
    
    content.popup_instance = pop
    pop.open()

class Interface(MDApp): #Main application window
        def build(self, **kwargs):
                super().__init__(**kwargs)
        
                #Window configuration
                Window.clearcolor = get_color_from_hex("#848884")
                self.title = global_variable.title

                interface = BoxLayout(orientation='vertical')

                self.GUI = GUI_option_linux()
                menu = self.create_menu_bar()
                interface.add_widget(menu)
                interface.add_widget(self.GUI) #Add all GUI

                return interface
        
        def on_start(self):
                threading.Thread(target=self.CheckUSB,daemon=True).start()

        def create_menu_bar(self):
                action_bar = ActionBar(pos_hint={'top': 1}, size_hint_y=None, height='80dp') # Main bar
                action_view = ActionView() #Settings in main bar
                action_prev = ActionPrevious(title="", with_previous=False, height='80dp',
                                             app_icon_width=0, app_icon_height=0,
                                             size_hint_x=1, width=0, disabled=True)
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
                        
                btn_help = ActionButton(text=Language._('help box'), size_hint_x=2, font_size=sp(30), width=dp(20),height='22dp', color=global_variable.color_menu_voice)
                btn_help.bind(on_press=lambda x: self.HowToUse())
                action_view.add_widget(btn_help)

                btn_about = ActionButton(text=Language._('about'), size_hint_x=2, font_size=sp(30), width=dp(20),height='22dp', color=global_variable.color_menu_voice)
                btn_about.bind(on_press=lambda x: self.About())
                action_view.add_widget(btn_about)

                btn_donation = ActionButton(text=Language._('donation'), size_hint_x=2, font_size=sp(30), width=dp(20),height='22dp', color=global_variable.color_menu_voice)
                btn_donation.bind(on_press=lambda x: self.Donation())
                action_view.add_widget(btn_donation)

                action_bar.add_widget(action_view) #Add all to main bar
                return action_bar

        def HowToUse(self):
                Show_popup(title_=Language._("how to use menu"), text_=Language._("how to use msg"),icon_type_="info", width_=1200,height_=650, f_size=24,
                           btn_width_=0.5, btn_height_=0.5)
                
        def Donation(self):
                Show_popup(title_=Language._("donation box"), text_=Language._("donation box msg"),icon_type_="donation", width_=800,height_=650, f_size=24,
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
                        self.GUI.ShowPasswordList()
                        global_variable.CheckUSBFlag = True #wake up the thread
                except Exception as e:
                        pass

        def USBListening(self):
                os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

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

def main():

        from screeninfo import get_monitors
        monitor = get_monitors()[0] #Get information regarding the monitor

        if ((monitor.width >= dp(800)) and (monitor.height >= dp(600))): #Check min dimensions
                Window.size = (dp(1200), dp(900))
                Interface().run() #Create the interface
                sys.exit() #Stop

        else:
                #If the dimension of monitor is not correct
                flag = tk.messagebox.showerror(title=Language._("window size error"), message = Language._("window size error msg"))
                if (flag): exit()

if __name__ == "__main__":
        main()
