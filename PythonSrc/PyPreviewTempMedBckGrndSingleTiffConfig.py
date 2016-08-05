import numpy as np
import sys
import os
import glob
import time
from subprocess import call

FolderName = sys.argv[1]

os.chdir(FolderName)
CfgFile = 'Cfg.tmp'


CurrentFiles = glob.glob('*.tif')
print "\n//////////////////////////\nSelect File to work on:\n\n"
for kat in range(len(CurrentFiles)):
    print  str(kat) + " : " + CurrentFiles[kat]

WorkFolderNum = raw_input("Enter File to process (i.e. 4):  ")

FileName = CurrentFiles[int(WorkFolderNum)]

MedSize = 2
while (np.mod(MedSize,2) == 0):
    MedSize = raw_input("Enter the median window size (enter an odd number such as 101):  ")
    MedSize = int(MedSize)


CWD_n =os.getcwd()
FolderNames = CWD_n.split("/")
FolderOut = FolderNames[len(FolderNames)-1]+ FileName  + 'MedBckgSubs'
Bckg_FN = FolderNames[len(FolderNames)-1]+ FileName + 'MedBckg'


#FolderOut = FolderNames[len(FolderNames)-1] + 'BckgSubs'
#Bckg_FN = FolderNames[len(FolderNames)-1]+'Bckg'
#FolderOut = FolderName + 'BckgSubs'
#Bckg_fn = FolderName+'Bckg'
if os.path.isdir(FolderOut):
    print FolderOut
    print Bckg_FN
    var = raw_input("Output folder already exists any existing processed data will be overwritten, do you wish to conitnue? Y/N [N]: ")
    if (var == 'Y' or var == 'y'):
        print "Starting background substraction and file preview..."
        ##cleans up tempfolder
        shellAct = "rm -r " + FolderOut + "/*"
        call(shellAct,shell = 'True')
        shellAct = "rm -r " + Bckg_FN + "/*"
        call(shellAct,shell = 'True')
        shellAct = "rm -r " +FileName+ "_Preview.tif"
        call(shellAct,shell = 'True')
    else:
        sys.exit("\n\n//////////////////////////////////////////////////////////\nProcessed Folder duplicated please rename your data folder (MM)\n//////////////////////////////////////////////////////////\n")
else:
    os.mkdir(FolderOut)
    os.mkdir(Bckg_FN)
    var = 'Created'




while os.path.exists(CfgFile):
    print 'Configuration file already present \n waiting for clean up ....\n'
    time.sleep(5)


CfgData = FileName+";"+str(MedSize)
f = open(CfgFile, 'w')
f.write(CfgData)
f.close()

