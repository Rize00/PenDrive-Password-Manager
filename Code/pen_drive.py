#----------- Python modules ----------#
import subprocess
import json
import os
import shutil
from pathlib import Path
from pathlib import PurePath
import time
import platform

import psutil

#---------- Application modules --------#
import global_variable
import crypting

class USBRecursiveScanner():
    ''' This class contains the methods for USB pendrive '''
    def __init__(self):
        # Query lsblk for the hierarchy
        self.cmd = ["lsblk", "-J", "-o", "NAME,MOUNTPOINT,RM,TRAN"]

        self.observer = [] #List of observers
        self.path = "" #Path of the class
        self.reg_key = "" #Key for confront

    def get_usb_mounts(self):
        all_mounts = []
        try:
            current_os = platform.system()

            if current_os == "Linux":
                output = subprocess.check_output(self.cmd).decode('utf-8')
                data = json.loads(output)
                for device in data.get('blockdevices', []):
                    if device.get('tran') == 'usb' or device.get('rm') == '1':
                        self._extract_mountpoints(device, all_mounts)

            elif current_os == "Windows":
                import ctypes
                for part in psutil.disk_partitions(all=False):
                    # 2 = DRIVE_REMOVABLE
                    if ctypes.windll.kernel32.GetDriveTypeW(part.device) == 2:
                        if part.mountpoint:
                            all_mounts.append(part.mountpoint)

            return list(set(filter(None, all_mounts)))
        except Exception as e:
            return [f"Errore: {e}"]

    def _extract_mountpoints(self, device_dict, found_list):
        ''' Recursive function to go down the partitions (children). '''
        # If this level (parent or child) has a mountpoint, take it
        mp = device_dict.get('mountpoint')
        if mp:
            found_list.append(mp)
        
        # If child
        if 'children' in device_dict:
            for child in device_dict['children']:
                self._extract_mountpoints(child, found_list)

    def get_space_gb(self):
        ''' Return the space disk in GB '''
        try:
            if self.path:
                total, used, free = shutil.disk_usage(self.path)
                return [total // (2**30), free // (2**30)]
        except Exception as e:
            pass

    def get_writable_and_not_full(self, min_free_mb=10):
        '''
        Returns only the mountpoints of USB pendrive that are writeable and have at least 'min_free_mb' of space.
        '''
        all_mounts = self.get_usb_mounts() #get mountpoint
        
        valid_mounts = []
        
        for path in all_mounts:
            # Check write
            is_writable = os.access(path, os.W_OK)
            # Check free space
            try:
                usage = shutil.disk_usage(path)
                free_mb = usage.free / (1024 * 1024)
            except Exception:
                free_mb = 0
                
            if is_writable and free_mb > min_free_mb:
                valid_mounts.append(path)

        try:
            valid_mounts = [Path(i) for i in valid_mounts]
        except Exception as e:
            pass
        
        return valid_mounts

    def update_file_compact(self,text_name, new_line=None, remove_line=None):
        '''
        This function is for updating the main file of this application
        - If the file does not exits, it will create it.
        - If there is a new line, it will add
        . If there is a remove line, it will remove it
        3 arguments: text_name, new_line, remove_line
        '''
        lines = []
        if self.path:
            filepath = self.path / text_name
        else:
            #Pah does not exists
            return
        
        # Read the file and saves the lines
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
        # If there is remove line
        if remove_line is not None:
            target = remove_line.strip()
            lines = [l for l in lines if l != target]

        # If there is new line
        if new_line is not None:
            clean_new = new_line.strip()
            if clean_new:
                lines.append(clean_new)

        # Write it down
        with open(filepath, "w", encoding="utf-8") as f:
            for i, l in enumerate(lines):
                f.write(l + "\n") #\n is a good choice
        try:
            if platform.system() == "Windows":
                import ctypes
                hex_code = 0x02 #Hide file in Windows OS
                ctypes.windll.kernel32.SetFileAttributesW(str(filepath), hex_code)
        except Exception as e: pass

        return lines

    def row_filtrer_beginning(self, file_name, prefix):
        founded_row = []        
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                for row in file:
                    if row.startswith(prefix):
                        founded_row.append(row.strip())
        except FileNotFoundError:
            with open(file_name, 'w', encoding='utf-8') as f:
                pass
        
        return founded_row
    

    def ChangePath(self, string):
        try:
            PurePath(string)
            self.path = string
        except TypeError:
            pass

    def GetPath(self): return self.path

    
    def attach(self,observer):
        if observer not in self.observer:
            self.observer.append(observer)
        else: pass

    def detach(self, observer):
        try:
            self.observer.remove(observer)
        except ValueError: pass


    def Return_rows(self):
        try:
            with open(global_variable.main_filename_application, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except Exception as e:
            return []
        
    def PasswordListUpdate(self):
        '''This function will update the password list according to the key'''
        ''' There is a need to use one other variable'''
        if self.path:
            if self.reg_key == "" and global_variable.KeyString != "": #if first time
                self.reg_key = global_variable.KeyString #save the value
                return self.GetList() #Return the list
            elif self.reg_key == global_variable.KeyString:
                show = self.GetList()
                return self.GetList() #Return the list
            elif global_variable.KeyString != "" and self.reg_key != global_variable.KeyString: #Check the key string
                self.reg_key = global_variable.KeyString #save the value
                return self.GetList() #Return the list

    def GetList(self):
        row_list = self.Return_rows()
        if row_list: #If there is something
            username = [s.split(" | ")[0] for s in row_list]
            
            show = [] #List for the list box
            for i in range (0,len(username)):
                x = crypting.decrypt_aes(username[i]) #Try to decrypt
                if x: #if decrypt is successfull
                    show.append(x)
            return show
        else:
            return []

    def RemoveLine(self, text):
        x = crypting.crypt_aes(text) #try to crypt
        if x: #if success
            try:
                row = "".join(self.row_filtrer_beginning(global_variable.main_filename_application, x.hex())) #check the row in hex
                self.update_file_compact(global_variable.main_filename_application, new_line=None, remove_line= row) #remove the row
            except Exception as e:
                pass
                
            
            
