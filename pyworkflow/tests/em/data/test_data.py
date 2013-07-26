'''
Created on May 20, 2013

@author: laura
'''

from glob import glob, iglob
import unittest
from pyworkflow.tests import *
from pyworkflow.em.data import *
from pyworkflow.utils.path import makePath


class TestSetOfMicrographs(unittest.TestCase):
        
    @classmethod
    def setUpClass(cls):
        cls.outputPath = getOutputPath('test_data')
        
        cls.dbGold = getGoldPath('Micrographs_BPV3', 'micrographs_gold.sqlite')
        
        cls.micsPattern = getInputPath('Micrographs_BPV3', '*.mrc')
        
        cls.dbFn = getOutputPath(cls.outputPath, 'micrographs.sqlite')
        
        #cls.mics = glob(cls.micsPattern)
        cls.mics = []
        for mic in iglob(cls.micsPattern):
            cls.mics.append(getRelPath(mic))
        
        if len(cls.mics) == 0:
            raise Exception('There are not micrographs matching pattern')
        cls.mics.sort()
                  
        cleanPath(cls.outputPath)
        makePath(cls.outputPath)
    
        
    def checkSet(self, setMics):
        idCount = 1
        
        for fn, mic in zip(self.mics, setMics):            
            self.assertEqual(fn, mic.getFileName(), "micrograph name in the set is wrong")
            self.assertEqual(idCount, mic.getId(), "micrograph id in the set is wrong")
            mic2 = setMics[idCount] # Test getitem
            self.assertEqual(mic, mic2, "micrograph got from id is wrong")
            idCount += 1            
        
    def testCreate(self):
        """ Create a SetOfMicrographs from a list of micrographs """
        setMics = SetOfMicrographs(self.dbFn, tiltPairs=False)
        setMics.setSamplingRate(1.2)
        for fn in self.mics:
            mic = Micrograph(fn)
            setMics.append(mic)
            
        setMics.write()        
        self.checkSet(setMics)
        
    def testRead(self):
        """ Read micrographs from a SetOfMicrographs """
        setMics = SetOfMicrographs(self.dbGold)
        self.checkSet(setMics)

    
       
if __name__ == '__main__':
#    suite = unittest.TestLoader().loadTestsFromName('test_data_xmipp.TestXmippCTFModel.testConvertXmippCtf')
#    unittest.TextTestRunner(verbosity=2).run(suite)
    
    unittest.main()