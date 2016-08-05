import numpy as np
import sys
from PIL import Image
import os
import glob
import time
from subprocess import call
import tifffile
from scipy import stats
from scipy import ndimage
import javabridge as jv
import bioformats as bf
jv.start_vm(class_path=bf.JARS)


##print(sys.argv[1])
os.chdir(sys.argv[1])


##CtrlWhile = 0
##MedSize = 101 ##Make it even
MedSteps = 10
##LinSTD_fn = "LinearSTD.dat"
##SqrSTD_fn = "SquareSTD.dat"
Counts = 0##np.loadtxt('Count.STD')

#FileNamePattern = '*.tif'
#File8bitSuff = '-8B'
#ConvertOpt = "-quiet"##" -quiet -auto-level -depth 8"

FolderName = sys.argv[1]
CfgFile = 'Cfg.tmp'
f = open(CfgFile, 'r')
FN_lst = f.readline()
f.close()
FN_lst = FN_lst.split(";",1)
FilesOnFold = FN_lst[0]
MedSize = FN_lst[1] 
MedSize = int(MedSize)
MedStepsRange = MedSize/10
os.remove(CfgFile)

SaveFilesName = FilesOnFold[0:len(FilesOnFold)-4]
##os.chdir(FolderName)
#print(FolderName)
##CfgFile = 'Cfg.tmp'
##if not os.path.isfile(CfgFile):
##    sys.exit("\n\n//////////////////////////////////////////////////////////\nProcessed Folder duplicated please r##ename your data folder (MM)\n//////////////////////////////////////////////////////////\n")
##else:
##    os.remove(CfgFile)
##f = open(CfgFile, 'r')
##FN_lst = f.readline()
##f.close()
##FN_lst = FN_lst.split(";",1)
##WorkFolderName = FN_lst[0]
##SeqSize = FN_lst[1] 


##os.remove(CfgFile)

##os.chdir(WorkFolderName)



CWD_n =os.getcwd()
FolderNames = CWD_n.split("/")
FolderOut = FolderNames[len(FolderNames)-1] + FilesOnFold + 'MedBckgSubs'
Bckg_FN = FolderNames[len(FolderNames)-1]+ FilesOnFold +'MedBckg'
SuperPrev_fn = FolderNames[len(FolderNames)-1] + FilesOnFold + "_Preview.tif"
BckgSubs_fn = FolderOut + '/MedBckgSubs'
Bckg_fn = Bckg_FN  + '/MedBckg'

if os.path.isfile(SuperPrev_fn):
    os.remove(SuperPrev_fn)



##FilesOnFold## = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
Char1 = 'bool' 
rdr = bf.ImageReader(FilesOnFold, perform_init=True)
Meta = bf.get_omexml_metadata(FilesOnFold)
md = bf.omexml.OMEXML(Meta)#,xml=None
pixels = md.image().Pixels
TempStack = False
VolumeStack = False
if (pixels.SizeT > 1):
    TempStack = True    
    StackLength = pixels.SizeT
elif (pixels.SizeZ > 1):
    VolumeStack = True
    StackLength = pixels.SizeZ
else: 
    print(FilesOnFold)
    sys.exit("\n\n Selected file is not a Stack \n\n")
  
if TempStack:
    Data_temp= rdr.read(t=0,rescale=False)
else:
    Data_temp= rdr.read(z=0,rescale=False)
##Data_temp = tifffile.imread(FilesOnFold,key=1)
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')uint16'
Char = Char1+', '+Char2
##FullData = np.zeros(int(SeqSize),dtype = Char)

##FilesNum = len(FilesOnFold)

##FilesNumOld = len(FilesOnFold)-1

if 1:
##while CtrlWhile < 12: ##will run the loop for 30 seconds without new images before leaving the script
    ##with tifffile.TiffFile(FilesOnFold) as tif:
        ##TotalFrames=len(tif.pages)-1
    ##    images = tif.asarray()## reads stack into images
    
    ##del tif
    ##images.shape
    ##images = tifffile.imread(FilesOnFold[0])
    ##CntFull = 0
    ##for Files_fn in FilesOnFold:## stores all the imags into a vector
    ##    if ~FullData [CntFull][0]:
    ##        Data_temp = tifffile.imread(Files_fn)
    ##        FullData [CntFull][0] = 1
    ##        FullData [CntFull][1][:,:] = Data_temp[:,:]
    ##    CntFull+=1
   
    if (StackLength > MedSize): #(images.shape[0] TotalFrames > MedSize): 
        #WorkFiles = FilesOnFold[Counts:Counts+MedSize]
        ##Counts += 1 
        #CtrlWhile = 0
        #WorkFile8 = WorkFiles[0]
        #img = tifffile.imread(WorkFile8)
        ##img = tifffile.imread(FilesOnFold,key = Counts)
        if TempStack:
            img = rdr.read(t=Counts,rescale=False)
        else:
            img = rdr.read(z=Counts,rescale=False)
        ##img = images[Counts,:,:]
        VecSize = img.shape[0]*img.shape[1]
        #lallap
        for katF in np.arange(StackLength-MedSize):##images.shape[0] np.arange(TotalFrames-MedSize):
            TempVec = np.zeros((VecSize,MedSteps+1))+np.nan
        
            katCt = 0
            for kat in range(Counts,Counts+MedSize,MedStepsRange):#range(0,MedSize,MedSteps):
                #WorkFile8 = WorkFiles[kat]
                #img = tifffile.imread(WorkFile8)
                if TempStack:
                    img = rdr.read(t=kat,rescale=False)
                else:
                    img = rdr.read(z=kat,rescale=False)
                ##img = images[kat,:,:] ##img = tifffile.imread(FilesOnFold,key = kat)#img = images[kat,:,:]  #FullData [kat][1][:,:]
                VecSize = img.shape[0]*img.shape[1]
                imgVec = np.ndarray.flatten(np.reshape(img,(VecSize,1)))
                TempVec [:,katCt] = imgVec
                katCt += 1
            ##
            MedImgVec = np.median(TempVec,1).astype(np.int16)

            MedImg = np.reshape(MedImgVec,(img.shape[0],img.shape[1]))
                
            #WorkFileMed = WorkFiles[MedSize/2]
            #img = tifffile.imread(WorkFileMed)
            if TempStack:
                img = rdr.read(t=Counts+MedSize/2,rescale=False)
            else:
                img = rdr.read(z=Counts+MedSize/2,rescale=False)
            ##img = images[Counts+MedSize/2,:,:]##img = tifffile.imread(FilesOnFold,key = Counts+MedSize/2)#img = images[Counts+MedSize/2,:,:]
            BckgSubs = img.astype(np.int16)-MedImg.astype(np.int16)##/
            BckgSubs[BckgSubs<0] = 0
            WorkFiles = FilesOnFold[0:len(FilesOnFold)-4]
            FileSave = BckgSubs_fn + WorkFiles + '_' + str(Counts) + '.tif' ##Filename for background substracted frame
            #im = Image.fromarray(BckgSubs)
            tifffile.imsave(FileSave,BckgSubs)
            FileSave = Bckg_fn + WorkFiles + '_' + str(Counts) + '.tif' ##Filename for background substracted frame
            tifffile.imsave(FileSave,MedImg)
            ##im = Image.fromarray(MedImg)
            ##im.save(FileSave)
            ##yayaya
            ##Mode substraction
            ##BckgSubsVec = np.ndarray.flatten(np.reshape(BckgSubs,(VecSize,1)))
        
            if os.path.isfile(SuperPrev_fn):
                #LinSTD = np.loadtxt(LinSTD_fn)
                #SqrSTD = np.loadtxt(SqrSTD_fn)
                LinSTD = LinSTD + BckgSubs
                SqrSTD = SqrSTD + BckgSubs**2
                Var = np.sqrt((SqrSTD*Counts-LinSTD**2)/(Counts*(Counts-1))).astype(np.float64)
                ##VarImg = np.reshape(Var,(img.shape[0],img.shape[1]))
                ##im = Image.fromarray(VarImg)
                ##im.save(SuperPrev_fn)
                im = Image.fromarray(Var.astype(np.float32))
                im.save(SuperPrev_fn)
                SuperPrev_fnT = SuperPrev_fn+'f'
                tifffile.imsave(SuperPrev_fn,Var.astype(np.float32))
                ##FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
                ##FilesNum = len(FilesOnFold)
            
            else:
                LinSTD = BckgSubs
                SqrSTD = BckgSubs**2
                Var = np.sqrt((SqrSTD*Counts-LinSTD**2)/(Counts*(Counts-1))).astype(np.float32)
                ##VarImg = np.reshape(Var,(img.shape[0],img.shape[1]))
                ##VarImg = np.reshape(Var,(img.shape[0],img.shape[1]))
                ##im = Image.fromarray(VarImg)
                ##im.save(SuperPrev_fn)
                im = Image.fromarray(Var.astype(np.float32))
                im.save(SuperPrev_fn)
                SuperPrev_fnT = SuperPrev_fn+'f'
                tifffile.imsave(SuperPrev_fnT,Var.astype(np.float32))
                ##FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
                ##FilesNum = len(FilesOnFold)
            
            Counts += 1
            
    else:
        print("Stack ",FilesOnFold," is too small - select another data set")
       ## time.sleep(5)
       ## FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
       ## FilesNumOld = FilesNum
       ## FilesNum = len(FilesOnFold)
       ## if (FilesNum == FilesNumOld):
       ##     CtrlWhile += 1 

## saves all input files in single tif
##CntFull=0
##DataSave = np.zeros((int(SeqSize),Data_temp.shape[0],Data_temp.shape[1]))
##for Files_fn in FilesOnFold:
##    if FullData [CntFull][0]:
##        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
##    CntFull+=1
##
##OutPutSingleFile = '../'+WorkFolderName+'.tif'
##with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
##    tif.save(DataSave, compress=0)
jv.kill_vm()
print "All Done!"
## saves all Bacground substracted files in single tif
FileNamePattern = BckgSubs_fn + '*'
FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
Char1 = 'bool'
Data_temp = tifffile.imread(FilesOnFold[0])
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')uint16'
Char = Char1+', '+Char2
FullData = np.zeros(len(FilesOnFold),dtype = Char)
CntFull = 0
for Files_fn in FilesOnFold:
    if ~FullData [CntFull][0]:
        Data_temp = tifffile.imread(Files_fn)
        FullData [CntFull][0] = 1
        FullData [CntFull][1][:,:] = Data_temp[:,:]
        ##yadayada
    CntFull+=1

CntFull = 0
DataSave = np.zeros((len(FilesOnFold),Data_temp.shape[0],Data_temp.shape[1]),dtype=np.uint16)
for Files_fn in FilesOnFold:
    if FullData [CntFull][0]:
        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
    CntFull+=1

OutPutSingleFile = SaveFilesName+FolderOut+'.tif'
with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
    tif.save(DataSave, compress=0)

## saves all Bacground files in single tif
FileNamePattern = Bckg_fn + '*'
FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
Char1 = 'bool'
Data_temp = tifffile.imread(FilesOnFold[0])
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')uint16'
Char = Char1+', '+Char2
FullData = np.zeros(len(FilesOnFold),dtype = Char)
CntFull = 0
for Files_fn in FilesOnFold:
    if ~FullData [CntFull][0]:
        Data_temp = tifffile.imread(Files_fn)
        FullData [CntFull][0] = 1
        FullData [CntFull][1][:,:] = Data_temp[:,:]
    CntFull+=1

CntFull = 0
DataSave = np.zeros((len(FilesOnFold),Data_temp.shape[0],Data_temp.shape[1]),dtype=np.uint16)
for Files_fn in FilesOnFold:
    if FullData [CntFull][0]:
        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
    CntFull+=1

OutPutSingleFile = SaveFilesName+Bckg_FN + '.tif'
with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
    tif.save(DataSave, compress=0)



##cleans up tempfolder
FileNamePattern = BckgSubs_fn + '*'
shellAct = "rm " + FileNamePattern
call(shellAct,shell = 'True')
shellAct = "rmdir " + FolderOut
call(shellAct,shell = 'True')
FileNamePattern = Bckg_fn + '*'
shellAct = "rm " + FileNamePattern
call(shellAct,shell = 'True')
shellAct = "rmdir " + Bckg_FN
call(shellAct,shell = 'True')
##os.chdir("..")
##shellAct = "tar -cvzf " + WorkFolderName + ".tar.gz " + WorkFolderName
##call(shellAct,shell = 'True')

        



