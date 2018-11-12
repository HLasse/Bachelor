#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 09:46:56 2018

@author: lasse
"""


# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import os
import wave
from os import listdir
from os.path import isfile, join

import re


# In[2]:

mypath='/home/lasse/Desktop/Bachelor/Autobiographic/'
os.chdir(mypath)


# In[3]:

"""
Triangles1epPatients
TrianglesControls
TrianglesChronicPatients
"""


# In[4]:

rel_dir_path = 'Controls1/' # Change this one to process the other folders


# In[5]:

TimeCodes = pd.read_csv(rel_dir_path+'test.csv', sep=",")


# In[6]:

TimeCodes.head(5)


# In[7]:

# Fix bad timecodes
#if rel_dir_path == 'Triangles1epPatients':
#    TimeCodes.loc[(TimeCodes['File']=='dp31.txt') & (TimeCodes['TimeStop']=='(0:06:12.8'), "TimeStop"] = '(0:06:12.8)'
#    TimeCodes.loc[(TimeCodes['File']=='dp4.txt') & (TimeCodes['TimeStart']=='1(0:09:12.8)'), "TimeStart"] = '(0:09:12.8)'


# In[8]:

def get_coded_files(df, file_col):
    return np.unique(df[file_col])

def sub_txt_to_wav(fnames):
    return [f[:-4]+".wav" for f in fnames]


# In[9]:

coded_files = get_coded_files(TimeCodes, "File")
coded_files = sub_txt_to_wav(coded_files)


# In[10]:

coded_files


# In[11]:

def get_filepaths(rel_wav_path, coded_files):
    """
    Find Wav files in folder (path given relative to cwd)
    Check against the timecoded files
    """
    # Find all relevant files
    fileList=[ f for f in listdir(join(os.getcwd(),rel_wav_path)) if isfile(join(os.getcwd(),rel_wav_path,f)) ]
    fileList= [s for s in fileList if 'wav' in s]
    fileList= [s for s in fileList if s in coded_files]
    return fileList
    


# In[12]:

filepaths = get_filepaths(rel_dir_path,coded_files)
filepaths


# In[13]:

def slice(infile, outfilename, start_ms, end_ms):
    width = infile.getsampwidth()
    rate = infile.getframerate()
    fpms = rate / 1000 # frames per ms
    length = int((end_ms - start_ms) * fpms)
    start_index = int(start_ms * fpms)
    
    out = wave.open(outfilename, "w")
    out.setparams((infile.getnchannels(), width, rate, length, 
                   infile.getcomptype(), infile.getcompname()))
    
    infile.rewind()
    anchor = infile.tell()
    infile.setpos(anchor + start_index)
    out.writeframes(infile.readframes(length))


# In[14]:

def valid_timecode(s):
    return bool(re.match("^\(\d:\d\d:\d\d.\d\)", s))


# In[15]:

def run_slicer(rel_wav_path, file_paths, timecodes):
    
    if not os.path.exists(rel_wav_path+"/sliced"):
        os.makedirs(rel_wav_path+"/sliced")
    for FileName in sorted(file_paths):
        print(str(FileName))
        t=timecodes.copy()
        t=t[t['File'] == FileName[:-3]+"txt"] # Find relevant rows in timecodes df. [:-4] removes .wav

        for i in range(len(t.index)):
            OutName=rel_wav_path+"/sliced/"+str(FileName[:-4])+'_'+str(i)+'.wav'
            
            x=t['TimeStart'].values[i]
            if not valid_timecode(x):
                continue
            StartTime=int(float(x[1])*3600000 + float(x[3])*600000 + float(x[4])*60000 + float(x[6])*10000 + float(x[7])*1000 + float(x[9])*100)
            
            x=t['TimeStop'].values[i]
            if not valid_timecode(x):
                continue
            EndTime=int(float(x[1])*3600000 + float(x[3])*600000 + float(x[4])*60000 + float(x[6])*10000 + float(x[7])*1000 + float(x[9])*100)
            
            FileNamePath = rel_wav_path + "/" + FileName
            print(FileNamePath)
            print(OutName)
            try:
                InFile = wave.open(FileNamePath, "r")
            except IOError:
                print('IOError')
                print('File not found')
            try:
                slice(InFile, OutName, StartTime, EndTime)
            except:   
                print('Slicer not working')
        try:
            print(file_paths)
            print(FileName)
            file_paths.remove(FileName)
        except ValueError:
            raise ValueError('File not found')
            break

    print('Files Not Matched: '+ '\n'.join(file_paths))


# In[16]:

run_slicer(rel_dir_path, filepaths, TimeCodes)


# In[17]:

def get_bad_timecodes(rel_wav_path, file_paths, timecodes):
    
    for FileName in sorted(file_paths):
        #print(FileName + ":")
        t=timecodes.copy()
        t=t[t['File'] == FileName[:-3]+"txt"] # Find relevant rows in timecodes df. [:-4] removes .wav

        for i in range(len(t.index)):
            
            x=t['TimeStart'].values[i]
            if not valid_timecode(x):
                print("____start_____")
                print(FileName)
                print(str(x))
                continue

            x=t['TimeStop'].values[i]
            if not valid_timecode(x):
                print("____stop_____")
                print(FileName)
                print(str(x))
                continue


# In[18]:

get_bad_timecodes(rel_dir_path, filepaths, TimeCodes)


# In[ ]:



