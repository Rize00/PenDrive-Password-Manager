'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Version: 0.1
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is about buttons, entry, list box and information box behavior. 
'''
#----------------- Python modules ----------------#
import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext
import string
import base64
import time
import zlib
from sys import platform
#------------- Application modules ------------#
import global_variable
from main_module import Language
import crypting

if platform == "linux" or platform == "linux2":
        import GUI_option_linux as GUI_option


def Alphabet_1(s):
        #This function is used only for checking the alphabet in key text box and in the entry boxes
        #It accept only one argument: string

        #Define the available array
        array = list(string.ascii_letters + string.digits + string.punctuation)
        #Check the argument of the function
        if s in array: return True
        else: return False
#End Alphabet_1

class PasswordList():
        '''This class rappresent the PassowrdList box '''
        def __init__(self,Interface, width_canvas, height_canvas, x_canvas, y_canvas,
                     string_text = " ", txt_width = 0, list_box_width = 60, list_box_height = 5,
                     x_text_position = 0, y_text_position = 0, x_listbox = 0,y_listbox = 0, font_text = "Arial",
                     font_size = 8, text_style = "bold"):
                self.observer = []
                #Observer 0: USB
                
                self.window = Interface #Save the ctk parent
                #----------- CANVAS --------------#
                self.canvas = tk.Canvas(Interface,width=width_canvas, height=height_canvas, bg=global_variable.color_canvas, highlightthickness=0)
                self.canvas.place(x = x_canvas, y = y_canvas)
                #---------- TEXT for give a name to the list box ----------#
                self.text = self.canvas.create_text(x_text_position ,y_text_position,
                                                    text = string_text, width = txt_width, fill=global_variable.color_text_info, font=(font_text, font_size, text_style)) 
                #---------- LIST BOX -------#
                self.frame = tk.Frame(Interface)
                self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL) #Add the scrollbar for the listbox
                self.listbox = tk.Listbox(self.frame, yscrollcommand=self.scrollbar.set, selectmode=tk.SINGLE, width=30, height=17)

                # scrollbar configuration
                self.scrollbar.config(command=self.listbox.yview)
                self.listbox.place(x=10, y=10)
                self.frame.place(x=x_listbox, y=y_listbox, width = 475, height = 670)

                #Binding events for the listbox
                self.listbox.bind('<Control-c>', self.CopyToClipBoard)
                self.listbox.bind('<BackSpace>', self.Clear)

        def WriteIn(self, file_list):
                '''This function will add some strings to the list box.
                   Accept only one argument: list'''
                if isinstance(file_list, list):
                        try:
                                for l in file_list:
                                        self.listbox.insert(tk.END, l)
                        except Exception as e:
                                pass

        def CopyToClipBoard(self,event):
                '''This function is an event function. If the user wants to copy the password.
                CTRL+C -> copy'''
                w = event.widget
                try:
                        index = int(w.curselection()[0]) #Select the voice
                        value = w.get(index) #Return the values

                        if "| " in value and (global_variable.KeyString != ""):
                                value = value.split("| ")[1] #Take the password
                                value = crypting.decrypt_aes(value) #Decrypt
                                
                                self.window.clipboard_clear() #Clear the clipboard
                                self.window.clipboard_append(value) #Append for CTRL+V
                                time.sleep(global_variable.time_sleep_append_copy) #A time is needed otherwise will not copy.
                                
                                return "break"
                        else:
                                #If there is no key or there is some string problem, show an error
                                GUI_option.Popup(self.window,title_=Language._("key error"), text_=Language._("key set msg"),
                                      width=600, height=350, pos_x_window=None, pos_y_window=None, x_text_pos=50, y_text_pos=100,
                                      bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12, x_button_position = 200, y_button_position=250,
                                      icon_im="warning", x_icon=330, y_icon=20)
                except Exception as e:
                        pass

        def Clear(self,event):
                '''This function is an event function. If the user wants to remove a voice'''
                w = event.widget
                selection = w.curselection() #If some selection
                if selection:
                        index = selection[0]
                        value = w.get(index)
                        value_username = value.split('|')[0].strip() #get the username/email and strip some char
                        self.observer[0].RemoveLine(value_username)
                        self.observer[0].PasswordListUpdate() #Update the list

        def ClearFor_Replace(self):
                '''This function is called in Password Thread '''
                self.listbox.delete(0, 'end')

        def attach(self,observer):
                if observer not in self.observer:
                        self.observer.append(observer)
                else: pass
        def detach(self, observer):
                try:
                        self.observer.remove(observer)
                except ValueError: pass

#End class PasswordList

class Insert_box_text():
        '''This class is for the entry boxed username-password '''
        def __init__(self,Interface, width_canvas, height_canvas, x_canvas, y_canvas,
                     string_text = " ", txt_width = 0, entry_width = 0, entry_height = 0,
                     x_text_position = 0, y_text_position = 0, shift_xbox_from_text = 0, shift_ybox_from_text = 0):
                
                #----------- CANVAS --------------#
                self.canvas = tk.Canvas(Interface,width=width_canvas, height=height_canvas, bg=global_variable.color_canvas, highlightthickness=0)
                self.canvas.place(x = x_canvas, y = y_canvas)
                #---------- TEXT BOX USERNAME EMAIL ----------#
                self.text = self.canvas.create_text(x_text_position , y_text_position, text = string_text, width = txt_width, fill=global_variable.color_text_info)

                check_alphabet = (Interface.register(Alphabet_1), '%S') #Check alphabet inside
     
                #---------- ENTRY BOX USERNAME EMAIL -------#
                self.user_input_UE = tk.StringVar()
                self.canvas.entry_UE = tk.Entry(Interface, width=entry_width, textvariable=self.user_input_UE)   
                self.canvas.entry_UE.place(x = x_canvas + shift_xbox_from_text, y= y_canvas+ shift_ybox_from_text)
                self.canvas.entry_UE.config(validate='key', vcmd=check_alphabet)

                #--------- ENTRY PASSWORD TEXT ----------#
                x_text = x_text_position - 5
                y_text = y_text_position
                y_password_canvas = y_canvas + shift_ybox_from_text + 60
                
                self.canvas1 = tk.Canvas(Interface,width=width_canvas, height=height_canvas, bg=global_variable.color_canvas, highlightthickness=0)
                self.canvas1.place(x = x_canvas, y = y_password_canvas)
                self.text_password = self.canvas1.create_text(x_text , y_text,text = "Password", width = txt_width, fill=global_variable.color_text_info)
                
                #---------- ENTRY BOX Password-------
                x_password_entry = x_canvas + shift_xbox_from_text
                
                self.user_input_password = tk.StringVar()
                self.canvas1.entry_password = tk.Entry(Interface, width=entry_width, textvariable=self.user_input_password)   
                self.canvas1.entry_password.place(x = x_password_entry, y= y_password_canvas + 30)
                self.canvas1.entry_password.config(validate='key', vcmd=check_alphabet)

                #Binding
                self.canvas.entry_UE.bind("<KeyRelease>", lambda event: self.CheckLen(event), add="+")
                self.canvas1.entry_password.bind("<KeyRelease>", lambda event: self.CheckLen(event), add="+")

                self.window = Interface

        def Get_text(self):
                '''This is a getter function. It will return only the input inside the text boxes'''
                if global_variable.KeyString != "": #the key string is necessary!
                        if len(self.canvas.entry_UE.get()) >= 1 and len(self.canvas1.entry_password.get()) >= 1:
                                input = [self.canvas.entry_UE.get(), self.canvas1.entry_password.get()]
                                return input
                        else: return []
                else:
                        GUI_option.Popup(self.window,title_=Language._("key error"), text_=Language._("key error msg"),
                                         width=600, height=350, pos_x_window=None, pos_y_window=None, x_text_pos=20, y_text_pos=130,
                                         bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12,
                                         x_button_position = 180, y_button_position=220,
                                         icon_im="warning", x_icon=290, y_icon=10)
                

        def Clear(self):
                '''This function accept no arguments. Clear function will clear the entry boxes'''
                self.user_input_UE.set("")
                self.user_input_password.set("")

        def CheckLen(self,event):
                '''This function is an event function. If the user uses too much char'''
                length_value = event.widget.get()
                if len(length_value) > 30:
                        event.widget.delete(30,'end') #Update the text

#End class Insert box text

class KeyConfig_box():
        def __init__(self,Interface, width_canvas, height_canvas, x_canvas, y_canvas,
                     string_text = " ", txt_width = 0, x_text_position=0, y_text_position=0, entry_width=0, entry_height=0, font_=()):
                
                self.canvas_key = tk.Canvas(Interface,width=width_canvas, height=height_canvas, bg=global_variable.color_canvas, highlightthickness=0)
                self.canvas_key.place(x = x_canvas, y = y_canvas)
                #---------- TEXT ----------#
                x_text = x_text_position
                y_text = y_text_position
                self.text = self.canvas_key.create_text(x_text ,y_text,text = string_text, width = txt_width, fill=global_variable.color_text_info, font=font_)

                check_alphabet = (Interface.register(Alphabet_1), '%S') #Check the alphabet

                #------ Key entry -------#
                self.key_input = tk.StringVar()
                self.canvas_key.entry_key = tk.Entry(Interface, width=entry_width, textvariable=self.key_input)
                self.canvas_key.entry_key.place(x = x_canvas + 80, y= y_canvas - 5)
                self.canvas_key.entry_key.config(validate='key', vcmd=check_alphabet)

                #Binding
                self.canvas_key.entry_key.bind("<KeyRelease>", lambda event: self.CheckLen(event), add="+")

        def CheckLen(self,event):
                '''This function is an event function. If the user uses too much char'''
                length_value = event.widget.get()
                if len(length_value) > 16:
                        event.widget.delete(16,'end') #Update the string

        def Get_text(self):
                '''Tiis function is a getter function. It will return the key string '''
                return self.canvas_key.entry_key.get()

        def Clear(self):
                '''Set the key input to empty string '''
                self.key_input.set("")

        def SetStatus(self,new_state):
                '''This function will change the config state of key entry '''
                if new_state == "normal" or new_state == "disabled":
                        self.canvas_key.entry_key.config(state=new_state)

        def GetStatus(self):
                ''' This function will return the key entry state '''
                return self.canvas_key.entry_key["state"]
        
#end class key config

class button_factory():
        '''This is a factory class for buttons in the gui'''
        
        def __init__(self,Interface, x_position = 0, y_position = 0, width_button = 0, height_button = 0, font_style = None):
                self.observer = [] #List of observer
                #--------------- Sviluppo del notify observer -----------------
        def attach(self,observer):
                if observer not in self.observer:
                        self.observer.append(observer)
                else: pass
        def detach(self, observer):
                try:
                        self.observer.remove(observer)
                except ValueError: pass

        def notify(self):
                pass

        def info(self):
                name = self.button._text
                
#End button factory

class button_2(button_factory): #set key input Button
        def __init__(self,Interface, x_position = 0, y_position = 0, width_button = 0, height_button = 0, font_style = None,
                     fg_color_ = None, text_color_ = None, border_color_ = None, border_width_ = None, corner_radius_ = None):
                '''
                This function will create the key input button.
                Observer 0: KeyBox
                Observer 1: USB
                Observer 2: PasswordList
                '''
                self.observer = [] #List of observer
                self.window = Interface
                
                
                #-------- GUI ---------#
                self.button = ctk.CTkButton(Interface,text="Set Key", height=height_button,
                                                width=width_button,command=self.notify, font = font_style,
                                                fg_color = fg_color_ , text_color = text_color_ ,
                                                border_color= border_color_, border_width=border_width_,
                                                corner_radius = corner_radius_)
                self.button.place(x=x_position,y=y_position)

        def notify(self):
                '''This function is only called when the button is clicked '''
                self.info()
                if self.observer[0].GetStatus() == "normal": #check key entry state 
                        string = self.observer[0].Get_text() #Retrieve the text
                        if len(string) == 16:
                                self.observer[0].SetStatus("disabled") #Set the new state is the length is correct
                                global_variable.KeyString = string #Assign the value to the global variable
                                #Call the password file
                                self.observer[1].PasswordListUpdate()
                        else:
                                if global_variable.current_path == "":
                                        GUI_option.Popup(self.window,title_=Language._("error path"), text_=Language._("error path msg"),
                                                         width=600, height=350, pos_x_window=None, pos_y_window=None, x_text_pos=20, y_text_pos=130,
                                                         bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12,
                                                         x_button_position = 180, y_button_position=230,
                                                         icon_im="warning", x_icon=290, y_icon=10)
                                else:
                                        GUI_option.Popup(self.window,title_=Language._("key error"), text_=Language._("ley len error msg"),
                                                         width=600, height=350, pos_x_window=None, pos_y_window=None, x_text_pos=20, y_text_pos=130,
                                                         bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12,
                                                         x_button_position = 180, y_button_position=230,
                                                         icon_im="warning", x_icon=290, y_icon=10)
                                        global_variable.KeyString = "" #Fallback
                else:
                        self.observer[0].SetStatus("normal") #If the entry box is disabled, change it
                        self.observer[0].Clear() #Clear the entry box
                        self.observer[2].ClearFor_Replace() #Clear the list
                        global_variable.KeyString = "" #Set the global variable to empty string
                        
#End class button2

class button_3(button_factory): #insert Button
        '''
        This function will create the insert button.
        Observer 0: InsertTextBox
        Observer 1: USB
        '''
        def __init__(self,Interface, x_position = 0, y_position = 0, width_button = 0, height_button = 0, font_style = None,
                     fg_color_ = None, text_color_ = None, border_color_ = None, border_width_ = None, corner_radius_ = None):

                self.observer = []
                self.window = Interface

                #--------- GUI ----------#
                self.button = ctk.CTkButton(Interface,text="Insert", height=height_button,
                                                width=width_button,command=self.notify, font = font_style,
                                                fg_color = fg_color_ , text_color = text_color_ ,
                                                border_color= border_color_, border_width=border_width_,
                                                corner_radius = corner_radius_)
                self.button.place(x=x_position,y=y_position)

        def notify(self):
                '''This function is only called when the button is clicked '''
                self.info()
                
                form_UEP_values = self.observer[0].Get_text() #Get the form values
                try:
                        if global_variable.current_path and global_variable.KeyString: #Check if variables are set
                                if form_UEP_values: #Check if not empty form
                                        first_entry = crypting.crypt_aes(form_UEP_values[0]) #Crypt the first entry and check the file
                                        founded_row_corresponding_to_crypted_key = self.observer[1].row_filtrer_beginning(global_variable.main_filename_application, first_entry.hex())
                                        if not founded_row_corresponding_to_crypted_key: #if there is not a row like this
                                                try:
                                                        y = crypting.crypt_aes(form_UEP_values[1]) #crypt the password
                                                        #SAVE THE STRING CRYPTED NAME + CRYPTED PASSWORD
                                                        new_line_to_file = first_entry.hex() + " | " + y.hex()
                                                        #Write in the file
                                                        self.observer[1].update_file_compact(global_variable.main_filename_application,new_line_to_file,None)
                                                        #Clear the entry boxes
                                                        self.observer[0].Clear()
                                                        #Call the password file for see the changes
                                                        self.observer[1].PasswordListUpdate()
                                                except Exception as e:
                                                        pass
                                        else:
                                                #Show error if there is a row like this
                                                GUI_option.Popup(self.window,title_=Language._("form error"), text_=Language._("form error msg username"),
                                                      width=600, height=350, pos_x_window=None, pos_y_window=None, x_text_pos=20, y_text_pos=130,
                                                      bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12,
                                                      x_button_position = 200, y_button_position=250,
                                                      icon_im="warning", x_icon=290, y_icon=10)

                                else:
                                        #If there is empty form
                                        GUI_option.Popup(self.window,title_=Language._("form error"), text_=Language._("form error msg miss key-username"),
                                                         width=600, height=350, pos_x_window=None, pos_y_window=None, x_text_pos=20, y_text_pos=130,
                                                         bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12,
                                                         x_button_position = 200, y_button_position=250,
                                                         icon_im="warning", x_icon=290, y_icon=10)
                        else:
                                #if not path
                                if global_variable.current_path == "":
                                        GUI_option.Popup(self.window,title_=Language._("error path"), text_=Language._("error path msg"),
                                              width=600, height=350, pos_x_window=None, pos_y_window=None, x_text_pos=20, y_text_pos=130,
                                              bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12,
                                              x_button_position = 180, y_button_position=220,
                                              icon_im="warning", x_icon=290, y_icon=10)
                except Exception as e:
                        pass
        
#End class button insert

class Information_usb_port_on_screen():
        '''This class shows on the screen information regarding the USB'''
        def __init__(self,Interface,width_canvas, height_canvas, x_canvas, y_canvas, x_text, y_text, font_, txt_width = 0, outline_rect_color = "red",
                        rect_x = 0, rect_y = 0, rect_x1 = 0, rect_y1 = 0, border_width = 0):
                
                self.window = Interface #Save ctk parent
                self.text = []

                #---- Canvas -----#
                self.canvas = tk.Canvas(Interface,width=width_canvas, height=height_canvas, bg="white")
                self.canvas.place(x = x_canvas, y = y_canvas)

                #---- Rect in canvas ---#
                self.canvas.rect = self.canvas.create_rectangle(rect_x,rect_y, rect_x1, rect_y1, outline=outline_rect_color, width=border_width)

                #---- Text inside the rect inside the canvas --#
                string_text = Language._("usb info")
                self.title = self.canvas.create_text(x_text ,y_text,text = string_text, width = 0, fill='black', anchor = "nw", font = font_)      

        def Update(self, dir_path="", space = []):
                '''
                This function will update the info box.
                Accept only two arguments: directory path and usb space info
                '''
                
                self.Remove() #Remove the previous info

                x_text, y_text = 10, 60

                try:
                        string_text = "Path: " + str(dir_path)
                        global_variable.current_path = dir_path
                        
                except Exception as e: string_text = "USB: "
                
                self.text.append(self.canvas.create_text(x_text , y_text, text = string_text, width = 0, fill='black', anchor = "nw"))
                y_text = y_text + 55

                try:
                        if space[1]: string_text = Language._("info free space") + str(space[1]) + " Gb"
                except Exception as e: string_text = Language._("info free space")
                                
                self.text.append(self.canvas.create_text(x_text , y_text, text = string_text, width = 0, fill='black', anchor = "nw"))
                y_text = y_text + 55

                try:
                        if space[0]: string_text = Language._("info total space") + str(space[0]) + " Gb"
                except Exception as e: string_text = Language._("info total space")
                        
                self.text.append(self.canvas.create_text(x_text , y_text, text = string_text, width = 0, fill='black', anchor = "nw"))
                self.window.update() #Update the GUI

        def Remove(self):
                temp = self.text
                for i in range(0,len(temp)):
                        self.canvas.delete(self.text[i])
                        self.window.update()
                self.text = []
                global_variable.current_path = ""

#End class Information_on_screen

