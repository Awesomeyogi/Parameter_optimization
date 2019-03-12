#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 08:24:43 2019
requires following files
1) dft_data.csv (this is taxt file contaning angle and sft scan energies)
2)bTVBT4_zro.itp
3)com files
4)top files



@author: yogesh
"""
import numpy as np
import sys
import os
import re
import xlrd
import os.path
import unicodedata
import subprocess
import shutil
import xlwt
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
from sklearn. metrics import r2_score

from subprocess import call
from os import listdir
from os.path import isfile, join
cwd = os.getcwd()   #current working directory



dft_dat = pd.read_csv("dft_data.csv")
print (dft_dat)

#===================READING ALL FILES IN ACCENDING ORDER===========================================================================
onlyfiles = [f for f in listdir(cwd) if isfile(join(cwd, f))] #will extract only files from a address leaving out directories

alist = []
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

def get_energies(ext):
    name = []
    energy = []
    dic = {'name_'+ext:name,'pot_energy_'+ext:energy}
    for x in alist:
        if x[-4:]==".log" and x[-7:-4] == ext:      # Change as per log file 
            filename = x
            file = open(filename,'r')
            print  (filename)
            lines = file.readlines()
            file.close()
            for h,line in enumerate(lines):
                if "Energies (kJ/mol)" in line:
                    for l,eng_terms in enumerate(lines[h+1:h+6]):
                        if "Potential" in eng_terms:
                            eng_term = eng_terms.split()
                            index = eng_term.index("Potential")
                            engs = lines[h+2+l].split()
                            eng = engs[index]
                            name.append(filename)
                            energy.append(eng)
                          
                    
    return dic
#_______________________________________________________                    
orignal = get_energies("org")  
zero   =  get_energies("zro")
               
df1  = pd.DataFrame(orignal)
df2  = pd.DataFrame(zero)
R = pd.concat([dft_dat, df1,df2 ], axis=1, sort=False)

#________________________________________________________

z_e = R["pot_energy_zro"].values
zro_engs = []
print(len(z_e))
for en in z_e:
    zro_engs.append(float(en)-float(z_e[0])) 
R["zro_ref_engs"] = zro_engs

o_e = R["pot_energy_org"].values
org_engs = []
for en in o_e:
    org_engs.append(float(en)-float(o_e[0])) 
R["org_ref_engs"] = org_engs




#_________________________________________________________ 
# import data

d_e = R["dft_eng"].values
dft_engs = []
for en in d_e:
    dft_engs.append((en-d_e[0])*2625.5)  # calulating reference energies in Kjoule/mol
R["dft_ref_en"] = dft_engs
R['diffrence'] = R['dft_ref_en'] - R['zro_ref_engs']

R.to_csv("trial.csv")
#__________________________________________________________________
X = R["angle"].values
Y = R["diffrence"].values

# define function for fitting

def Dih (ang,c0,c1,c2,c3,c4,c5):
    sai = 180 - ang
    p = np.cos(np.radians(sai))
    
    return (c0*(p**0)+c1*(p**1)+c2*(p**2)+c3*(p**3)+c4*(p**4)+c5*(p**5))



# find optical parameters
P0 = [-15.13,19,-10,-26,32,15]  #initial guesses
c,cov = curve_fit (Dih, X, Y, P0) #fit model

print("optimal parameters are:")
print(c)

# calculate predictions
y_pred = Dih(X,c[0],c[1],c[2],c[3],c[4],c[5])



#plot data and prediction
# =============================================================================
# plt.figure()
# plt.title('Diffrence in DFT and MM_Zero')
# plt.plot(X,Y,'r--',label='actual')
# plt.plot(X,y_pred,'b-',label='predicted')
# plt.ylabel('E in KJ/mol')
# plt.xlabel('Angle')
# plt.legend(loc='best')
# plt.show()
# =============================================================================
#=====================================================================
# This part is directly copied from auto_part1
itp_file = open("bTVBT4_Zero.itp",'r')
print  ("reading Zro.itp")
itp_lines = itp_file.readlines()
itp_file.close()

ndx = 0
code = 0

for i,line in enumerate(itp_lines):
    if "[ dihedrals ] ; propers" in line:
        ndx = i
for org,line in enumerate(itp_lines[ndx+3:]):
    word = line.split()
    if len(word) != 0:
        code += 1
        print(code,":",org+ndx+3,":",line)    
        
        
    if len(word) == 0:
        break
            
input_string = input("Enter only one Dihedral code:")
list  = input_string.split()       
new_dihedral = []

for l in list:
    line = itp_lines[ndx+2+int(l)]  
    word = line.split()
    if len(word) != 0:
        print(word,"yyy")
        word[4] = 3
        word[5] = round(c[0],4)
        word[6] = round(c[1],4)
        word[7] = round(c[2],4)
        word[8] = round(c[3],4)
        word[9] = round(c[4],4)
        word[10] = round(c[5],4)
        word[11] = ";"
        word[12:] = " "
        new ='  '.join(map(str, word))
        new_dihedral.append(new)
    if len(word) == 0:
        break
print (new_dihedral)    
#______________________________________________________________  
f = open("bTVBT4_cor.itp","w")

orignal_index = []
for a in list:
    orignal_index.append(int(a)+ndx+2)
    
for b,line in enumerate(itp_lines):
    if b in orignal_index:
        index = orignal_index.index(b)
        f.write(new_dihedral[index])
        f.write("\n")
    else:
        f.write(line)

f.close()
#==========================================================================

#______Writing script for corrected dihedral__________

for i in onlyfiles[:]:
    print (i[-4:])
    if i[-4:]==".com":
        filename = i
        name = i[:-4]
        # creating script file
        f1 = open(name+"-cor.sh",'w')
        f1.write(
                """#!/bin/bash -l
#SBATCH -N 1
#SBATCH -t 1:00:00
#SBATCH -J {}
#SBATCH -A 2018-2-50      
#SBATCH -e error.log
#SBATCH -o output.log
input={}
cmd=md

export OMP_NUM_THREADS=1
APRUN_OPTIONS="-n 1 -d 1 -cc none"

module swap PrgEnv-cray PrgEnv-gnu
module add gromacs/5.0.6

# prep data
log=$input-$cmd-cor

# ---> execute gromacs tasks <---

aprun $APRUN_OPTIONS gmx_mpi grompp -f $cmd.mdp -c $input.gro -p cor.top -o $input-$cmd-cor.tpr -maxwarn 1 > $log.1 2>&1   #-n index.ndx 
aprun $APRUN_OPTIONS gmx_mpi mdrun -s $input-$cmd-cor.tpr -rerun $input.gro -g $input-$cmd-cor.log 


                """.format(name,name)
                )
        f1.close()
        call("sbatch {}-cor.sh".format(name),shell=True)




