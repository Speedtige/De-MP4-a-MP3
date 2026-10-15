
# -*- coding: utf-8 -*-
#!/usr/bin/env python

from moviepy.editor import *
import os, sys

##=========================================================================================================
##=========================================================================================================

class Path():
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for pyinstaller"""
        try:
            #PyInstaller Create a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

##=========================================================================================================
##=========================================================================================================

def output_name_name(name, output_name):

    txt_title1 = name
    txt_title2 = txt_title1.split("/")
    txt_title3 = txt_title2[-1]

    name_1 = txt_title3.split('/')[-1]
    name_2 = name_1.split('.')[0]

    name = output_name + '/' + name_2 + '.mp3'
    path_4 = os.path.isfile(name)
    
    if path_4 == True:
        
        return 'Se Encuentra'

    else:
        
        return '/' + name_2 + '.mp3'

def convert(mp4_name, output_name):

    try:
    
        for i in mp4_name:
            path_1 = Path.resource_path(i)
            path_2 = Path.resource_path(output_name)

            mp3_file = output_name_name(path_1, output_name)

            if mp3_file == 'Se Encuentra':
                continue

            else:

                path_3 = Path.resource_path(path_2 + mp3_file)

                videoclip = VideoFileClip(path_1)
                audioclip = videoclip.audio
                audioclip.write_audiofile(path_3)
                audioclip.close()
                videoclip.close()

        return 'He Finalizado Exitosamente'

    except Exception as e:
        print(e)