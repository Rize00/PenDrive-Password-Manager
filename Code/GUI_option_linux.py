'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Version: 0.1
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is for the graphics user interface options. Here, you can modify text, position, ecc... 
'''
#---- Python Modules ---#
import tkinter as tk
from tkinter import font as tkfont
import sys
import os
import webbrowser
#---- Application modules ----#
from main_module import Language
import global_variable

def Popup(Interface, title_="Popup", text_="", width=400, height=250, pos_x_window=None, pos_y_window=None, x_text_pos=50, y_text_pos=80,
                          bg_color="#ffffff", text_color="#000000", font_family="Arial", font_size=12, x_button_position = 0, y_button_position=0,
                          icon_im="info", x_icon=0, y_icon=0):
    # Window
    popup = tk.Toplevel(Interface)
    popup.title(title_)
    popup.configure(bg=bg_color)
    popup.resizable(False, False)

    if pos_x_window is not None and pos_y_window is not None:
        popup.geometry(f"{width}x{height}+{pos_x_window}+{pos_y_window}")
    else:
        #Centering
        Interface.update_idletasks()
        x = Interface.winfo_x() + (Interface.winfo_width() // 2) - (width // 2)
        y = Interface.winfo_y() + (Interface.winfo_height() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

    popup.transient(Interface)
    popup.grab_set()

    #Font and Icon
    custom_font = tkfont.Font(family=font_family, size=font_size)
    if icon_im:
            icons = {"info": "ℹ", "warning": "⚠️", "donation" : "🫶", "error usb" : "⛔"}
            choosed_icon = icons.get(icon_im, "")
            # Make Icon

    if icon_im == "info":
        # Make Text
        message = tk.Label(popup, text=text_, bg=bg_color, fg=text_color, 
                           font=custom_font, wraplength=width-x_text_pos-20, justify="left")
        message.place(x=x_text_pos, y=y_text_pos)

        icon = tk.Label(popup, text=choosed_icon, bg=bg_color, fg=text_color, font=(font_family, 25))
        icon.place(x=x_icon - 70, y=y_icon) 

        button = tk.Button(popup, text="OK", width=10, command=popup.destroy)
        button.place(x=x_button_position, y=y_button_position)
        button = tk.Button(popup, text="🌍 Github", width=10, command=lambda: webbrowser.open_new("https://www.github.com"))
        button.place(x=x_button_position-200, y=y_button_position)
        button = tk.Button(popup, text="License", width=10, command=lambda: webbrowser.open_new("https://www.gnu.org/licenses/gpl-3.0.html"))
        button.place(x=x_button_position+200, y=y_button_position)
    elif icon_im == "error usb":
        popup.attributes('-type', 'toolbar')
        border = tk.Frame(popup, highlightbackground="red",highlightthickness=10)
        border.pack(fill="both", expand=True)
        inside_border= tk.Frame(border, bg=bg_color)
        inside_border.pack(expand=True, fill="both")

        icon = tk.Label(inside_border, text=choosed_icon, bg=bg_color, fg=text_color, font=(font_family, 40))
        icon.place(x=x_icon - 110, y=y_icon) 
        
        popup.configure(relief="ridge",bd=20)

        message = tk.Label(inside_border, text=text_, bg=bg_color, fg=text_color, 
                           font=custom_font, wraplength=width-x_text_pos-20, justify="left")
        message.place(x=x_text_pos, y=y_text_pos)

        button = tk.Button(inside_border, text="OK", width=10)
        button.place(x=x_button_position, y=y_button_position)
        button.config(command=lambda: os.execl(sys.executable, os.path.abspath(__file__), *sys.argv))
    else:
        if icon_im == "donation":
            icon = tk.Label(popup, text=choosed_icon, bg=bg_color, fg=text_color, font=(font_family, 25))
            icon.place(x=x_icon - 70, y=y_icon)
            message = tk.Label(popup, text=text_, bg=bg_color, fg=text_color, 
                               font=custom_font, wraplength=width-x_text_pos-20, justify="left")
            message.place(x=x_text_pos, y=y_text_pos)
            button = tk.Button(popup, text="OK", width=10, command=popup.destroy)
            button.place(x=x_button_position, y=y_button_position)
            button.config(command=popup.destroy)
            
        elif icon_im == "warning":
            popup.attributes('-type', 'toolbar')
            border = tk.Frame(popup, highlightbackground="orange",highlightthickness=10)
            icon = tk.Label(popup, text=choosed_icon, bg=bg_color, fg=text_color, font=(font_family, 40))
            icon.place(x=x_icon - 70, y=y_icon)
            
            border.pack(fill="both", expand=True)
            inside_border= tk.Frame(border, bg=bg_color)
            inside_border.pack(expand=True, fill="both")
            message = tk.Label(inside_border, text=text_, bg=bg_color, fg=text_color, 
                           font=custom_font, wraplength=width-x_text_pos-20, justify="left")
            message.place(x=x_text_pos, y=y_text_pos)
            
            popup.configure(relief="ridge",bd=20)
            button = tk.Button(inside_border, text="OK", width=10)
            button.place(x=x_button_position, y=y_button_position)
            button.config(command=popup.destroy)
        else:
            message = tk.Label(popup, text=text_, bg=bg_color, fg=text_color, 
                               font=custom_font, wraplength=width-x_text_pos-20, justify="left")
            message.place(x=x_text_pos, y=y_text_pos)           
            button = tk.Button(popup, text="OK", width=10)
            button.place(x=x_button_position, y=y_button_position)
            button.config(command=popup.destroy)

    Interface.bell()
    
    return popup

#End class popup

class PasswordList():
    def __init__(self):

        self.x_canvas , self.y_canvas = 50, 150
        self.string_text, self.txt_width = Language._("password list") , 1000
        self.list_box_width = 30
        self.list_box_height = 20
        self.width_canvas, self.height_canvas = 17*self.list_box_width, 40

        self.font_text = "Arial"
        self.font_size = 16
        self.text_style = "bold italic"
        self.x_text_position = 160
        self.y_text_position = 17

        self.x_list_box = self.x_canvas + 5
        self.y_list_box = self.y_canvas + 50

    def Get_Option(self):
        return [self.width_canvas, self.height_canvas,
                self.x_canvas, self.y_canvas,
                self.string_text, self.txt_width,
                self.list_box_width, self.list_box_height,
                self.x_text_position, self.y_text_position,
                self.x_list_box, self.y_list_box,
                self.font_text, self.font_size,
                self.text_style]

#End GUI_OptionPasswordList

class InsertBox():
    def __init__(self):
        self.width_canvas, self.height_canvas = 260, 25
        self.x_canvas, self.y_canvas = 750, 150 

        self.string_text = Language._("first entry name")
        self.txt_width = 500
        self.entry_width = 20
        self.entry_height = 20
        self.x_text_position, self.y_text_position = 130,12

        self.shift_xbox_from_text, self.shift_ybox_from_text = -20, 30

    def Get_Option(self):
        return [self.width_canvas, self.height_canvas,
                self.x_canvas, self.y_canvas,
                self.string_text, self.txt_width,
                self.entry_width,
                self.entry_height,
                self.x_text_position, self.y_text_position,
                self.shift_xbox_from_text, self.shift_ybox_from_text]

#End GUI_SaveBox

class KeyConfigBox():
    def __init__(self):
        self.width_canvas, self.height_canvas = 70, 35
        self.x_canvas, self.y_canvas = 50, 80
        self.string_text = "Key:"
        self.txt_width = 200
        self.x_text_position, self.y_text_position = 35, 15
        self.entry_width, self.entry_height= 20, 20
        self.font = ("Arial",12,"bold")

    def Get_Option(self):
        return [self.width_canvas, self.height_canvas, self.x_canvas, self.y_canvas,
                self.string_text, self.txt_width, self.x_text_position, self.y_text_position,
                self.entry_width, self.entry_height, self.font]

class Button():
    def __init__(self):
        self.setKey_x_position = 450
        self.setKey_y_position = 73
        self.insert_x_position = 800
        self.insert_y_position = 330
        
        width_button = 150
        self.setKey_width_button = 150
        self.setKey_height_button = 30
        self.insert_width_button = width_button
        self.insert_height_button = width_button/2

        button_border_color = "#006edc" #"white"
        self.setKey_border_color = button_border_color
        self.insert_border_color= button_border_color
        
        
        self.font = ("Arial", 16, "bold")
        self.corner_radius = None     #Curvatura del tasto
        self.border_width = 5       # Spessore del bordo
        self.fg_color="white"       # Colore background
        self.text_color="black"      # Colore del testo

    def Get_Option_insert(self):
        return [self.insert_x_position, self.insert_y_position,
                self.insert_width_button, self.insert_height_button,
                self.font,
                self.fg_color, self.text_color,
                self.insert_border_color, self.border_width, self.corner_radius]

    def Get_Option_setKey(self):
        return [self.setKey_x_position, self.setKey_y_position,
                self.setKey_width_button, self.setKey_height_button,
                self.font,
                self.fg_color, self.text_color,
                self.insert_border_color, self.border_width, self.corner_radius]
