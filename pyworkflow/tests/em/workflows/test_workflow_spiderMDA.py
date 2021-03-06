# **************************************************************************
# *
# * Authors:     J.M. de la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jgomez@cnb.csic.es'
# *
# **************************************************************************


import pyworkflow.em.packages.spider as spider
from pyworkflow.em.convert import ImageHandler
from pyworkflow.em.protocol import ProtImportParticles
from pyworkflow.em.packages.spider.convert import writeSetOfImages

from pyworkflow.tests import setupTestProject, DataSet, unittest, BaseTest
from test_workflow import TestWorkflow

  
   
class TestSpiderConvert(TestWorkflow):
    """ Check the images are converted properly to spider format. """
    
    @classmethod
    def setUpClass(cls):    
        # Create a new project
        setupTestProject(cls)
        cls.dataset = DataSet.getDataSet('mda')
        cls.particlesFn = cls.dataset.getFile('particles')
    
    def test_convert(self):
        """ Run an Import particles protocol. """
        protImport = self.newProtocol(ProtImportParticles, filesPath=self.particlesFn, samplingRate=3.5)
        self.launchProtocol(protImport)
        # check that input images have been imported (a better way to do this?)
        if getattr(protImport, 'outputParticles', None) is None:
            raise Exception('Import of images: %s, failed. outputParticles is None.' % self.particlesFn)
        
        ih = ImageHandler()
        stackFn = self.getOutputPath('stack.stk')
        selFn = self.getOutputPath('stack_sel.stk')
        print "stackFn: ", stackFn
        
        writeSetOfImages(protImport.outputParticles, stackFn, selFn)
        
        #for i, img in enumerate(protImport.outputParticles):
        #    newLoc = (i+1, stackFn)
            #if i > 10:
            #    break
            #print img.getLocation(), 
            #inputXmipp = locationToXmipp(*img.getLocation())
            #outputXmipp = locationToXmipp(*newLoc)
            #cmd = 'source ~/xmipp/.xmipp.bashrc; xmipp_image_convert -i %s -o %s' % (inputXmipp, outputXmipp)
            #print cmd
            #os.system(cmd)  
        #   ih.convert(img, newLoc)
            
       
       
class TestSpiderWorkflow(TestWorkflow):
    @classmethod
    def setUpClass(cls):    
        # Create a new project
        setupTestProject(cls)
        cls.dataset = DataSet.getDataSet('mda')
        cls.particlesFn = cls.dataset.getFile('particles')
    
    def test_mdaWorkflow(self):
        """ Run an Import particles protocol. """
        protImport = self.newProtocol(ProtImportParticles, filesPath=self.particlesFn, samplingRate=3.5)
        self.launchProtocol(protImport)
        # check that input images have been imported (a better way to do this?)
        if protImport.outputParticles is None:
            raise Exception('Import of images: %s, failed. outputParticles is None.' % self.particlesFn)
        
        protFilter = self.newProtocol(spider.SpiderProtFilter)
        protFilter.inputParticles.set(protImport)
        protFilter.inputParticles.setExtendedAttribute('outputParticles')
        self.launchProtocol(protFilter)
        
        protAPSR = self.newProtocol(spider.SpiderProtAlignAPSR)
        protAPSR.inputParticles.set(protFilter.outputParticles)
        self.launchProtocol(protAPSR)
        
        protPairwise = self.newProtocol(spider.SpiderProtAlignPairwise)
        protPairwise.inputParticles.set(protFilter.outputParticles)
        self.launchProtocol(protPairwise)       
         
        protMask = self.newProtocol(spider.SpiderProtCustomMask)
        protMask.inputImage.set(protAPSR.outputAverage)
        self.launchProtocol(protMask)       
              
        protCAPCA = self.newProtocol(spider.SpiderProtCAPCA)
        protCAPCA.maskType.set(1)
        protCAPCA.maskImage.set(protMask.outputMask)
        protCAPCA.inputParticles.set(protAPSR.outputParticles)
        self.launchProtocol(protCAPCA)
        
        protWard = self.newProtocol(spider.SpiderProtClassifyWard)
        protWard.pcaFile.set(protCAPCA.imcFile)
        protWard.inputParticles.set(protAPSR.outputParticles)
        self.launchProtocol(protWard)
        
        protKmeans = self.newProtocol(spider.SpiderProtClassifyKmeans)
        protKmeans.pcaFile.set(protCAPCA.imcFile)
        protKmeans.inputParticles.set(protAPSR.outputParticles)
        protKmeans.numberOfClasses.set(4)
        self.launchProtocol(protKmeans)
        
        protDiday = self.newProtocol(spider.SpiderProtClassifyDiday)
        protDiday.pcaFile.set(protCAPCA.imcFile)
        protDiday.inputParticles.set(protAPSR.outputParticles)
        self.launchProtocol(protDiday)               
        


if __name__ == "__main__":
    unittest.main()
