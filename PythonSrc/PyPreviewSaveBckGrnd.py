#import matplotlib.pyplot as plt
import numpy as np
import sys
from PIL import Image
import os
import glob
import time
from subprocess import call
import tifffile

print(sys.argv[1])
os.chdir(sys.argv[1])


CtrlWhile = 0
MedSize = 101 ##Make it even
MedSteps = 10
LinSTD_fn = "LinearSTD.dat"
SqrSTD_fn = "SquareSTD.dat"
Counts = 0##np.loadtxt('Count.STD')

FileNamePattern = '*.tif'
#File8bitSuff = '-8B'
#ConvertOpt = "-quiet"##" -quiet -auto-level -depth 8"

FolderName = sys.argv[1]

os.chdir(FolderName)
print(FolderName)
CfgFile = 'Cfg.tmp'

f = open(CfgFile, 'r')
FN_lst = f.readline()
f.close()
FN_lst = FN_lst.split(";",1)
WorkFolderName = FN_lst[0]
SeqSize = FN_lst[1] 


os.remove(CfgFile)

os.chdir(WorkFolderName)



CWD_n =os.getcwd()
FolderNames = CWD_n.split("/")
FolderOut = '../'+ FolderNames[len(FolderNames)-1] + 'BckgSubs'
SuperPrev_fn = '../'+FolderNames[len(FolderNames)-1] + "_Preview.tif"
BckgSubs_fn = FolderOut+'/BckgSubs'
Bckg_fn = '../'+ FolderNames[len(FolderNames)-1]+'Bckg'+'/Bckg'

if os.path.isfile(SuperPrev_fn):
    os.remove(SuperPrev_fn)



FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
Char1 = 'bool' 
Data_temp = tifffile.imread(FilesOnFold[0])
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')uint16'
Char = Char1+', '+Char2
FullData = np.zeros(int(SeqSize),dtype = Char)

FilesNum = len(FilesOnFold)

FilesNumOld = len(FilesOnFold)-1

while CtrlWhile < 12: ##will run the loop for 30 seconds without new images before leaving the script
    CntFull = 0
    for Files_fn in FilesOnFold:
        if ~FullData [CntFull][0]:
            Data_temp = tifffile.imread(Files_fn)
            FullData [CntFull][0] = 1
            FullData [CntFull][1][:,:] = Data_temp[:,:]
        CntFull+=1
   
    if (FilesNum-Counts > MedSize): 
        #WorkFiles = FilesOnFold[Counts:Counts+MedSize]
        #Counts += 1 
        CtrlWhile = 0
        #WorkFile8 = WorkFiles[0]
        #img = tifffile.imread(WorkFile8)
        img = FullData [Counts][1][:,:]
        VecSize = img.shape[0]*img.shape[1]
        TempVec = np.zeros((VecSize,MedSteps+1))+np.nan
        
        katCt = 0
        for kat in range(Counts,Counts+MedSize,MedSteps):#range(0,MedSize,MedSteps):
            #WorkFile8 = WorkFiles[kat]
            #img = tifffile.imread(WorkFile8)
            img = FullData [kat][1][:,:]
            VecSize = img.shape[0]*img.shape[1]
            imgVec = np.ndarray.flatten(np.reshape(img,(VecSize,1)))
            TempVec [:,katCt] = imgVec
            katCt += 1

        Counts += 1
        MedImgVec = np.median(TempVec,1)
        MedImg = np.reshape(MedImgVec,(img.shape[0],img.shape[1]))
        
        #WorkFileMed = WorkFiles[MedSize/2]
        #img = tifffile.imread(WorkFileMed)
        img = FullData [Counts+MedSize/2][1][:,:]
        BckgSubs= img-MedImg;##/
        WorkFiles = FilesOnFold[Counts+MedSize/2][0:len(FilesOnFold[Counts+MedSize/2])-4]
        FileSave = BckgSubs_fn + WorkFiles + '.tif' ##Filename for background substracted frame
        im = Image.fromarray(BckgSubs)
        im.save(FileSave)
        FileSave = Bckg_fn + WorkFiles + '.tif' ##Filename for background substracted frame
        im = Image.fromarray(MedImg)
        im.save(FileSave)
        
        BckgSubsVec = np.ndarray.flatten(np.reshape(BckgSubs,(VecSize,1)))
        
        if os.path.isfile(SuperPrev_fn):
            #LinSTD = np.loadtxt(LinSTD_fn)
            #SqrSTD = np.loadtxt(SqrSTD_fn)
            LinSTD = LinSTD + BckgSubs
            SqrSTD = SqrSTD + BckgSubs**2
            Var = np.sqrt((SqrSTD*Counts-LinSTD**2)/(Counts*(Counts-1)))
            VarImg = np.reshape(Var,(img.shape[0],img.shape[1]))
            im = Image.fromarray(VarImg)
            im.save(SuperPrev_fn)
            FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
            FilesNum = len(FilesOnFold)
            
        else:
            LinSTD = BckgSubs
            SqrSTD = BckgSubs**2
            Var = np.sqrt((SqrSTD*Counts-LinSTD**2)/(Counts*(Counts-1)))
            VarImg = np.reshape(Var,(img.shape[0],img.shape[1]))
            VarImg = np.reshape(Var,(img.shape[0],img.shape[1]))
            im = Image.fromarray(VarImg)
            im.save(SuperPrev_fn)
            FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
            FilesNum = len(FilesOnFold)
    else:
        time.sleep(5)
        FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
        FilesNumOld = FilesNum
        FilesNum = len(FilesOnFold)
        if (FilesNum == FilesNumOld):
            CtrlWhile += 1 

## saves all input files in single tif
CntFull=0
DataSave = np.zeros((int(SeqSize),Data_temp.shape[0],Data_temp.shape[1]))
for Files_fn in FilesOnFold:
    if FullData [CntFull][0]:
        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
    CntFull+=1

OutPutSingleFile = '../'+WorkFolderName+'.tif'
with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
    tif.save(DataSave, compress=0)

## saves all Bacground substracted fies in single tif
FileNamePattern = BckgSubs_fn + '*'

Char1 = 'bool'
Data_temp = tifffile.imread(FilesOnFold[0])
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')float32'
Char = Char1+', '+Char2
FullData = np.zeros(int(SeqSize),dtype = Char)

FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)

CntFull = 0
for Files_fn in FilesOnFold:
    if ~FullData [CntFull][0]:
        Data_temp = tifffile.imread(Files_fn)
        FullData [CntFull][0] = 1
        FullData [CntFull][1][:,:] = Data_temp[:,:]
    CntFull+=1

CntFull = 0
DataSave = np.zeros((len(FilesOnFold),Data_temp.shape[0],Data_temp.shape[1]))
for Files_fn in FilesOnFold:
    if FullData [CntFull][0]:
        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
    CntFull+=1

OutPutSingleFile = FolderOut+'.tif'
with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
    tif.save(DataSave, compress=0)

##cleans up tempfolder
shellAct = "rm " + FileNamePattern
call(shellAct,shell = 'True')
shellAct = "rmdir " + FolderOut
call(shellAct,shell = 'True')
os.chdir("..")
shellAct = "tar -cvzf " + WorkFolderName + ".tar.gz " + WorkFolderName
call(shellAct,shell = 'True')

        



