# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 18:34:12 2018

@author: YOGESH

files required 
1) com files
2) name_org
3) lig.gro # this is required to set correct format of .gro

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


#file = open("lig1.top",'r')
#print  ("reading li1.gro")
#lines_lig1 = file.readlines()
#file.close()


file = open("lig.gro",'r')#aprun $APRUN_OPTIONS gmx_mpi grompp -f $cmd.mdp -c $input.gro -p lig1.top -o $input-$cmd.tpr > $log.1 2>&1   #-n index.ndx 
#aprun $APRUN_OPTIONS gmx_mpi mdrun -s $input-$cmd.tpr -deffnm $input-$cmd -cpi $input-$cmd.cpt >> $log 2>&1
print  ("reading lig1.gro")
lines_lig1 = file.readlines()
file.close()
resnum = []
resname = []
atom = []
number = []

for h,line in enumerate(lines_lig1[2:41]):

            words = line.split()
            resnum.append(words[0])
            resname.append(words[1])
           
            atom.append(words[2])
            number.append(words[3])
            
print("number have {} lines".format(len(number)))

for i in onlyfiles[:]:
    print (i[-4:])
    if i[-4:]==".com":
        filename = i
        name = i[:-4]
        file = open(filename,'r')
        print  (filename)
        lines = file.readlines()
        file.close()
        x_cord =[]
        y_cord =[]
        z_cord =[]
        for h,line in enumerate(lines[6:45]):
            words = line.split()
            x_cord.append(float(words[2])/10)
            y_cord.append(float(words[3])/10)
            z_cord.append(float(words[4])/10)
	
        # writing gro file 
        f = open(name+".gro",'w')
        f.write("mol \n")
        f.write("   39\n")
        print(len(x_cord),"_____")
        for j in range(len(x_cord)):
         #   f.write("{:10s}{:5s}{:5s}{:8.3f}{:8.3f}{:8.3f}\n".format(resname[j],atom[j],number[j],x_cord[j],y_cord[j],z_cord[j]))
            res = resname[j]
            f.write("{:>5s}{:<5.5s}{:>5.5s}{:>5s}{:8.3f}{:8.3f}{:8.3f}\n".format("1",res[:],atom[j],number[j],x_cord[j],y_cord[j],z_cord[j]))
    
        #'xyz': "{resid:>5d}{resname:<5.5s}{name:>5.5s}{index:>5d}{pos[0]:8.3f}{pos[1]:8.3f}{pos[2]:8.3f}\n"
        f.write("   5.00000   5.00000   5.00000\n")
        f.close()
        # creating script file
        f1 = open(name+"-org.sh",'w')
        f1.write(
                """#!/bin/bash -l
#SBATCH -N 1
#SBATCH -t 1:00:00
#SBATCH -J prot-mol-md
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
log=$input-$cmd-org

# ---> execute gromacs tasks <---

aprun $APRUN_OPTIONS gmx_mpi grompp -f $cmd.mdp -c $input.gro -p org.top -o $input-$cmd-org.tpr -maxwarn 1 > $log.1 2>&1   #-n index.ndx 
aprun $APRUN_OPTIONS gmx_mpi mdrun -s $input-$cmd-org.tpr -rerun $input.gro -g $input-$cmd-org.log


                """.format(name)
                )
        f1.close()
        call("sbatch {}-org.sh".format(name),shell=True)

#______________Zero-Dihedral_________________--

itp_file = open("bTVBT4_org.itp",'r')
print  ("reading orignal.itp")
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
            
input_string = input("Enter a list Dihedral code separated by space ")
list  = input_string.split()       
f.close()
new_dihedral = []

for l in list:
    line = itp_lines[ndx+2+int(l)]  
    word = line.split()
    if len(word) != 0:
        print(word,"yyy")
        word[4] = 3
        word[5] = 0
        word[6] = 0
        word[7] = 0
        word[8] = 0
        word[9] = 0
        word[10] = 0
        word[11] = ";"
        word[12:] = " "
        new ='     '.join(map(str, word))
        new_dihedral.append(new)
    if len(word) == 0:
        break
print (new_dihedral)    
#______________________________________________________________  
f = open("bTVBT4_Zro.itp","w")

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

#______Writing script for zero dihedral__________

for i in onlyfiles[:]:
    print (i[-4:])
    if i[-4:]==".com":
        filename = i
        name = i[:-4]
        # creating script file
        f1 = open(name+"-zro.sh",'w')
        f1.write(
                """#!/bin/bash -l
#SBATCH -N 1
#SBATCH -t 1:00:00
#SBATCH -J prot-mol-md
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
log=$input-$cmd-zro

# ---> execute gromacs tasks <---

aprun $APRUN_OPTIONS gmx_mpi grompp -f $cmd.mdp -c $input.gro -p zro.top -o $input-$cmd-zro.tpr -maxwarn 1 > $log.1 2>&1   #-n index.ndx 
aprun $APRUN_OPTIONS gmx_mpi mdrun -s $input-$cmd-zro.tpr -rerun $input.gro -g $input-$cmd-zro.log 


                """.format(name)
                )
        f1.close()
        call("sbatch {}-zro.sh".format(name),shell=True)







