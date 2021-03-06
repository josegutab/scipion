# ***************************************************************************
# * Authors:     Laura del Cano (ldelcano@cnb.csic.es)
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
from pyworkflow.em.protocol import ProtImportCTF, ProtImportMicrographs


class TestImportBase(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.dsXmipp = DataSet.getDataSet('xmipp_tutorial')
        cls.dsGrigorieff = DataSet.getDataSet('grigorieff')

    
class TestImportCTFs(TestImportBase):

    def testImportCTFFromXmipp(self):
        #First, import a set of micrographs
        protImport = self.newProtocol(ProtImportMicrographs, filesPath=self.dsXmipp.getFile('allMics'), samplingRate=1.237, voltage=300)
        self.launchProtocol(protImport)
        self.assertIsNotNone(protImport.outputMicrographs.getFileName(), "There was a problem with the import")

        protCTF = self.newProtocol(ProtImportCTF,
                                 importFrom=ProtImportCTF.IMPORT_FROM_XMIPP3,
                                 filesPath=self.dsXmipp.getFile('ctfsDir'),
                                 filesPattern='*.ctfparam')
        protCTF.inputMicrographs.set(protImport.outputMicrographs)
        protCTF.setObjLabel('import ctfs from xmipp ')
        self.launchProtocol(protCTF)

        self.assertIsNotNone(protCTF.outputCTF, "There was a problem when importing ctfs.")

    def testImportCTFFromGrigorieff(self):
        #First, import a set of micrographs
        protImport = self.newProtocol(ProtImportMicrographs, filesPath=self.dsXmipp.getFile('allMics'), samplingRate=1.237, voltage=300)
        self.launchProtocol(protImport)
        self.assertIsNotNone(protImport.outputMicrographs.getFileName(), "There was a problem with the import")

        protCTF = self.newProtocol(ProtImportCTF,
                                 importFrom=ProtImportCTF.IMPORT_FROM_GRIGORIEFF,
                                 filesPath=self.dsGrigorieff.getFile('ctfsDir'),
                                 filesPattern='*.out')
        protCTF.inputMicrographs.set(protImport.outputMicrographs)
        protCTF.setObjLabel('import ctfs from grigorieff ')
        self.launchProtocol(protCTF)

        self.assertIsNotNone(protCTF.outputCTF, "There was a problem when importing ctfs.")

