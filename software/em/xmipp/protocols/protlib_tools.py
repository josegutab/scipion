#!/usr/bin/env python
'''
#/***************************************************************************
# * Authors:     J.M. de la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *              Joaquin Oton Perez (joton@cnb.csic.es)
# *
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
# *  e-mail address 'xmipp@cnb.csic.es'
# ***************************************************************************
'''
 
 # This lib is to gather a set of tools based on xmipp library functions 

from xmipp import *

def scaleVolume(scale, inputVol, outputVol):
    ''' This function scale a volume and sets 
        the information of the header file acording to the new scale '''
    
    img = Image()
    img.read(inputVol, DATA_ALL)
    
    dim = img.getDimensions()
    
    ndim = [int(e * scale) for e in dim]
    rscale = [ float(nd) / d for nd,d in zip(ndim, dim)]
    
    for i, label in enumerate([MDL_SAMPLINGRATE_X, MDL_SAMPLINGRATE_Y, MDL_SAMPLINGRATE_Z]):
       img.setMainHeaderValue(label, img.getMainHeaderValue(label) / rscale[i])
       
    for i, label in enumerate([MDL_ORIGIN_X, MDL_ORIGIN_Y, MDL_ORIGIN_Z]):
       img.setHeaderValue(label, img.getHeaderValue(label) * rscale[i])
       
    for i, label in enumerate([MDL_SHIFT_X, MDL_SHIFT_Y, MDL_SHIFT_Z]):
       img.setHeaderValue(label, img.getHeaderValue(label) * rscale[i])
    
    img.scale(*ndim[:-1])
    img.write(outputVol)
