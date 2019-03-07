# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 18:34:12 2018

@author: YOGESH
"""
import sys
import os
import re
import xlrd
import os.path
import unicodedata
import subprocess
import shutil
import xlwt

from subprocess import call
from os import listdir
from os.path import isfile, join
cwd = os.getcwd()   #current working directory

onlyfiles = [f for f in listdir(cwd) if isfile(join(cwd, f))] #will extract only files from a address leaving out directories

alist = []
import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

for x in onlyfiles[:]:
    if x[-4:]==".log":
        alist.append(x)
alist.sort(key=natural_keys)

book = xlwt.Workbook()
sh = book.add_sheet('Sheet1',cell_overwrite_ok=True)
row = 0
Energy = []
name = []

for x in alist:
    if x[-4:]==".log":
        filename = x
        file = open(filename,'r')
        print  (filename)
        lines = file.readlines()
        file.close()
        K = 0
        
        for h,line in enumerate(lines):
            if "Potential    Kinetic En" in line:
                name.append(x[:-4])
                words = lines[h+1].split()
                Energy.append(float(words[2]))
                #sh.write(row+1,1,float(words[3]))
                #sh.write(row+1,0,x[:-4]) 
                break
    

    row +=1  
    


for j,ene in enumerate(Energy):
    sh.write(j,0,name[j])
    sh.write(j,1,Energy[j])
row +=1
book.save("Energies.xls")

print (Energy)
