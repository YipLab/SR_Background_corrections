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


CWD_n =os.getcwd()
FolderNames = CWD_n.split("/")


FolderOutGauss = FolderNames[len(FolderNames)-1]+ FileName  + 'GaussBckgSubs'
Bckg_FNGauss = FolderNames[len(FolderNames)-1]+ FileName +'GaussBckg'

FolderOutGaussScale = FolderNames[len(FolderNames)-1]+ FileName  + 'GaussBckgSubsScale'


#FolderOut = FolderNames[len(FolderNames)-1] + 'BckgSubs'
#Bckg_FN = FolderNames[len(FolderNames)-1]+'Bckg'
#FolderOut = FolderName + 'BckgSubs'
#Bckg_fn = FolderName+'Bckg'
if os.path.isdir(FolderOutGauss):
    print FolderOutGauss
    print Bckg_FNGauss
    var = raw_input("Output folder already exists any existing processed data will be overwritten, do you wish to conitnue? Y/N [N]: ")
    if (var == 'Y' or var == 'y'):
        print "Starting background substraction and file preview..."
        ##cleans up tempfolder
        shellAct = "rm -r " + FolderOutGauss + "/*"
        call(shellAct,shell = 'True')
        shellAct = "rm -r " + Bckg_FNGauss + "/*"
        call(shellAct,shell = 'True')
        shellAct = "rm -r " + FolderOutGaussScale + "/*"
        call(shellAct,shell = 'True')
        shellAct = "rm -r " +FileName+ "_Preview.tif"
        call(shellAct,shell = 'True')
    else:
        sys.exit("\n\n//////////////////////////////////////////////////////////\nProcessed Folder duplicated please rename your data folder (MM)\n//////////////////////////////////////////////////////////\n")
else:
    os.mkdir(FolderOutGaussScale)
    os.mkdir(FolderOutGauss)
    os.mkdir(Bckg_FNGauss)
    var = 'Created'




while os.path.exists(CfgFile):
    print 'Configuration file already present \n waiting for clean up ....\n'
    time.sleep(5)

print FileName

f = open(CfgFile, 'w')
f.write(FileName)
f.close()

