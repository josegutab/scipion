# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
"""
This sub-package will contains Xmipp specific protocols
"""

from bibtex import _bibtex # Load bibtex dict with references

_logo = "xmipp_logo.png"
_references = ['delaRosaTrevin2013', 'Sorzano2013']

from xmipp3 import *
from convert import *
from dataimport import *

# some sub-packages
from nma import *
from pdb import *

from protocol_preprocess import *

from viewer import XmippViewer

from viewer_cl2d import XmippCL2DViewer
from viewer_cltomo import XmippCLTomoViewer
from viewer_ctf_discrepancy import XmippCTFDiscrepancyViewer
from viewer_ml2d import XmippML2DViewer
from viewer_movie_alignment import XmippMovieAlignViewer
from viewer_resolution3d import XmippResolution3DViewer
from viewer_validate_nontilt import XmippValidateNonTiltViewer

#from viewer_reconstruct_significant import XmippReconstructSignificantViewer
# TODO(coss): add viewer_reconstruct_significant.py pretty please

from plotter import XmippPlotter

from protocol_align_volume import XmippProtAlignVolume, XmippProtAlignVolumeForWeb
from protocol_apply_alignment import XmippProtApplyAlignment
from protocol_break_symmetry import XmippProtAngBreakSymmetry
from protocol_cl2d_align import XmippProtCL2DAlign
from protocol_cl2d import XmippProtCL2D
from protocol_cltomo import XmippProtCLTomo
# from protocol_ctf_defocus_group import XmippProtCTFDefocusGroup
from protocol_ctf_discrepancy import XmippProtCTFDiscrepancy
from protocol_ctf_micrographs import XmippProtCTFMicrographs
from protocol_denoise_particles import XmippProtDenoiseParticles
from protocol_extract_particles import XmippProtExtractParticles
from protocol_extract_particles_movies import XmippProtExtractMovieParticles
from protocol_extract_particles_pairs import XmippProtExtractParticlesPairs
from protocol_helical_parameters import XmippProtHelicalParameters
from protocol_kerdensom import XmippProtKerdensom
from protocol_ml2d import XmippProtML2D
from protocol_movie_alignment import ProtMovieAlignment, ProtMovieAlignment
from protocol_particle_pick_automatic import XmippParticlePickingAutomatic
from protocol_particle_pick_consensus import XmippProtConsensusPicking
from protocol_particle_pick import XmippProtParticlePicking 
from protocol_particle_pick_pairs import XmippProtParticlePickingPairs
from protocol_preprocess_micrographs import XmippProtPreprocessMicrographs
from protocol_projection_outliers import XmippProtProjectionOutliers
from protocol_projmatch import XmippProtProjMatch, XmippProjMatchViewer
from protocol_random_conical_tilt import XmippProtRCT
from protocol_ransac import XmippProtRansac
from protocol_reconstruct_fourier import XmippProtReconstructFourier
from protocol_reconstruct_highres import XmippProtReconstructHighRes
from protocol_reconstruct_significant import XmippProtReconstructSignificant
from protocol_resolution3d import XmippProtResolution3D
from protocol_rotational_spectra import XmippProtRotSpectra 
from protocol_screen_classes import XmippProtScreenClasses
from protocol_screen_particles import XmippProtScreenParticles
from protocol_validate_nontilt import XmippProtValidateNonTilt

# Wizards
from wizard import *

_environ = getEnviron()
