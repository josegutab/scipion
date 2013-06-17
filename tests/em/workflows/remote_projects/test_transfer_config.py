"""
Created on Apr 9, 2013

@author: antonio
"""
import sys
import unittest
from pyworkflow.manager import Manager
from utils.file_transfer import *
from pyworkflow.hosts import ExecutionHostMapper, ExecutionHostConfig
from os.path import split

projName = "TestProject"

class TestTransfer(unittest.TestCase):
    
    def setUp(self):
        manager = Manager()
        self.proj = manager.createProject(projName)  # Now it will be loaded if exists
        self.fileTransfer = FileTransfer()
    
    def testTransferProtocols(self):
        result = self.proj.mapper.selectByClass('EmanProtBoxing')
        if len(result):    
            for emanProtBoxing in result:
                emanProtBoxing.setHostName('glassfishdev')
                hostsMapper = ExecutionHostMapper(self.proj.hostsPath)
                executionHostConfig = hostsMapper.selectByLabel(emanProtBoxing.getHostName())
                self.proj.sendProtocol(emanProtBoxing, executionHostConfig)
       
        self.assertTrue(self.checkProtocolFiles(emanProtBoxing))  

    def checkProtocolFiles(self, protocol):        
        hostsMapper = ExecutionHostMapper(self.proj.hostsPath)
        executionHostConfig = hostsMapper.selectByLabel(protocol.getHostName())
        projectFolder = split(self.proj.path)[1]
        
        filePathList = []        
        
        for filePath in protocol.getFiles():
            targetFilePath = join(executionHostConfig.getHostPath(), projectFolder, filePath)
            filePathList.append(targetFilePath)                        
                        
        # Check if all files was correctly transferred        
        notSentFiles = self.fileTransfer.checkOneHostFiles(filePathList, 
                                                           executionHostConfig.getHostName(), 
                                                           executionHostConfig.getUserName(), 
                                                           executionHostConfig.getPassword(), 
                                                           gatewayHosts = None, 
                                                           numberTrials = 1,                        
                                                           forceOperation = False,
                                                           operationId = 1)
        return (len(notSentFiles) == 0)

if __name__ == "__main__":
    #import sys;sys.argv = ["", "Test.testName"]
    print "HOLAAAA"
    unittest.main()