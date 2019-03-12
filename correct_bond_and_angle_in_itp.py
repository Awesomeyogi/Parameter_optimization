#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 11:15:12 2019

@author: yogesh

note that itp file should be genrated from acpype

it requires two files 
1) dft cordinates in xyz format with name "dft_opt.xyz"
2) itp file "bTVBT4.itp"


"""

import sys
import os
import re
import xlrd
import os.path
import unicodedata
import subprocess
import shutil
import math
import numpy as np

from subprocess import call

def cal_dis(px,py,pz,qx,qy,qz):
   return(math.sqrt((px-qx)**2 + (py-qy)**2 + (pz-qz)**2))

def get_angle(a,b,c):
    #a = np.array([32.49, -39.96,-3.86])
    #b = np.array([31.39, -39.28, -4.66])
    #c = np.array([31.14, -38.09,-4.49])
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return (np.degrees(angle))
    

dft_file = open("dft_opt.xyz",'r')
print  ("reading dft_opt.xyz")
dft_lines = dft_file.readlines()
dft_file.close()

itp_file = open("bTVBT4.itp",'r')
print  ("reading bTVBT4.itp")
itp_lines = itp_file.readlines()
itp_file.close()
Atom1 = 0
Atom2 = 0
new_bonds = []
new_angle = []
ndx = 0
#_______________________________________________________
#__________________BOND__________________________________
for i,line in enumerate(itp_lines):
    if "[ bonds ]" in line:
        ndx = i
        break
count = 0
for line in itp_lines[ndx+2:]:
    word = line.split()
    if len(word) != 0:
        Atom1 = int(word[0])
        Atom2 = int(word[1])
        Name1,px,py,pz = dft_lines[Atom1+1].split()
        Name2,qx,qy,qz = dft_lines[Atom2+1].split()
        dis = cal_dis(float(px),float(py),float(pz),float(qx),float(qy),float(qz))
        dis_nm = dis/10
        word[3] = float("{0:.5f}".format(dis_nm))
        count += 1
        
        new ='     '.join(map(str, word))
        new_bonds.append(new)
    if len(word) == 0:
        break
#_________________________________________________________
#_____________ANGLE________________________________________
ndx2 = 0
for i,line in enumerate(itp_lines):
    if "[ angles ]" in line:
        ndx2 = i
        break
count2 = 0
for line in itp_lines[ndx2+2:]:
    word = line.split()
    if len(word) != 0:
        Atom1 = int(word[0])
        Atom2 = int(word[1])
        Atom3 = int(word[2])
        print(word)
        Name1,px,py,pz = dft_lines[Atom1+1].split()
        Name2,qx,qy,qz = dft_lines[Atom2+1].split()
        Name3,rx,ry,rz = dft_lines[Atom3+1].split()
        a = np.array([float(px),float(py),float(pz)])
        b = np.array([float(qx),float(qy),float(qz)])
        c = np.array([float(rx),float(ry),float(rz)])
        
        angle = get_angle(a,b,c)
        
        word[4] = float("{0:.5f}".format(angle))
        count2 += 1
        
        new ='    '.join(map(str, word))
        print(new)
        new_angle.append(new)
    if len(word) == 0:
        break


#__________________________________________________________-
f = open("bTVBT4_new2.itp","w")
for i,line in enumerate(itp_lines[:ndx+2]):
    f.write(itp_lines[i])

for j in new_bonds:              #writings new bonds
    f.write(j)
    f.write("\n")

for i in itp_lines[ndx+count+2:ndx2+2]:   #writing pairs
    f.write(i)        


for j in new_angle:               #writing new angles
    f.write(j)
    f.write("\n")

    

for i in itp_lines[ndx2+count2+2:len(itp_lines)]:      #writing reminder of orignal file
    f.write(i)        
    
f.close

