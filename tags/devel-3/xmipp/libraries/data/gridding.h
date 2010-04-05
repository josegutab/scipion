/***************************************************************************
 *
 * Authors: Sjors H.W. Scheres (scheres@cnb.csic.es)
 *
 *  Part of this code is strongly based on ideas by Pawel Penczek & Zhengfan
 *  Yang as implemented in SPARX at the University of Texas - Houston 
 *  Medical School
 *
 *  see P. A. Penczek, R. Renka, and H. Schomberg,
 *      J. Opt. Soc. Am. _21_, 449 (2004)
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/
#ifndef GRIDDING_H
#define GRIDDING_H
#include "funcs.h"
#include "multidimensional_array.h"
#include "fft.h"

#define GRIDDING_ALPHA 1.75
#define GRIDDING_NPAD 2
#define GRIDDING_K 6

/// @defgroup Gridding Gridding
/// @ingroup DataLibrary

/// @defgroup ReverseGridding Reverse Gridding
/// @ingroup Gridding

// ***************************************************************************
// ************************ Reverse Gridding *********************************
// ***************************************************************************

/** Produce a complex MultidimArray for reverse gridding from a complex MultidimArray
 * @ingroup ReverseGridding
 *
 *  Produces a Fourier-space MultidimArray for reverse-gridding
 *  interpolation from a Fourier-space MultidimArray 
 */
void produceReverseGriddingFourierMatrix(MultidimArray< std::complex < double > > &in, 
                                         MultidimArray< std::complex < double > > &out,
                                         KaiserBessel &kb);

/** Produce a complex MultidimArray for reverse gridding from a real Matrix2D
 * @ingroup ReverseGridding
 *
 *  Produces a Fourier-space MultidimArray for reverse-gridding
 *  interpolation from a real-space MultidimArray 
 *  This real-space MultidimArray should have the Xmipp origin set!
 */
void produceReverseGriddingFourierMatrix(const MultidimArray< double > &in, 
                                         MultidimArray< std::complex< double > > &out,
                                         KaiserBessel &kb);

/** Produce a real MultidimArray for reverse gridding from a real Matrix2D
 * @ingroup ReverseGridding
 *
 *  Produces a real-space MultidimArray for reverse-gridding
 *  interpolation from a real-space MultidimArray
 */
void produceReverseGriddingMatrix(const MultidimArray< double > &in, 
                                  MultidimArray< double > &out,
                                  KaiserBessel &kb);

/** Reverse-gridding based interpolationin a MultidimArray
 * @ingroup ReverseGridding
 *
 * Interpolates the value of the MultidimArray M at the point (x,y,z) knowing
 * that this image has been processed for reverse-gridding
 *
 * (x,y,z) are in logical coordinates (note that n is supposed to be one)
 *
 * To interpolate using gridding you must prepare the image first!
 * An example to interpolate an image at (0.5,0.5) using
 * gridding would be:
 *
 * @code
 * KaiserBessel kb;
 * matrix2D<double> Maux;
 * produceReverseGriddingMatrix(img(),Maux,kb);
 * interpolated_value = interpolatedElementReverseGridding2D(Maux,0.5,0.5,kb);
 * @endcode
 */
template <typename T>
T interpolatedElementReverseGridding2D(const MultidimArray<T> &in, double x, double y, const KaiserBessel &kb)
{
    // size of this image:
    int nx = XSIZE(in);
    int ny = YSIZE(in);
    
    // Go from logical to physical coordinates in the small image
    x -= FIRST_XMIPP_INDEX(nx/GRIDDING_NPAD);
    y -= FIRST_XMIPP_INDEX(ny/GRIDDING_NPAD);
    
    // Get the convolution window parameters
    int K = kb.get_window_size();
    int kbmin = -K/2;
    int kbmax = -kbmin;
    int kbc = kbmax+1;
    T pixel = 0.;
    double w = 0.;
    
    x = fmod(2*x, double(nx));
    y = fmod(2*y, double(ny));
    int inxold = int(ROUND(x));
    int inyold = int(ROUND(y));
    
    double tablex1 = kb.i0win_tab(x-inxold+3);
    double tablex2 = kb.i0win_tab(x-inxold+2);
    double tablex3 = kb.i0win_tab(x-inxold+1);
    double tablex4 = kb.i0win_tab(x-inxold);
    double tablex5 = kb.i0win_tab(x-inxold-1);
    double tablex6 = kb.i0win_tab(x-inxold-2);
    double tablex7 = kb.i0win_tab(x-inxold-3);

    double tabley1 = kb.i0win_tab(y-inyold+3);
    double tabley2 = kb.i0win_tab(y-inyold+2);
    double tabley3 = kb.i0win_tab(y-inyold+1);
    double tabley4 = kb.i0win_tab(y-inyold);
    double tabley5 = kb.i0win_tab(y-inyold-1);
    double tabley6 = kb.i0win_tab(y-inyold-2);
    double tabley7 = kb.i0win_tab(y-inyold-3); 
	
    int x1, x2, x3, x4, x5, x6, x7, y1, y2, y3, y4, y5, y6, y7;
	
    if ( inxold <= kbc || inxold >=nx-kbc-2 || 
	 inyold <= kbc || inyold >=ny-kbc-2 )  {
	x1 = (inxold-3)%nx;
	x2 = (inxold-2)%nx;
	x3 = (inxold-1)%nx;
	x4 = (inxold  )%nx;
	x5 = (inxold+1)%nx;
	x6 = (inxold+2)%nx;
	x7 = (inxold+3)%nx;

	y1 = ((inyold-3)%ny);
	y2 = ((inyold-2)%ny);
	y3 = ((inyold-1)%ny);
	y4 = ((inyold  )%ny);
	y5 = ((inyold+1)%ny);
	y6 = ((inyold+2)%ny);
	y7 = ((inyold+3)%ny);
    } else {
	x1 = inxold-3;
	x2 = inxold-2;
	x3 = inxold-1;
	x4 = inxold;
	x5 = inxold+1;
	x6 = inxold+2;
	x7 = inxold+3;

	y1 = inyold-3;
	y2 = inyold-2;
	y3 = inyold-1;
	y4 = inyold;
	y5 = inyold+1;
	y6 = inyold+2;
	y7 = inyold+3;
    }
    
    // The actual convolution
    pixel = ( DIRECT_MAT_ELEM(in,y1,x1)*tablex1 +
              DIRECT_MAT_ELEM(in,y1,x2)*tablex2 + 
              DIRECT_MAT_ELEM(in,y1,x3)*tablex3 +
	      DIRECT_MAT_ELEM(in,y1,x4)*tablex4 +
              DIRECT_MAT_ELEM(in,y1,x5)*tablex5 +
              DIRECT_MAT_ELEM(in,y1,x6)*tablex6 +
	      DIRECT_MAT_ELEM(in,y1,x7)*tablex7 ) * tabley1 +

            ( DIRECT_MAT_ELEM(in,y2,x1)*tablex1 +
              DIRECT_MAT_ELEM(in,y2,x2)*tablex2 + 
              DIRECT_MAT_ELEM(in,y2,x3)*tablex3 +
	      DIRECT_MAT_ELEM(in,y2,x4)*tablex4 +
              DIRECT_MAT_ELEM(in,y2,x5)*tablex5 +
              DIRECT_MAT_ELEM(in,y2,x6)*tablex6 +
	      DIRECT_MAT_ELEM(in,y2,x7)*tablex7 ) * tabley2 +

            ( DIRECT_MAT_ELEM(in,y3,x1)*tablex1 +
              DIRECT_MAT_ELEM(in,y3,x2)*tablex2 + 
              DIRECT_MAT_ELEM(in,y3,x3)*tablex3 +
	      DIRECT_MAT_ELEM(in,y3,x4)*tablex4 +
              DIRECT_MAT_ELEM(in,y3,x5)*tablex5 +
              DIRECT_MAT_ELEM(in,y3,x6)*tablex6 +
	      DIRECT_MAT_ELEM(in,y3,x7)*tablex7 ) * tabley3 +

            ( DIRECT_MAT_ELEM(in,y4,x1)*tablex1 +
              DIRECT_MAT_ELEM(in,y4,x2)*tablex2 + 
              DIRECT_MAT_ELEM(in,y4,x3)*tablex3 +
	      DIRECT_MAT_ELEM(in,y4,x4)*tablex4 +
              DIRECT_MAT_ELEM(in,y4,x5)*tablex5 +
              DIRECT_MAT_ELEM(in,y4,x6)*tablex6 +
	      DIRECT_MAT_ELEM(in,y4,x7)*tablex7 ) * tabley4 +

            ( DIRECT_MAT_ELEM(in,y5,x1)*tablex1 +
              DIRECT_MAT_ELEM(in,y5,x2)*tablex2 + 
              DIRECT_MAT_ELEM(in,y5,x3)*tablex3 +
	      DIRECT_MAT_ELEM(in,y5,x4)*tablex4 +
              DIRECT_MAT_ELEM(in,y5,x5)*tablex5 +
              DIRECT_MAT_ELEM(in,y5,x6)*tablex6 +
	      DIRECT_MAT_ELEM(in,y5,x7)*tablex7 ) * tabley5 +

            ( DIRECT_MAT_ELEM(in,y6,x1)*tablex1 +
              DIRECT_MAT_ELEM(in,y6,x2)*tablex2 + 
              DIRECT_MAT_ELEM(in,y6,x3)*tablex3 +
	      DIRECT_MAT_ELEM(in,y6,x4)*tablex4 +
              DIRECT_MAT_ELEM(in,y6,x5)*tablex5 +
              DIRECT_MAT_ELEM(in,y6,x6)*tablex6 +
	      DIRECT_MAT_ELEM(in,y6,x7)*tablex7 ) * tabley6 +

            ( DIRECT_MAT_ELEM(in,y7,x1)*tablex1 +
              DIRECT_MAT_ELEM(in,y7,x2)*tablex2 + 
              DIRECT_MAT_ELEM(in,y7,x3)*tablex3 +
	      DIRECT_MAT_ELEM(in,y7,x4)*tablex4 +
              DIRECT_MAT_ELEM(in,y7,x5)*tablex5 +
              DIRECT_MAT_ELEM(in,y7,x6)*tablex6 +
	      DIRECT_MAT_ELEM(in,y7,x7)*tablex7 ) * tabley7;
    
    w = (tablex1+tablex2+tablex3+tablex4+tablex5+tablex6+tablex7) *
	(tabley1+tabley2+tabley3+tabley4+tabley5+tabley6+tabley7);	
    
    return pixel/w;

}

/** Reverse-gridding based interpolation in a 3D matrix
 * @ingroup ReverseGridding
 *
 * Interpolates the value of the 3D matrix M at the point (x,y,z) knowing
 * that this matrix has been processed for reverse-gridding
 *
 * (x,y,z) are in logical coordinates
 *
 * To interpolate using gridding you must prepare the matrix first!
 * An example to interpolate an image at (0.5,0.5,0.5) using
 * gridding would be:
 *
 * @code
 * KaiserBessel kb;
 * MultidimArray<double> Maux;
 * produceReverseGriddingMatrix3D(vol(),Maux,kb);
 * interpolated_value = interpolatedElementReverseGridding3D(Maux,0.5,0.5,0.5,kb);
 * @endcode
 */
template <typename T>
T interpolatedElementReverseGridding3D(MultidimArray<T> &in, double x, double y, double z, const KaiserBessel &kb)
{
    // size of this image:
    int nx = XSIZE(in);
    int ny = YSIZE(in);
    int nz = ZSIZE(in);
    
    // Go from logical to physical coordinates in the small image
    x -= FIRST_XMIPP_INDEX(nx/GRIDDING_NPAD);
    y -= FIRST_XMIPP_INDEX(ny/GRIDDING_NPAD);
    z -= FIRST_XMIPP_INDEX(nz/GRIDDING_NPAD);
    
    // Get the convolution window parameters
    int K = kb.get_window_size();
    int kbmin = -K/2;
    int kbmax = -kbmin;
    int kbc = kbmax+1;
    double pixel =0.;
    double w=0.;
    
    x = fmod(2*x, double(nx));
    y = fmod(2*y, double(ny));
    z = fmod(2*z, double(nz));
    int inxold = int(ROUND(x));
    int inyold = int(ROUND(y));
    int inzold = int(ROUND(z));
    
    double tablex1 = kb.i0win_tab(x-inxold+3);
    double tablex2 = kb.i0win_tab(x-inxold+2);
    double tablex3 = kb.i0win_tab(x-inxold+1);
    double tablex4 = kb.i0win_tab(x-inxold);
    double tablex5 = kb.i0win_tab(x-inxold-1);
    double tablex6 = kb.i0win_tab(x-inxold-2);
    double tablex7 = kb.i0win_tab(x-inxold-3);

    double tabley1 = kb.i0win_tab(y-inyold+3);
    double tabley2 = kb.i0win_tab(y-inyold+2);
    double tabley3 = kb.i0win_tab(y-inyold+1);
    double tabley4 = kb.i0win_tab(y-inyold);
    double tabley5 = kb.i0win_tab(y-inyold-1);
    double tabley6 = kb.i0win_tab(y-inyold-2);
    double tabley7 = kb.i0win_tab(y-inyold-3); 
	
    double tablez1 = kb.i0win_tab(z-inzold+3);
    double tablez2 = kb.i0win_tab(z-inzold+2);
    double tablez3 = kb.i0win_tab(z-inzold+1);
    double tablez4 = kb.i0win_tab(z-inzold);
    double tablez5 = kb.i0win_tab(z-inzold-1);
    double tablez6 = kb.i0win_tab(z-inzold-2);
    double tablez7 = kb.i0win_tab(z-inzold-3); 

    int x1, x2, x3, x4, x5, x6, x7, y1, y2, y3, y4, y5, y6, y7, z1, z2, z3, z4, z5, z6, z7;
	
    if ( inxold <= kbc || inxold >=nx-kbc-2 || 
	 inyold <= kbc || inyold >=ny-kbc-2 || 
	 inzold <= kbc || inzold >= nz-kbc-2 )  {
	x1 = (inxold-3)%nx;
	x2 = (inxold-2)%nx;
	x3 = (inxold-1)%nx;
	x4 = (inxold  )%nx;
	x5 = (inxold+1)%nx;
	x6 = (inxold+2)%nx;
	x7 = (inxold+3)%nx;

	y1 = ((inyold-3)%ny);
	y2 = ((inyold-2)%ny);
	y3 = ((inyold-1)%ny);
	y4 = ((inyold  )%ny);
	y5 = ((inyold+1)%ny);
	y6 = ((inyold+2)%ny);
	y7 = ((inyold+3)%ny);

	z1 = ((inzold-3)%nz);
	z2 = ((inzold-2)%nz);
	z3 = ((inzold-1)%nz);
	z4 = ((inzold  )%nz);
	z5 = ((inzold+1)%nz);
	z6 = ((inzold+2)%nz);
	z7 = ((inzold+3)%nz);
    } else {
	x1 = inxold-3;
	x2 = inxold-2;
	x3 = inxold-1;
	x4 = inxold;
	x5 = inxold+1;
	x6 = inxold+2;
	x7 = inxold+3;

	y1 = inyold-3;
	y2 = inyold-2;
	y3 = inyold-1;
	y4 = inyold;
	y5 = inyold+1;
	y6 = inyold+2;
	y7 = inyold+3;

	z1 = inzold-3;
	z2 = inzold-2;
	z3 = inzold-1;
	z4 = inzold;
	z5 = inzold+1;
	z6 = inzold+2;          
	z7 = inzold+3;
    }
    
    // The actual convolution
    // COSS: This is a bad idea
    pixel =(( DIRECT_VOL_ELEM(in,z1,y1,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z1,y1,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z1,y1,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z1,y1,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z1,y1,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z1,y1,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z1,y1,x7)*tablex7 ) * tabley1 +
            ( DIRECT_VOL_ELEM(in,z1,y2,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z1,y2,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z1,y2,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z1,y2,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z1,y2,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z1,y2,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z1,y2,x7)*tablex7 ) * tabley2 +
            ( DIRECT_VOL_ELEM(in,z1,y3,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z1,y3,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z1,y3,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z1,y3,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z1,y3,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z1,y3,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z1,y3,x7)*tablex7 ) * tabley3 +
            ( DIRECT_VOL_ELEM(in,z1,y4,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z1,y4,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z1,y4,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z1,y4,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z1,y4,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z1,y4,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z1,y4,x7)*tablex7 ) * tabley4 +
            ( DIRECT_VOL_ELEM(in,z1,y5,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z1,y5,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z1,y5,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z1,y5,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z1,y5,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z1,y5,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z1,y5,x7)*tablex7 ) * tabley5 +
            ( DIRECT_VOL_ELEM(in,z1,y6,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z1,y6,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z1,y6,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z1,y6,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z1,y6,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z1,y6,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z1,y6,x7)*tablex7 ) * tabley6 +
            ( DIRECT_VOL_ELEM(in,z1,y7,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z1,y7,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z1,y7,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z1,y7,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z1,y7,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z1,y7,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z1,y7,x7)*tablex7 ) * tabley7 ) * tablez1 +

           (( DIRECT_VOL_ELEM(in,z2,y1,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z2,y1,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z2,y1,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z2,y1,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z2,y1,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z2,y1,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z2,y1,x7)*tablex7 ) * tabley1 +
            ( DIRECT_VOL_ELEM(in,z2,y2,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z2,y2,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z2,y2,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z2,y2,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z2,y2,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z2,y2,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z2,y2,x7)*tablex7 ) * tabley2 +
            ( DIRECT_VOL_ELEM(in,z2,y3,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z2,y3,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z2,y3,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z2,y3,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z2,y3,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z2,y3,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z2,y3,x7)*tablex7 ) * tabley3 +
            ( DIRECT_VOL_ELEM(in,z2,y4,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z2,y4,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z2,y4,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z2,y4,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z2,y4,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z2,y4,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z2,y4,x7)*tablex7 ) * tabley4 +
            ( DIRECT_VOL_ELEM(in,z2,y5,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z2,y5,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z2,y5,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z2,y5,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z2,y5,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z2,y5,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z2,y5,x7)*tablex7 ) * tabley5 +
            ( DIRECT_VOL_ELEM(in,z2,y6,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z2,y6,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z2,y6,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z2,y6,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z2,y6,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z2,y6,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z2,y6,x7)*tablex7 ) * tabley6 +
            ( DIRECT_VOL_ELEM(in,z2,y7,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z2,y7,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z2,y7,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z2,y7,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z2,y7,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z2,y7,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z2,y7,x7)*tablex7 ) * tabley7 ) * tablez2 +

           (( DIRECT_VOL_ELEM(in,z3,y1,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z3,y1,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z3,y1,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z3,y1,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z3,y1,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z3,y1,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z3,y1,x7)*tablex7 ) * tabley1 +
            ( DIRECT_VOL_ELEM(in,z3,y2,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z3,y2,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z3,y2,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z3,y2,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z3,y2,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z3,y2,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z3,y2,x7)*tablex7 ) * tabley2 +
            ( DIRECT_VOL_ELEM(in,z3,y3,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z3,y3,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z3,y3,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z3,y3,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z3,y3,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z3,y3,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z3,y3,x7)*tablex7 ) * tabley3 +
            ( DIRECT_VOL_ELEM(in,z3,y4,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z3,y4,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z3,y4,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z3,y4,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z3,y4,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z3,y4,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z3,y4,x7)*tablex7 ) * tabley4 +
            ( DIRECT_VOL_ELEM(in,z3,y5,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z3,y5,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z3,y5,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z3,y5,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z3,y5,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z3,y5,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z3,y5,x7)*tablex7 ) * tabley5 +
            ( DIRECT_VOL_ELEM(in,z3,y6,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z3,y6,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z3,y6,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z3,y6,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z3,y6,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z3,y6,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z3,y6,x7)*tablex7 ) * tabley6 +
            ( DIRECT_VOL_ELEM(in,z3,y7,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z3,y7,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z3,y7,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z3,y7,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z3,y7,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z3,y7,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z3,y7,x7)*tablex7 ) * tabley7 ) * tablez3 +

           (( DIRECT_VOL_ELEM(in,z4,y1,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z4,y1,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z4,y1,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z4,y1,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z4,y1,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z4,y1,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z4,y1,x7)*tablex7 ) * tabley1 +
            ( DIRECT_VOL_ELEM(in,z4,y2,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z4,y2,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z4,y2,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z4,y2,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z4,y2,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z4,y2,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z4,y2,x7)*tablex7 ) * tabley2 +
            ( DIRECT_VOL_ELEM(in,z4,y3,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z4,y3,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z4,y3,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z4,y3,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z4,y3,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z4,y3,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z4,y3,x7)*tablex7 ) * tabley3 +
            ( DIRECT_VOL_ELEM(in,z4,y4,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z4,y4,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z4,y4,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z4,y4,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z4,y4,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z4,y4,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z4,y4,x7)*tablex7 ) * tabley4 +
            ( DIRECT_VOL_ELEM(in,z4,y5,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z4,y5,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z4,y5,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z4,y5,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z4,y5,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z4,y5,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z4,y5,x7)*tablex7 ) * tabley5 +
            ( DIRECT_VOL_ELEM(in,z4,y6,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z4,y6,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z4,y6,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z4,y6,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z4,y6,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z4,y6,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z4,y6,x7)*tablex7 ) * tabley6 +
            ( DIRECT_VOL_ELEM(in,z4,y7,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z4,y7,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z4,y7,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z4,y7,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z4,y7,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z4,y7,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z4,y7,x7)*tablex7 ) * tabley7 ) * tablez4 +

           (( DIRECT_VOL_ELEM(in,z5,y1,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z5,y1,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z5,y1,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z5,y1,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z5,y1,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z5,y1,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z5,y1,x7)*tablex7 ) * tabley1 +
            ( DIRECT_VOL_ELEM(in,z5,y2,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z5,y2,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z5,y2,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z5,y2,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z5,y2,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z5,y2,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z5,y2,x7)*tablex7 ) * tabley2 +
            ( DIRECT_VOL_ELEM(in,z5,y3,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z5,y3,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z5,y3,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z5,y3,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z5,y3,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z5,y3,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z5,y3,x7)*tablex7 ) * tabley3 +
            ( DIRECT_VOL_ELEM(in,z5,y4,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z5,y4,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z5,y4,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z5,y4,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z5,y4,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z5,y4,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z5,y4,x7)*tablex7 ) * tabley4 +
            ( DIRECT_VOL_ELEM(in,z5,y5,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z5,y5,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z5,y5,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z5,y5,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z5,y5,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z5,y5,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z5,y5,x7)*tablex7 ) * tabley5 +
            ( DIRECT_VOL_ELEM(in,z5,y6,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z5,y6,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z5,y6,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z5,y6,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z5,y6,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z5,y6,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z5,y6,x7)*tablex7 ) * tabley6 +
            ( DIRECT_VOL_ELEM(in,z5,y7,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z5,y7,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z5,y7,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z5,y7,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z5,y7,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z5,y7,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z5,y7,x7)*tablex7 ) * tabley7 ) * tablez5 +

           (( DIRECT_VOL_ELEM(in,z6,y1,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z6,y1,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z6,y1,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z6,y1,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z6,y1,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z6,y1,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z6,y1,x7)*tablex7 ) * tabley1 +
            ( DIRECT_VOL_ELEM(in,z6,y2,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z6,y2,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z6,y2,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z6,y2,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z6,y2,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z6,y2,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z6,y2,x7)*tablex7 ) * tabley2 +
            ( DIRECT_VOL_ELEM(in,z6,y3,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z6,y3,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z6,y3,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z6,y3,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z6,y3,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z6,y3,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z6,y3,x7)*tablex7 ) * tabley3 +
            ( DIRECT_VOL_ELEM(in,z6,y4,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z6,y4,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z6,y4,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z6,y4,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z6,y4,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z6,y4,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z6,y4,x7)*tablex7 ) * tabley4 +
            ( DIRECT_VOL_ELEM(in,z6,y5,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z6,y5,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z6,y5,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z6,y5,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z6,y5,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z6,y5,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z6,y5,x7)*tablex7 ) * tabley5 +
            ( DIRECT_VOL_ELEM(in,z6,y6,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z6,y6,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z6,y6,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z6,y6,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z6,y6,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z6,y6,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z6,y6,x7)*tablex7 ) * tabley6 +
            ( DIRECT_VOL_ELEM(in,z6,y7,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z6,y7,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z6,y7,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z6,y7,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z6,y7,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z6,y7,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z6,y7,x7)*tablex7 ) * tabley7 ) * tablez6 +

           (( DIRECT_VOL_ELEM(in,z7,y1,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z7,y1,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z7,y1,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z7,y1,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z7,y1,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z7,y1,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z7,y1,x7)*tablex7 ) * tabley1 +
            ( DIRECT_VOL_ELEM(in,z7,y2,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z7,y2,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z7,y2,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z7,y2,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z7,y2,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z7,y2,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z7,y2,x7)*tablex7 ) * tabley2 +
            ( DIRECT_VOL_ELEM(in,z7,y3,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z7,y3,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z7,y3,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z7,y3,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z7,y3,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z7,y3,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z7,y3,x7)*tablex7 ) * tabley3 +
            ( DIRECT_VOL_ELEM(in,z7,y4,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z7,y4,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z7,y4,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z7,y4,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z7,y4,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z7,y4,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z7,y4,x7)*tablex7 ) * tabley4 +
            ( DIRECT_VOL_ELEM(in,z7,y5,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z7,y5,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z7,y5,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z7,y5,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z7,y5,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z7,y5,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z7,y5,x7)*tablex7 ) * tabley5 +
            ( DIRECT_VOL_ELEM(in,z7,y6,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z7,y6,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z7,y6,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z7,y6,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z7,y6,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z7,y6,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z7,y6,x7)*tablex7 ) * tabley6 +
            ( DIRECT_VOL_ELEM(in,z7,y7,x1)*tablex1 +
              DIRECT_VOL_ELEM(in,z7,y7,x2)*tablex2 + 
              DIRECT_VOL_ELEM(in,z7,y7,x3)*tablex3 +
	      DIRECT_VOL_ELEM(in,z7,y7,x4)*tablex4 +
              DIRECT_VOL_ELEM(in,z7,y7,x5)*tablex5 +
              DIRECT_VOL_ELEM(in,z7,y7,x6)*tablex6 +
	      DIRECT_VOL_ELEM(in,z7,y7,x7)*tablex7 ) * tabley7 ) * tablez7;

    w = (tablex1+tablex2+tablex3+tablex4+tablex5+tablex6+tablex7) *
	(tabley1+tabley2+tabley3+tabley4+tabley5+tabley6+tabley7) *
	(tablez1+tablez2+tablez3+tablez4+tablez5+tablez6+tablez7);	
    
    return pixel/w;

}

/// @defgroup ReverseGriddingRelated Reverse Gridding Related Functions
/// @ingroup ReverseGridding

/** Reverse-gridding based 2D projection operation
 * @ingroup ReverseGriddingRelated
 *
 * Extracts a plane from a volume using reverse-gridding interpolation,
 * knowing that this volume has been processed for gridding.
 *
 * rot, tilt and psi and the respective Euler angles
 *
 * To interpolate using gridding you must prepare the volume first!
 * An example to extract a Fourier-plane, i.e. to calculate a
 * real-space projection, would be:
 *
 * @code
 * KaiserBessel kb;
 * MultidimArray<std::complex<double> > Faux;
 * TODO!!!!
 * @endcode
 */


/** Reverse-gridding based geometric transformation on a 2D matrix
 * @ingroup ReverseGriddingRelated
 *
 * Applies a geometric transformation to a 2D matrix with
 * reverse-gridding-based interpolation, knowing that this image has been
 * processed for gridding.
 *
 * A is a 3x3 transformation matrix.
 *
 * Note that the output dimensions should be given if a different
 * scale is to be applied.
 *
 * To interpolate using gridding you must prepare the image first!
 * An example to apply a gridding-based transformation would be:
 *
 * @code
 * KaiserBessel kb;
 * matrix2D<double> Maux,out;
 * produceReverseGriddingMatrix(img(),Maux,kb);
 * Matrix2D<double> A = rotation2DMatrix(63.1);
 * applyGeometryReverseGridding(out,A,Maux,IS_NOT_INV,DONT_WRAP,kb);
 * @endcode
 */
template<typename T>
void applyGeometryReverseGridding2D(MultidimArray<T> &M2, 
                                    const MultidimArray<T> &M1, 
                                    Matrix2D< double > A, 
                                    const KaiserBessel &kb, bool inv, bool wrap, 
                                    int nx = 0, int ny = 0, T outside = (T) 0)
{
    int m1, n1, m2, n2;
    double x, y, xp, yp;
    double minxp, minyp, maxxp, maxyp;
    int cen_x, cen_y;

    if ((XSIZE(A) != 3) || (YSIZE(A) != 3))
        REPORT_ERROR(1102, "Apply_geom: geometrical transformation is not 3x3");

    if (XSIZE(M1) == 0)
    {
        M2.clear();
        return;
    }

    // For scalings the output matrix is explicitly resized to the final size 
    // Otherwise, just take half the size of the gridding image
    if (nx == 0) 
	nx = XSIZE(M1) / GRIDDING_NPAD;
    if (ny == 0) 
	ny = XSIZE(M1) / GRIDDING_NPAD;
    M2.resize(ny, nx);
    M2.setXmippOrigin();

    if (!inv)
        A = A.inv();

    // Find center and limits of image
    cen_y  = (int)(YSIZE(M2) / 2);
    cen_x  = (int)(XSIZE(M2) / 2);
    // Take 2x oversize M1 dims into account for calculating the limits 
    minxp  = FIRST_XMIPP_INDEX(XSIZE(M1)/2);
    minyp  = FIRST_XMIPP_INDEX(YSIZE(M1)/2);
    maxxp  = LAST_XMIPP_INDEX(XSIZE(M1)/2);
    maxyp  = LAST_XMIPP_INDEX(YSIZE(M1)/2);

    // Now we go from the output image to the input image, ie, for any pixel
    // in the output image we calculate which are the corresponding ones in
    // the original image, make an interpolation with them and put this value
    // at the output pixel
    for (int i = 0; i < YSIZE(M2); i++)
    {
        // Calculate position of the beginning of the row in the output image
        x = -cen_x;
        y = i - cen_y;

        // Calculate this position in the input image according to the
        // geometrical transformation
        // they are related by
        // coords_output(=x,y) = A * coords_input (=xp,yp)
        xp = x * dMij(A, 0, 0) + y * dMij(A, 0, 1) + dMij(A, 0, 2);
        yp = x * dMij(A, 1, 0) + y * dMij(A, 1, 1) + dMij(A, 1, 2);

        for (int j = 0; j < XSIZE(M2); j++)
        {
            bool interp;

            // If the point is outside the image, apply a periodic extension
            // of the image, what exits by one side enters by the other
            interp = true;

            if (wrap)
            {
                if (xp < minxp - XMIPP_EQUAL_ACCURACY ||
                    xp > maxxp + XMIPP_EQUAL_ACCURACY)
                    xp = realWRAP(xp, minxp - 0.5, maxxp + 0.5);

                if (yp < minyp - XMIPP_EQUAL_ACCURACY ||
                    yp > maxyp + XMIPP_EQUAL_ACCURACY)
                    yp = realWRAP(yp, minyp - 0.5, maxyp + 0.5);
            }
            else
            {
                if (xp < minxp - XMIPP_EQUAL_ACCURACY ||
                    xp > maxxp + XMIPP_EQUAL_ACCURACY)
                    interp = false;

                if (yp < minyp - XMIPP_EQUAL_ACCURACY ||
                    yp > maxyp + XMIPP_EQUAL_ACCURACY)
                    interp = false;
            }

            if (interp)
                dMij(M2, i, j) = interpolatedElementReverseGridding2D(M1,xp,yp,kb);
	    else
		dMij(M2, i, j) = outside;

          // Compute new point inside input image
            xp += dMij(A, 0, 0);
            yp += dMij(A, 1, 0);
        }
    }
}

/** Reverse-gridding based geometric transformation on a 3D matrix
 * @ingroup ReverseGriddingRelated
 *
 * Applies a geometric transformation to a 3D matrix with
 * reverse-gridding-based interpolation, knowing that this image has been
 * processed for gridding.
 *
 * A is a 3x3 transformation matrix.
 *
 * To interpolate using gridding you must prepare the MultidimArray first!
 * An example to apply a gridding-based transformation would be:
 *
 * @code
 * KaiserBessel kb;
 * MultidimArray<double> Maux,out;
 * produceReverseGriddingMatrix(vol(),Maux,kb);
 * Matrix2D<double> A = rotation2DMatrix(63.1);
 * applyGeometryReverseGridding3D(out,A,Maux,IS_NOT_INV,DONT_WRAP,kb);
 * @endcode
 */
template<typename T>
void applyGeometryReverseGridding3D(MultidimArray<T> &V2,
                                    const MultidimArray<T> &V1,  
                                    Matrix2D< double > A, 
                                    const KaiserBessel &kb, 
                                    bool inv, bool wrap, 
                                    int nx = 0, int ny = 0, int nz = 0, T outside = (T) 0)
{
    int m1, n1, o1, m2, n2, o2;
    double x, y, z, xp, yp, zp;
    double minxp, minyp, maxxp, maxyp, minzp, maxzp;
    int   cen_x, cen_y, cen_z;

    if ((XSIZE(A) != 4) || (YSIZE(A) != 4))
        REPORT_ERROR(1102, "Apply_geom3D: geometrical transformation is not 4x4");

    if (XSIZE(V1) == 0)
    {
        V2.clear();
        return;
    }

    // For scalings the output matrix is explicitly resized to the final size 
    // Otherwise, just take half the size of the gridding image
    if (nx == 0) 
	nx = XSIZE(V1) / GRIDDING_NPAD;
    if (ny == 0) 
	ny = XSIZE(V1) / GRIDDING_NPAD;
    if (nz == 0) 
	nz = ZSIZE(V1) / GRIDDING_NPAD;
    V2.resize(nz, ny, nx);
    V2.setXmippOrigin();

    if (!inv)
        A = A.inv();

    // Find center of MultidimArray
    cen_z = (int)(V2.zdim / 2);
    cen_y = (int)(V2.ydim / 2);
    cen_x = (int)(V2.xdim / 2);
    // Take 2x oversize M1 dims into account for calculating the limits 
    minxp  = FIRST_XMIPP_INDEX(XSIZE(V1)/2);
    minyp  = FIRST_XMIPP_INDEX(YSIZE(V1)/2);
    minzp  = FIRST_XMIPP_INDEX(ZSIZE(V1)/2);
    maxxp  = LAST_XMIPP_INDEX(XSIZE(V1)/2);
    maxyp  = LAST_XMIPP_INDEX(YSIZE(V1)/2);
    maxzp  = LAST_XMIPP_INDEX(ZSIZE(V1)/2);

    // Now we go from the output MultidimArray to the input MultidimArray, ie, for any
    // voxel in the output MultidimArray we calculate which are the corresponding
    // ones in the original MultidimArray, make an interpolation with them and put
    // this value at the output voxel

    // V2 is not initialised to 0 because all its pixels are rewritten
    for (int k = 0; k < V2.zdim; k++)
        for (int i = 0; i < V2.ydim; i++)
        {
            // Calculate position of the beginning of the row in the output
            // MultidimArray
            x = -cen_x;
            y = i - cen_y;
            z = k - cen_z;

            // Calculate this position in the input image according to the
            // geometrical transformation they are related by
            // coords_output(=x,y) = A * coords_input (=xp,yp)
            xp = x * dMij(A, 0, 0) + y * dMij(A, 0, 1) + z * dMij(A, 0, 2)
                 + dMij(A, 0, 3);
            yp = x * dMij(A, 1, 0) + y * dMij(A, 1, 1) + z * dMij(A, 1, 2)
                 + dMij(A, 1, 3);
            zp = x * dMij(A, 2, 0) + y * dMij(A, 2, 1) + z * dMij(A, 2, 2)
                 + dMij(A, 2, 3);

            for (int j = 0; j < V2.xdim; j++)
            {
                bool interp;

                // If the point is outside the volume, apply a periodic
                // extension of the volume, what exits by one side enters by
                // the other
                interp = true;
                if (wrap)
                {
                    if (xp < minxp - XMIPP_EQUAL_ACCURACY ||
                        xp > maxxp + XMIPP_EQUAL_ACCURACY)
                        xp = realWRAP(xp, minxp - 0.5, maxxp + 0.5);

                    if (yp < minyp - XMIPP_EQUAL_ACCURACY ||
                        yp > maxyp + XMIPP_EQUAL_ACCURACY)
                        yp = realWRAP(yp, minyp - 0.5, maxyp + 0.5);

                    if (zp < minzp - XMIPP_EQUAL_ACCURACY ||
                        zp > maxzp + XMIPP_EQUAL_ACCURACY)
                        zp = realWRAP(zp, minzp - 0.5, maxzp + 0.5);
                }
                else
                {
                    if (xp < minxp - XMIPP_EQUAL_ACCURACY ||
                        xp > maxxp + XMIPP_EQUAL_ACCURACY)
                        interp = false;

                    if (yp < minyp - XMIPP_EQUAL_ACCURACY ||
                        yp > maxyp + XMIPP_EQUAL_ACCURACY)
                        interp = false;

                    if (zp < minzp - XMIPP_EQUAL_ACCURACY ||
                        zp > maxzp + XMIPP_EQUAL_ACCURACY)
                        interp = false;
                }

                if (interp)
                    dVkij(V2, k, i, j) = (T) interpolatedElementReverseGridding3D(V1,xp,yp,zp,kb);
                else
                    dVkij(V2, k, i, j) = outside;

                // Compute new point inside input image
                xp += dMij(A, 0, 0);
                yp += dMij(A, 1, 0);
                zp += dMij(A, 2, 0);
            }
        }
}

/// @defgroup ForwardGridding Forward Gridding
/// @ingroup Gridding

// ***************************************************************************
// ************************ Reverse Gridding *********************************
// ***************************************************************************

/** Numerically approximate the voronoi area for a set of 2D points
 * @ingroup ForwardGridding
 *
 *  Calculate the Voronoi area for a set of 2D points. The borders are
 *  set to a rectangle from min_x,min_y to max_x, max_y.
 *  Therefore, border effects should be taken care of in the
 *  generation of the x and y coordinates
 *
 */
void approximateVoronoiArea(std::vector<double> &voronoi_area,
			    const std::vector<double> &xin,
                            const std::vector<double> &yin, 
			    const double oversample = 10.);

/** Interpolate Cartesian coordinates from any irregularly sampled grid
 * @ingroup ForwardGridding
 *
 *  Interpolate Cartesian coordinates from an arbitrarily sampled grid
 *  using (forward) gridding. Note that the voronoi areas of the
 *  irregularly sampled coordinates have to be provided, and that the
 *  output of this routine needs to be passed through
 *  produceForwardGriddingMatrix2D or produceForwardGriddingFourierMatrix2D!
 *  The dimensions of the resulting matrix should be given.
 *
 * @code
 * KaiserBessel kb;
 * std::vector<double> x,y,data,voronoi_area;
 * MultidimArray<double> Maux;
 *
 * P.getCartesianCoordinates(x,y,data); // (P is a Polar<double>)
 * approximateVoronoiArea(voronoi_area,x,y);
 * Maux = interpolateCartesianFromArbitrarySampling(64,64,x,y,data,voronoi_area,kb);
 * produceForwardGriddingMatrix2D(Maux,Maux2,kb);
 * @endcode
 *
 */
template <typename T>
MultidimArray<T> interpolateCartesianFromArbitrarySampling(const int xdim, const int ydim,
                                                           const std::vector<double> &xin, 
                                                           const std::vector<double> &yin,
                                                           const std::vector<T> &data, 
                                                           const std::vector<double> &voronoi_area,
                                                           const KaiserBessel &kb)
{

    double wx,wy, xx, yy, dx, dy, r, w, sumw;
    MultidimAaray<T> result;

    // Oversample result GRIDDING_NPAD times
    result.initZeros(GRIDDING_NPAD*xdim, GRIDDING_NPAD*ydim);
    result.setXmippOrigin();
    
    // 1. Convolution interpolation
    // Loop over all cartesian coordinates: add all sampled points
    // within the window in x or y to the result, multiplied with the
    // corresponding gridding weights
    double window_size = (double)(kb.get_window_size()/2);
    FOR_ALL_ELEMENTS_IN_MATRIX2D(result)
    {
	xx = (double) j;
	yy = (double) i;
	sumw = 0.;
	for (int ii = 0; ii < xin.size(); ii++)
	{
	    dx = GRIDDING_NPAD*xin[ii] - xx;
	    if (ABS(dx) < window_size)
	    { 		
		dy = GRIDDING_NPAD*yin[ii] - yy;
		if (ABS(dy) < window_size)
		{
		    // Gridding weight
		    w = voronoi_area[ii] * kb.i0win_tab(dx) *  kb.i0win_tab(dy);
		    MAT_ELEM(result,i,j) += data[ii] * w;
		    sumw += w;
		}
	    }
	}
	if (sumw > 0.) 
	    MAT_ELEM(result,i,j) /= sumw;
    }

    return result;

}

/** Finish forward gridding after interpolateCartesianFromArbitrarySampling
 * @ingroup ForwardGridding
 *
 *  Produces a real-space MultidimArray after having performed 
 *  interpolateCartesianFromArbitrarySampling for real-space coordinates.
 */
void produceForwardGriddingMatrix(const MultidimArray< double > &in, 
                                  MultidimArray< double > &out,
                                  KaiserBessel &kb);

/** Finish forward gridding after interpolateCartesianFromArbitrarySampling
 * @ingroup ForwardGridding
 *
 *  Produces a real-space MultidimArray after having performed
 *  interpolateCartesianFromArbitrarySampling for fourier-space coordinates.
 */
void produceForwardGriddingMatrix(const MultidimArray< std::complex<double > > &in, 
                                  MultidimArray< double > &out,
                                  KaiserBessel &kb,
                                  bool is_centered = true);

/** Finish forward gridding after interpolateCartesianFromArbitrarySampling
 * @ingroup ForwardGridding
 *
 *  Produces a 2D fourier-space MultidimArray after having performed
 *  interpolateCartesianFromArbitrarySampling for fourier-space coordinates.
 */
void produceForwardGriddingFourierMatrix(const MultidimArray< std::complex<double > > &in, 
                                         MultidimArray< std::complex<double > > &out,
                                         KaiserBessel &kb,
                                         bool is_centered = true);


#endif
