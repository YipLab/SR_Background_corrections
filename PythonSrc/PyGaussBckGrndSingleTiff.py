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

os.chdir(sys.argv[1])


##MedSize = 101 
##MedSteps = 10
GaussRad = 100
Counts = 0

FolderName = sys.argv[1]
CfgFile = 'Cfg.tmp'
f = open(CfgFile, 'r')
FilesOnFold = f.readline()
f.close()
os.remove(CfgFile)

CWD_n =os.getcwd()
FolderNames = CWD_n.split("/")
FolderOutGauss = FolderNames[len(FolderNames)-1]+ FilesOnFold + 'GaussBckgSubs'
Bckg_FNGauss = FolderNames[len(FolderNames)-1]+ FilesOnFold+'GaussBckg'

FolderOutGaussScale = FolderNames[len(FolderNames)-1]+ FilesOnFold + 'GaussBckgSubsScale'

SuperPrev_fn = FolderNames[len(FolderNames)-1] + FilesOnFold + "_Preview.tif"


BckgSubs_fnGaussScale = FolderOutGaussScale+'/GaussBckgSubsScale'
BckgSubs_fnGauss = FolderOutGauss+'/GaussBckgSubs'
Bckg_fnGauss = Bckg_FNGauss +'/GaussBckg'


if os.path.isfile(SuperPrev_fn):
    os.remove(SuperPrev_fn)
Char1 = 'bool' 
rdr = bf.ImageReader(FilesOnFold, perform_init=True)
Meta = bf.get_omexml_metadata(FilesOnFold)
md = bf.omexml.OMEXML(Meta)
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


##Data_temp= rdr.read(Z=0)
##Data_temp = tifffile.imread(FilesOnFold,key=1)
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')uint16'
Char = Char1+', '+Char2

if 1:
    ##with tifffile.TiffFile(FilesOnFold) as tif:
   ##     images = tif.asarray()## reads stack into images
    
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
   
    if 1: 
        #WorkFiles = FilesOnFold[Counts:Counts+MedSize]
        ##Counts += 1 
        #CtrlWhile = 0
        #WorkFile8 = WorkFLiles[0]
        #img = tifffile.imread(WorkFile8)
        if TempStack:
            img = rdr.read(t=Counts,rescale=False)
        else:
            img = rdr.read(z=Counts,rescale=False)
            ##img =  images[Counts,:,:]
        VecSize = img.shape[0]*img.shape[1]
        #lallap
        for katF in np.arange(StackLength):##np.arange(images.shape[0]):
            #TempVec = np.zeros((VecSize,MedSteps+1))+np.nan
        
            #WorkFileMed = WorkFiles[MedSize/2]
            #img = tifffile.imread(WorkFileMed)
            if TempStack:
                img = rdr.read(t=katF,rescale=False)
            else:
                img = rdr.read(z=katF,rescale=False)
                ##img = images[katF,:,:]
            ##Gaussian substraction
            GaussImg = ndimage.gaussian_filter(img, sigma = GaussRad)
            ##BckgGaussSubs= img-GaussImg;
            BckgGaussSubs= img.astype(np.int16)-GaussImg.astype(np.int16);
            DTp = BckgGaussSubs>0
            BckgGaussSubs = BckgGaussSubs*DTp
            BckgGaussSubs = BckgGaussSubs.astype(np.uint16)
            
            WorkFiles = FilesOnFold[0:len(FilesOnFold)-4]
            FileSave = BckgSubs_fnGauss + WorkFiles + '_' + str(katF) + '.tif' ##Filename for background substracted frame
            #im = Image.fromarray(BckgSubs)
            tifffile.imsave(FileSave,BckgGaussSubs)
            FileSave = Bckg_fnGauss + WorkFiles + '_' + str(katF) + '.tif' ##Filename for background frame
            tifffile.imsave(FileSave,GaussImg)

            ScaleF = img.astype(np.float32).max()/BckgGaussSubs.max()
            BckgGaussSubs=BckgGaussSubs*ScaleF
            BckgGaussSubs=BckgGaussSubs.astype(np.uint16)
            WorkFiles = FilesOnFold[0:len(FilesOnFold)-4]
            FileSave = BckgSubs_fnGaussScale + WorkFiles + '_' + str(katF) + '.tif'
            tifffile.imsave(FileSave,BckgGaussSubs)
            if os.path.isfile(SuperPrev_fn):
                LinSTD = LinSTD + BckgGaussSubs
                SqrSTD = SqrSTD + BckgGaussSubs**2
                Var = np.sqrt((SqrSTD*Counts-LinSTD**2)/(Counts*(Counts-1))).astype(np.float64)
                im = Image.fromarray(Var.astype(np.float32))
                im.save(SuperPrev_fn)
            else:
                LinSTD = BckgGaussSubs
                SqrSTD = BckgGaussSubs**2
                Var = np.sqrt((SqrSTD*Counts-LinSTD**2)/(Counts*(Counts-1))).astype(np.float32)
                im = Image.fromarray(Var.astype(np.float32))
                im.save(SuperPrev_fn)
            
            Counts += 1
            
      
      
print "All Done!"
jv.kill_vm()

## saves all Scaled Background substracted files in single tif

FileNamePattern = BckgSubs_fnGaussScale + '*'
FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
Char1 = 'bool'
Data_temp = tifffile.imread(FilesOnFold[0])
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')float32'
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
DataSave = np.zeros((len(FilesOnFold),Data_temp.shape[0],Data_temp.shape[1]))
for Files_fn in FilesOnFold:
    if FullData [CntFull][0]:
        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
    CntFull+=1

OutPutSingleFile = FolderOutGaussScale+'.tif'
with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
    tif.save(DataSave, compress=0)

## saves all Background substracted files in single tif
FileNamePattern = BckgSubs_fnGauss + '*'
FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
Char1 = 'bool'
Data_temp = tifffile.imread(FilesOnFold[0])
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')float32'
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
DataSave = np.zeros((len(FilesOnFold),Data_temp.shape[0],Data_temp.shape[1]))
for Files_fn in FilesOnFold:
    if FullData [CntFull][0]:
        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
    CntFull+=1

OutPutSingleFile = FolderOutGauss+'.tif'
with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
    tif.save(DataSave, compress=0)


## saves all Background files in single tif
FileNamePattern = Bckg_fnGauss + '*'
FilesOnFold = sorted(glob.glob(FileNamePattern), key=os.path.getmtime)
Char1 = 'bool'
Data_temp = tifffile.imread(FilesOnFold[0])
Char2 = '('+str(Data_temp.shape[0])+','+str(Data_temp.shape[1])+')float32'
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
DataSave = np.zeros((len(FilesOnFold),Data_temp.shape[0],Data_temp.shape[1]))
for Files_fn in FilesOnFold:
    if FullData [CntFull][0]:
        DataSave[CntFull,:,:] = FullData [CntFull][1][:,:]
    CntFull+=1

OutPutSingleFile = Bckg_FNGauss + '.tif'
with tifffile.TiffWriter(OutPutSingleFile, bigtiff=True) as tif:
    tif.save(DataSave, compress=0)



##cleans up tempfolder
FileNamePattern = BckgSubs_fnGaussScale + '*'
shellAct = "rm " + FileNamePattern
call(shellAct,shell = 'True')
shellAct = "rmdir " + FolderOutGaussScale
call(shellAct,shell = 'True')

FileNamePattern = BckgSubs_fnGauss + '*'
shellAct = "rm " + FileNamePattern
call(shellAct,shell = 'True')
shellAct = "rmdir " + FolderOutGauss
call(shellAct,shell = 'True')


FileNamePattern = Bckg_fnGauss + '*'
shellAct = "rm " + FileNamePattern
call(shellAct,shell = 'True')
shellAct = "rmdir " + Bckg_FNGauss
call(shellAct,shell = 'True')
        
