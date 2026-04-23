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
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image,ImageTk
import customtkinter as ctk
from sys import platform
import os
import getpass
from pathlib import Path
import sys
import threading
import time
#---------------------------- Application modules ------------------------#
import interruttori
import global_variable
from pen_drive import USBRecursiveScanner

def Get_linux_language():
        #This function will return the language of OS.
        #For now, is only english and italian
        import locale
        
        lang, _ = locale.getlocale()
        if not lang: return "en" #Fallback

        l = lang.split('_')[0].lower()
        available = ["eng", "it"]
        
        if l in available: return l
        else: return "en"

#Set default language in this application
global_variable.language = Get_linux_language()

def get_resource_path(relative_path):
    """ Ottiene il percorso assoluto della risorsa (funziona sia in dev che in exe) """
    if hasattr(sys, '_MEIPASS'):
        # Se siamo dentro l'eseguibile, punta alla cartella temporanea
        return os.path.join(sys._MEIPASS, relative_path)
    # Se siamo in fase di sviluppo, usa il percorso normale
    return os.path.join(os.path.abspath("."), relative_path)

class Language():
        '''This class works with json file. It's main purpose is to translate string for the user '''
        def __init__(self):
                import json #For language translation
                path = get_resource_path('translation.json')
                with open(path, 'r', encoding='utf-8') as f:
                        global_variable.data_language = json.load(f)
        def _(key):
                try:
                        return global_variable.data_language[global_variable.language].get(key, key)
                except Exception as e:
                        pass
                        
        def Load_language(x): global_variable.language = x
#End class Language

Language() #Instanziate the class
USB = USBRecursiveScanner() #Instanziate the class

#Now we check the OS for add GUI configuration
if platform == "linux" or platform == "linux2": import GUI_option_linux as GUI_option
else:
        from tkinter import messagebox
        flag = tk.messagebox.showerror(title=Language._("error platform"), message = Language._("error platform msg"))
        if (flag): exit()
#--------------------------------------------------------------------------------------------------#

class Interface(ctk.CTk): #Main application window

        def __init__ (self):

                super().__init__(className=global_variable.title)
                self.title("PenDrive Password Manager")
                self.geometry(str(1200)+"x"+str(900)) #Dimension of window
                self.configure(fg_color="#848884") #Background color

                try:
                        icon = resource_path("logo.png")
                        img = Image.open(icon)
                        photo = ImageTk.PhotoImage(img)
                        self.iconphoto(False, photo)
                except Exception as e:
                        pass

                gui_option_array = [GUI_option.PasswordList(), GUI_option.InsertBox(), GUI_option.KeyConfigBox()]
                workflow = [{"init obj" : GUI_option, "method1" : "PasswordList", "method12" :  "Get_Option",
                             "second_function" : interruttori.PasswordList},
                            {"init obj" : GUI_option, "method1" : "InsertBox", "method12" :  "Get_Option",
                             "second_function" : interruttori.Insert_box_text},
                            {"init obj" : GUI_option, "method1" : "KeyConfigBox", "method12" :  "Get_Option",
                             "second_function" : interruttori.KeyConfig_box}]
                box_list = []
                
                for step in workflow:
                        x = getattr(step['init obj'], step['method1'])()
                        y = getattr(x, step['method12'])()
                        box_list.append(step['second_function'](self,*y))

                button_option = GUI_option.Button()
                temp_option = button_option.Get_Option_insert()
                insert_button = interruttori.button_3(self,temp_option[0],temp_option[1], temp_option[2], temp_option[3], temp_option[4], temp_option[5],
                                                    temp_option[6], temp_option[7], temp_option[8], temp_option[9])
                
                temp_option = button_option.Get_Option_setKey()
                setKey_button = interruttori.button_2(self,temp_option[0],temp_option[1], temp_option[2], temp_option[3], temp_option[4], temp_option[5],
                                                    temp_option[6], temp_option[7], temp_option[8], temp_option[9])

                usb_information = interruttori.Information_usb_port_on_screen(self,width_canvas = 380, height_canvas = 258, x_canvas = 690, y_canvas = 500,
                                                                              x_text = 120, y_text=10, font_=("Arial",12),
                                                                              txt_width = 200, outline_rect_color = "#708090",
                                                                              rect_x = 2, rect_y = 2, rect_x1 = 378, rect_y1 = 256, border_width=10)
                usb_information.Update(dir_path="", space=[])
                insert_button.attach(box_list[1])
                insert_button.attach(USB)
                
                setKey_button.attach(box_list[2])
                setKey_button.attach(USB)
                setKey_button.attach(box_list[0])

                box_list[0].attach(USB) #Password list

                USB.attach(box_list[0])
                #------------------------------------------ MENU BAR ----------------------------------------------#
                self.Menubar(usb_information)
                #--------------------------------------------------------------------------------------------------#

        def Menubar(self,usb_information):
                #This function will create the Menu bar at the top of the application window
                #Accept only a obj class: usb_information
                if type(usb_information).__name__ != "Information_usb_port_on_screen":
                        return

                from CTkMenuBar import CTkMenuBar
                menu_ = CTkMenuBar(master = self)
                #Create the Dropdown menu
                path = Path("/media/" + getpass.getuser())
                subvoice = USB.get_writable_and_not_full(10) #Return available usb path
                subvoice = [Path(i) for i in subvoice] #Define a real path

                if len(subvoice) == 0:
                        #If there is no path, show the message
                        menu_option = menu_.add_cascade(Language._("no pendrive"), fg_color="black", text_color="gold", command=lambda: self.USBListening())
                else:
                        #Add a generic path
                        menu_option = menu_.add_cascade(path, fg_color="black", text_color="gold")
                        #Add some functions to the subvoices with parameters (paths, obj)
                        command_function = [lambda i=i: self.ChangePathMenu(i, usb_information) for i in subvoice]
                        #Create the dropdown
                        dropdown1 = CustomDropdownMenu(widget=menu_option, fg_color="black", text_color="gold")
                        self.Make_cascade_menu(dropdown1, subvoice, command_function)
                        global_variable.CheckUSBFlag = True

                #How to use voice
                menu_option_howtouse = menu_.add_cascade(Language._("how to use menu"), command=lambda: self.HowToUse(), fg_color="black", text_color="gold")
                menu_option_about = menu_.add_cascade(Language._("about"), command=lambda: self.About(), fg_color="black", text_color="gold")
                #Donation link voice
                menu_option_donation = menu_.add_cascade(Language._("donation"), command=lambda: self.Donation(), fg_color="black", text_color="gold")

        def Make_cascade_menu(self,menu_name, label_name, command_function):
                '''This function will only create the dropdown voices '''
                for i in range (0,len(label_name)):
                        menu_name.add_option(option=label_name[i],command=command_function[i])

        def HowToUse(self):
                GUI_option.Popup(self, title_=Language._("how to use menu"), text_=Language._("how to use msg"), 
                       bg_color="#f0f0f0", text_color="#000000", 
                       font_family="Helvetica", font_size=11, 
                       pos_x_window=None, pos_y_window=None, icon_im=None,
                       x_text_pos=50, y_text_pos=50, width=1300, height=510,
                       x_button_position = 550, y_button_position=420,
                       x_icon = 0, y_icon = 0)
                
        def Donation(self):
                GUI_option.Popup(self, title_=Language._("donation box"), text_=Language._("donation box msg"), 
                       bg_color="#f0f0f0", text_color="#000000", 
                       font_family="Helvetica", font_size=11, 
                       pos_x_window=None, pos_y_window=None, icon_im="donation",
                       x_text_pos=10, y_text_pos=100, width=800, height=550,
                       x_button_position = 300, y_button_position=460,
                       x_icon = 420, y_icon=30)

        def About(self):
                GUI_option.Popup(self, title_=Language._("about box"), text_=Language._("about box msg"), 
                       bg_color="#f0f0f0", text_color="#000000", 
                       font_family="Helvetica", font_size=11, 
                       pos_x_window=None, pos_y_window=None, icon_im="info",
                       x_text_pos=50, y_text_pos=100, width=800, height=800,
                       x_button_position = 300, y_button_position=700,
                       x_icon = 450, y_icon=30)

        def ChangePathMenu(self, subvoice_i, usb_information):
                #Change the working directory
                os.chdir(subvoice_i)
                #Change the string variable insiede the USB class
                USB.ChangePath(subvoice_i)
                #Return the dimension memory of USB
                space_ = USB.get_space_gb()
                usb_information.Update(dir_path=subvoice_i, space=space_)
                USB.PasswordListUpdate() #Update the list respecting to path-key

        def USBListening(self):
                os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

#END INTERFACE CLASS
def CheckUSB(Interface):
        time.sleep(2)
        while True:
                time.sleep(2)
                if global_variable.CheckUSBFlag:
                        x = USB.get_writable_and_not_full(10)
                        if not x:
                                global_variable.CheckUSBFlag = False
                                GUI_option.Popup(Interface, title_=Language._("error no pendrive"), text_=Language._("no pendrive"), 
                                                 bg_color="#f0f0f0", text_color="#000000", 
                                                 font_family="Helvetica", font_size=11, 
                                                 pos_x_window=-20, pos_y_window=None, icon_im="error usb",
                                                 x_text_pos=100, y_text_pos=100, width=500, height=300,
                                                 x_button_position = 135, y_button_position=165,
                                                 x_icon = 290, y_icon=10)
def main():

        from screeninfo import get_monitors
        monitor = get_monitors()[0] #Get information regarding the monitor

        if ((monitor.width >= 800) and (monitor.height >= 600)): #Check min dimensions

                app = Interface() #Create the interface
                t = threading.Thread(target=CheckUSB, args=(app,), daemon=True)
                t.start()
                app.mainloop() #Start
                sys.exit() #Stop

        else:
                #If the dimension of monitor is not correct
                flag = tk.messagebox.showerror(title=Language._("window size error"), message = Language._("window size error msg"))
                if (flag): exit()

if __name__ == "__main__":
        main()
