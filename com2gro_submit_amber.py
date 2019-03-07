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


#file = open("lig1.top",'r')
#print  ("reading li1.gro")
#lines_lig1 = file.readlines()
#file.close()


file = open("lig.gro",'r')
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
        f1 = open(name+".sh",'w')
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
log=$input-$cmd.log

# ---> execute gromacs tasks <---

aprun $APRUN_OPTIONS gmx_mpi grompp -f $cmd.mdp -c $input.gro -p lig1.top -o $input-$cmd.tpr -maxwarn 1 > $log.1 2>&1   #-n index.ndx 
aprun $APRUN_OPTIONS gmx_mpi mdrun -s $input-$cmd.tpr -rerun $input.gro  >> $log 2>&1


                """.format(name)
                )
        f1.close()
        call("sbatch {}.sh".format(name),shell=True)

#aprun $APRUN_OPTIONS gmx_mpi grompp -f $cmd.mdp -c $input.gro -p lig1.top -o $input-$cmd.tpr > $log.1 2>&1   #-n index.ndx 
#aprun $APRUN_OPTIONS gmx_mpi mdrun -s $input-$cmd.tpr -deffnm $input-$cmd -cpi $input-$cmd.cpt >> $log 2>&1
