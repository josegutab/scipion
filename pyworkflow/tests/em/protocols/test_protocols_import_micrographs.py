# ***************************************************************************
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *
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
# *  e-mail address 'xmipp@cnb.csic.es'
# ***************************************************************************/

import os
from itertools import izip

from pyworkflow.tests import BaseTest, setupTestProject, DataSet
from pyworkflow.em.protocol import ProtImportMicrographs
from pyworkflow.em.data import SetOfMicrographs


class TestImportBase(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.dsXmipp = DataSet.getDataSet('xmipp_tutorial')
        cls.dsEmx = DataSet.getDataSet('emx')
        cls.dsMda = DataSet.getDataSet('mda')
        
    
class TestImportMicrographs(TestImportBase):
    
    def checkMicSet(self, micSet, goldFn):
        """ Compare micrographs of micSet with the 
        ones in the goldFn. Maybe except the full path.
        """
        goldSet  = SetOfMicrographs(filename = goldFn)

        for mic1, mic2 in izip(goldSet, micSet):
            # Remove the absolute path in the micrographs to
            # really check that the attributes should be equal
            mic1.setFileName(os.path.basename(mic1.getFileName()))
            mic2.setFileName(os.path.basename(mic2.getFileName()))

            self.assertTrue(mic1.equalAttributes(mic2, verbose=True))        
    
    def test_pattern(self):
        """ Import several micrographs from a given pattern.
        """
        args = {'importFrom': ProtImportMicrographs.IMPORT_FROM_FILES,
                'filesPath': self.dsXmipp.getFile('micrographs'),
                'filesPattern': '*.mrc',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.,
                'voltage': 100,
                'samplingRate': 2.1
                }
        
        
        def _checkOutput(prot, micsId=[], size=None):
            mics = getattr(prot, 'outputMicrographs', None)
            self.assertIsNotNone(mics)
            self.assertEqual(mics.getSize(), size)
            for i, m in enumerate(mics):
                if micsId:
                    self.assertEqual(m.getObjId(), micsId[i])
                self.assertAlmostEqual(m.getSamplingRate(), args['samplingRate'])
                a = m.getAcquisition()
                self.assertAlmostEqual(a.getVoltage(), args['voltage'])

        # Id's should be set increasing from 1 if ### is not in the 
        # pattern
        protMicImport = self.newProtocol(ProtImportMicrographs, **args)
        protMicImport.setObjLabel('from files')
        self.launchProtocol(protMicImport)
        _checkOutput(protMicImport, [1, 2, 3], size=3)
        
        # Id's should be taken from filename    
        args['filesPattern'] = 'BPV_####.mrc'
        protMicImport = self.newProtocol(ProtImportMicrographs, **args)
        protMicImport.setObjLabel('from files (with id)')
        self.launchProtocol(protMicImport)
        _checkOutput(protMicImport, [1386, 1387, 1388], size=3)

        # Import some micrographs from EMX        
        emxFn = self.dsEmx.getFile('coordinatesT1')
        args['importFrom'] = ProtImportMicrographs.IMPORT_FROM_EMX
        args['emxFile'] = emxFn
        protEmxImport = self.newProtocol(ProtImportMicrographs, **args)
        protEmxImport.setObjLabel('from emx (with coords)')
        self.launchProtocol(protEmxImport)
        _checkOutput(protEmxImport, [], size=1)

    
    def test_fromEmx(self):
        """ Import an EMX file with micrographs and defocus
        """
        emxFn = self.dsEmx.getFile('emxMicrographCtf1')
        protEmxImport = self.newProtocol(ProtImportMicrographs,
                                         importFrom=ProtImportMicrographs.IMPORT_FROM_EMX,
                                         emxFile=emxFn,
                                         magnification=10000,
                                         samplingRate=2.46
                                         )
        protEmxImport.setObjLabel('from emx ')
        self.launchProtocol(protEmxImport)
        
        self.checkMicSet(protEmxImport.outputMicrographs, 
                         goldFn=self.dsEmx.getFile('emxMicrographCtf1Gold'))

    
    def test_fromXmipp(self):
        """ Import an EMX file with micrographs and defocus
        """
        micsRoot = 'xmipp_project/Micrographs/Imported/run_001/%s'
        micsMd = self.dsXmipp.getFile(micsRoot % 'micrographs.xmd')
        prot1 = self.newProtocol(ProtImportMicrographs,
                                         importFrom=ProtImportMicrographs.IMPORT_FROM_XMIPP3,
                                         mdFile=micsMd,
                                         magnification=10000,
                                         samplingRate=1.237
                                         )
        prot1.setObjLabel('from xmipp (no-ctf)')
        self.launchProtocol(prot1)
        self.checkMicSet(prot1.outputMicrographs, 
                         goldFn=micsMd.replace('.xmd', '_gold.sqlite'))
        
        micsRoot = 'xmipp_project/Micrographs/Screen/run_001/%s'
        micsMd = self.dsXmipp.getFile(micsRoot % 'micrographs.xmd')
        prot2 = self.newProtocol(ProtImportMicrographs,
                                         importFrom=ProtImportMicrographs.IMPORT_FROM_XMIPP3,
                                         mdFile=micsMd,
                                         magnification=10000,
                                         samplingRate=1.237
                                         )
        prot2.setObjLabel('from xmipp (ctf)')
        self.launchProtocol(prot2)
        self.checkMicSet(prot2.outputMicrographs, 
                 goldFn=micsMd.replace('.xmd', '_gold.sqlite'))
        
