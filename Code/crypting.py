'''
Author: Riccardo Sebastiani
Application Name: PenDrive Password Manager
Version: 0.1
Copyright © 2026

License: GNU GPL v3 (General Public License)

This module is for crypting algorithm 
'''

try:
        from Cryptodome.Cipher import AES
        from Cryptodome.Util.Padding import pad
        from Cryptodome.Util.Padding import unpad
except Exception as e:
        print(f"ERROR: {e}")

import global_variable
import zlib

def crypt_aes(text):
        try:
                key = bytes(global_variable.KeyString, 'utf-8') #16, 24 or 32 byte
                cipher = AES.new(key, AES.MODE_ECB) # Modo semplice per iniziare
                y_compressed = zlib.compress(text.encode('utf-8'))
                y = pad(y_compressed, 16)
                y = cipher.encrypt(y)
                return y
        except Exception as e:
               print(e)

def decrypt_aes(text):
        try:
                key_byte = bytes(global_variable.KeyString,'utf-8')
                text_byte = bytes.fromhex(text)
                cipher = AES.new(key_byte, AES.MODE_ECB)
                text = cipher.decrypt(text_byte)
                text = unpad(text, AES.block_size)
                text_decompressed = zlib.decompress(text)
                return_value = text_decompressed.decode('utf-8')
                return return_value
        
        except Exception as e:
                return False
#End functions
