#!/usr/bin/env python
#------------------------------------------------------------------------------------------------
# Xmipp protocol for subtraction
#
# Example use:
# ./xmipp_partial_projection_subtraction.py
#
# Authors: 
#
#-----------------------------------------------------------------------------
# {section} Global parameters
#-----------------------------------------------------------------------------
#Comment
Comment='Describe your project here...'
# {file} Protocol Name
ProtocolName='ProjMatch/xmipp_2.4_subtraction_crunchy/xmipp_protocol_projmatch_backup.py'

# {expert}{file} CTFDat file with CTF data:
""" The input selfile may be a subset of the images in the CTFDat file, but all 
    images in the input selfile must be present in the CTFDat file. This field is 
    obligatory if CTF correction is to be performed. 
    Note that this file should be positioned in the project directory, and that the
    image names and ctf parameter filenames should be in absolute paths.
    Usually optained from the protocol file
"""

#Show results for iteration
""" Use data coming from iteration
"""
iterationNo=2

# Resume at iteration
""" Set to 1 to start a new run, set to -1 to continue the process (where you left it),
    set to a positive number N to restart at the begining of iteration N
    Note1: Do NOT delete working directory if this option is not set to 1
    Note2: Set this option to -1 if you want to perform extra iterations after
           successfully finish an execution
"""
ContinueAtIteration =1

# {expert} Resume at Iter (vs Step)
"""This option control how to resume a previously performed run.
    Set to TRUE to restart at the beginning of iteration N
    or FALSE to continue at step N. (N is set in the next parameter).
    NOTE:If you do not know what are you doing make it equal to False
"""
IsIter =False

#{expert}{file} Select the input volume
"""Name of the reference volume by default Iter_X_reconstruction.vol

"""
szInputVolumeName=''
#{expert}{file} Select docfile used to compute references
"""Name of the doc file used to compute reference library, usually 
   ../Iter_(X-1)/Iter_(X-1)_current_angles.doc
"""
szDocFileRef=''

# {expert} Mask reference volume?
doMask =True

#Crown Mask radius (inner)
dRradiusMin=39

#{expert}  iCrown mask radius center (outter)
dRradiusMax=64

# {expert} Backup Experimental Proj. angles
doBackupProjectionAngles =True

# {expert}Angular sampling rate
"""Angular distance (in degrees) between neighboring projection  points
   usually obtained from protocol file
"""   
AngSamplingRateDeg=''

# {expert}  Angular search range 
"""Maximum change in rot & tilt  (in +/- degrees)
   usually obtained from protocol file
"""   
MaxChangeInAngles =''

# {expert} Symmetry group
""" See http://xmipp.cnb.uam.es/twiki/bin/view/Xmipp/Symmetry
    for a description of the symmetry groups format
    If no symmetry is present, give c1
    usually obtained from protocol file
"""
SymmetryGroup=''

CTFDatName=''
# {expert} Correct by CTF:
""" Set to True if you want to correct by CTF
"""
doCTFCorrection=False

#------------------------------------------------------------------------------------------------
# {section} Parallelization issues
#------------------------------------------------------------------------------------------------

# distributed-memory parallelization (MPI)?
""" This option provides distributed-memory parallelization on multi-node machines. 
    It requires the installation of some MPI flavour, possibly together with a queueing system
"""
DoParallel=True

# Number of (shared-memory) threads?
""" This option provides shared-memory parallelization on multi-core machines. 
    It does not require any additional software, other than xmipp
"""
NumberOfThreads=2

# Number of MPI processes to use:
NumberOfMpiProcesses=2

# minumum size of jobs in mpi processe. Set to 1 for large images (e.g. 500x500) and to 10 for small images (e.g. 100x100)
MpiJobSize ='3'

# MPI system Flavour 
""" Depending on your queuing system and your mpi implementation, different mpirun-like commands have to be given.
    Ask the person who installed your xmipp version, which option to use. Or read: xxx
"""
SystemFlavour='TORQUE-OPENMPI'

#Verify
"""Check that some output files are created. 
"""
Verify=True

# {expert} print wrapper name
PrintWrapperCommand=True

# {expert} print wrapper parameters
PrintWrapperParameters=True

# {expert} show file verification
ViewVerifyedFiles=True 

#------------------------------------------------------------------------------------------------
# {hidden} Analysis of results
""" This script serves only for GUI-assisted visualization of the results
"""
AnalysisScript='visualize_partial_projection_subtraction.py'


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# {end-of-header} USUALLY YOU DO NOT NEED TO MODIFY ANYTHING BELOW THIS LINE ...
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#
myName='partial_projection_subtraction'
run_file1='./readDocfileAndPairExperimentalAndReferenceImages_v3.sh'
subtractionDir ='Subtraction'
referenceDir   ='Refs'
referenceStack   ='ref'
volsDir='Vols'
tempFileName=''
current_angles='current_angles.doc'
import os,sys,shutil,time
scriptdir = os.path.split(os.path.dirname(os.popen('which xmipp_protocols', 'r').read()))[0] + '/lib'
sys.path.append(scriptdir) # add default search path
scriptdir = os.path.split(os.path.dirname(os.popen('which xmipp_protocols', 'r').read()))[0] + '/protocols'
sys.path.append(scriptdir)
scriptdir = os.getcwd()
sys.path.append(scriptdir)
import log, logging
from pysqlite2 import dbapi2 as sqlite
from arg import getListFromVector, getBoolListFromVector
import dataBase,arg
global _dataBase
from xmipp import *
import glob

def actionsToBePerformedInsideLoop(_log):
    a=0
    for iterN in range(1, defocusGroupNo):
        #Create auxiliary metadata with image names , angles and CTF
        _Parameters = {
                       'CTFgroupName': defGroups[iterN]
                      ,'DocFileRef':DocFileRef[iterN]
                      ,'filename_currentAngles':filename_currentAngles
                      }
        command = "joinImageCTF"
        _VerifyFiles = []
        auxFilename = FileName(DocFileRef[iterN])
        _VerifyFiles.append(auxFilename.removeBlockName())
        _dataBase.insertCommand(command, _Parameters, iterN,_VerifyFiles)
        
        
        #reconstruct each CTF group
        _Parameters = {
                       'DocFileRef': DocFileRef[iterN]
                      , 'DoParallel' : DoParallel
                      , 'MpiJobSize':MpiJobSize
                      , 'NumberOfMpiProcesses':NumberOfMpiProcesses
                      , 'NumberOfThreads':NumberOfThreads
                      , 'reconstructedVolume':reconstructedVolume[iterN]
                      , 'SymmetryGroup': SymmetryGroup
                      , 'SystemFlavour':SystemFlavour
                      }
        command = "reconstructVolume"
        _VerifyFiles = []
        _VerifyFiles.append(reconstructedVolume[iterN])
        _dataBase.insertCommand(command, _Parameters, iterN,_VerifyFiles)
        #mask volume before projection
        
        _Parameters = {
                       'dRradiusMax':dRradiusMax
                      ,'dRradiusMin':dRradiusMin
                      ,'maskReconstructedVolume':maskReconstructedVolume[iterN]
                      ,'reconstructedVolume':reconstructedVolume[iterN]
                      }
        command = "maskVolume"
        _VerifyFiles = []
        auxFilename = FileName(DocFileRef[iterN])
        _VerifyFiles.append(maskReconstructedVolume[iterN])
        _dataBase.insertCommand(command, _Parameters, iterN,_VerifyFiles)

        #project reconstructe4d volumes
        _Parameters = {
                      'AngSamplingRateDeg':AngSamplingRateDeg
                      ,'DocFileRef':DocFileRef[iterN]
                      ,'DoParallel' : DoParallel
                      ,'maskReconstructedVolume':maskReconstructedVolume[iterN]
                      ,'MaxChangeInAngles':MaxChangeInAngles
                      , 'MpiJobSize':MpiJobSize
                      ,'NumberOfMpiProcesses':NumberOfMpiProcesses
                      ,'NumberOfThreads':NumberOfThreads
                      ,'referenceStack':referenceStack[iterN]
                      ,'SymmetryGroup': SymmetryGroup
                      ,'SystemFlavour':SystemFlavour
                      }
        command = "createProjections"
        _VerifyFiles = []
        _VerifyFiles.append(referenceStack[iterN])
        tmp = referenceStack[iterN]
        _VerifyFiles.append(tmp.replace('.stk','.doc'))
        _VerifyFiles.append(tmp.replace('.stk','_sampling.txt'))
        
        _dataBase.insertCommand(command, _Parameters, iterN,_VerifyFiles)
                 
#        #apply transform
#        #resta
#    _CTFDatName=CTFDatName
#    if(len(CTFDatName)<1 and doCTFCorrection):
#        if(len(partial_protocol.CTFDatName)>1):
#            _CTFDatName= '../' + partial_protocol.CTFDatName
#    
#    # revisar si realmente hay que pasarle _szDocFileRef a la siguiente funcion     
#    self.readDocfileAndPairExperimentalAndReferenceImages(_szDocFileRef)
#    
#    # Al finalizar cada iteracion borramos el volumen reconstruido
#    os.rm(reconstructedVolume)
         
        
def otherActionsToBePerformedBeforeLoop():
    #Create directories
    _Parameters = {
          'path':subtractionDir
        }
    command = 'createDir2'
    _dataBase.insertCommand(command, _Parameters, 1)
    
    _Parameters = {
          'path':volsDir
        }
    command = 'createDir2'
    _dataBase.insertCommand(command, _Parameters, 1)
    
    _Parameters = {
          'path':referenceDir
        }
    command = 'createDir2'
    _dataBase.insertCommand(command, _Parameters, 1)

def actionsToBePerformedBeforeLoopThatDoNotModifyTheFileSystem():

    global Iteration_Working_Directory
    Iteration_Working_Directory=os.path.join(WorkingDir,'Iter_'+ str(iterationNo))
    
    global subtractionDir  
    subtractionDir = os.path.join(Iteration_Working_Directory,subtractionDir)
    
    global volsDir
    volsDir = os.path.join(subtractionDir,volsDir)

    global referenceDir
    referenceDir = os.path.join(subtractionDir,referenceDir)
    

    
    
    global szInputVolumeName
    if ( len(szInputVolumeName) < 1 ):
        szInputVolumeName = 'Iter_'+str(iterationNo)+'_reconstruction.vol'

    global MaxChangeInAngles
    if(MaxChangeInAngles > 100):
        MaxChangeInAngles=-1

    global filename_currentAngles
    tmpFilename = 'Iter_'+ str(iterationNo) + '_' + current_angles
    filename_currentAngles = os.path.join(Iteration_Working_Directory,tmpFilename)
    
    tmpFileName = os.path.join(WorkingDir,'CtfGroups/ctf_group??????.sel')
    global defGroups
    defGroups=['']
    defGroups +=glob.glob(tmpFileName)
    
    global defocusGroupNo
    defocusGroupNo = len(defGroups)
    
    global DocFileRef
    DocFileRef=['']
    tmpFileName = FileName(filename_currentAngles)
    tmpFileName = tmpFileName.withoutExtension()
    for iterN in range(1, defocusGroupNo ):
        tmpDocFileRef = 'ctfgroup_' + str(iterN).zfill(6) + '@' + tmpFileName + '_ctfgroups.doc'
        DocFileRef.append(tmpDocFileRef
                          )
    global reconstructedVolume
    reconstructedVolume = [""]
    for iterN in range(1, defocusGroupNo ):
        tmpReconstruct = os.path.join(volsDir, 'rec_ctfg' + str(iterN).zfill(6) + '.vol')
        reconstructedVolume.append(tmpReconstruct)
        
    global maskReconstructedVolume
    maskReconstructedVolume = [""]
    for iterN in range(1, defocusGroupNo ):
        tmpReconstruct = os.path.join(volsDir, 'rec_ctfg' + str(iterN).zfill(6) + '_mask.vol')
        maskReconstructedVolume.append(tmpReconstruct)

    global referenceStack
    tmp = referenceStack
    referenceStack = [""]
    for iterN in range(1, defocusGroupNo ):
        tmpReconstruct = os.path.join(referenceDir, tmp + '_' + str(iterN).zfill(6) + '.stk')
        referenceStack.append(tmpReconstruct)


def ImportProtocol():
    pardir=os.path.abspath(os.getcwd())
    import utils_xmipp
    tempFileName=utils_xmipp.unique_filename(ProtocolName)
    fn = FileName(tempFileName)
    fn=fn.getBaseName()
    shutil.copy(ProtocolName,fn+'.py')
    exec  "import " + fn
    global ProjectDir
    ProjectDir = eval(fn +'.ProjectDir')
    global WorkingDir
    WorkingDir = eval(fn +'.WorkingDir')
    global LogDir
    LogDir = eval(fn +'.LogDir')
    global SymmetryGroup
    SymmetryGroup = eval(fn +'.SymmetryGroup')
    global AngSamplingRateDeg
    if(len(AngSamplingRateDeg) < 1):
        AngSamplingRateDeg=arg.getComponentFromVector(eval(fn +'.AngSamplingRateDeg'),iterationNo)
    global MaxChangeInAngles
    if(len(MaxChangeInAngles) < 1):
        MaxChangeInAngles=arg.getComponentFromVector(eval(fn +'.MaxChangeInAngles'),iterationNo)
    global refDirName
    refDirName=  eval(fn +'.LibraryDir')
        
def mainLoop(_log, iter):
    global ContinueAtIteration
    _import = 'from ProjMatchActionsToBePerformedBeforeLoop import createDir2;\
               from aux_partial_projection_subtraction import *'
    _dataBase.setPrintWrapperParameters(PrintWrapperParameters)
    _dataBase.setPrintWrapperCommand(PrintWrapperCommand)
    _dataBase.setProjDir(ProjectDir)
    _dataBase.setVerify(Verify,ViewVerifyedFiles)
    StartAtStepN=_dataBase.getStartingStep(IsIter)
    _dataBase.mainLoop(_log, StartAtStepN, _import)

#
# PROTOCOL STARTS HERE
#######
if __name__ == '__main__':
    #create Logging system
    # Set up logging
    ImportProtocol()
    _log = log.init_log_system(ProjectDir,
                                LogDir,
                                sys.argv[0],
                                WorkingDir)
    
    # Uncomment next line to get Debug level logging
    _log.setLevel(logging.DEBUG)
    _log.debug("Debug level logging enabled")
    #init DataBase
    global _dataBase
    _dataBase = dataBase.dataBase(ProjectDir,
                                LogDir,
                                sys.argv[0],
                                WorkingDir,
                                myName,
                                ContinueAtIteration)
    
    #preprocessing
    try:
        actionsToBePerformedBeforeLoopThatDoNotModifyTheFileSystem()
        otherActionsToBePerformedBeforeLoop()
        actionsToBePerformedInsideLoop(_log)
        mainLoop(_log, iter)
    except sqlite.Error, e:
        print "An error occurred:", e.args[0]
    
                    #(in another file) <<<<< define list with actions and parameters
                    #                  <<<<< store list in database as it is made
                    #                  <<<<< link with restart
    #postprocesing
