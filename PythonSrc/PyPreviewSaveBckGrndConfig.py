import sys
import os
import glob
import time

FolderName = sys.argv[1]

os.chdir(FolderName)
CfgFile = 'Cfg.tmp'
CurrentDirs = os.listdir('.')
print "\n//////////////////////////\nSelect Folder to work on:\n\n"
for kat in range(len(CurrentDirs)):
    if os.path.isdir(CurrentDirs[kat]):
        print  str(kat) + " : " + CurrentDirs[kat]
WorkFolderNum = raw_input("Enter Folder number (i.e. 4):  ")

WorkFolderName = CurrentDirs[int(WorkFolderNum)]
##os.chdir(WorkFolderName)
##CWD_n =os.getcwd()
##FolderNames = CWD_n.split("/")

print "\n//////////////////////////\n Enter Files in sequence:\n\n"

SeqSize = raw_input("\n-------->>>>>> Enter Files in sequence: (i.e. 5000):  ")

FolderOut = WorkFolderName + 'BckgSubs'
Bckg_fn = WorkFolderName+'Bckg'
if os.path.isdir(FolderOut):
    var = raw_input("Output folder already exists any existing processed data will be overwritten, do you wish to conitnue? Y/N [N]: ")
    if (var == 'Y' or var == 'y'):
        print "Starting background substraction and file preview..."
    else:
        sys.exit("\n\n//////////////////////////////////////////////////////////\nProcessed Folder duplicated please rename your data folder (MM)\n//////////////////////////////////////////////////////////\n")
else:
    os.mkdir(FolderOut)
    os.mkdir(Bckg_fn)



while os.path.exists(CfgFile):
    print 'Configuration file already present \n waiting for clean up ....\n'
    time.sleep(5)


f = open(CfgFile, 'w')
f.write(WorkFolderName + ';' + SeqSize)
f.close()

