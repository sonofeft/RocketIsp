from math import *
from rocketcea.biprop_utils.InterpProp_scipy import InterpProp
from rocketisp.nozzle.six_opt_parab import getOptEntranceExitAngles
from rocketisp.nozzle.huzel_data import getHuzelEntranceExitAngles

class Nozzle:
    """
    Nozzle contour object holds both a dimensionless and absolute dimension 
    representation of the nozzle.
    It includes interpolators for entire contour.

    :param CR: contraction ratio of chamber (Ainj / Athroat)
    :param eps: nozzle area ratio (Aexit / Athroat)
    :param pcentBell: nozzle percent bell (Lnoz / L_15deg_cone)
    :param Rt: in, throat radius
    :param Nsegs: number of segments to hold in array of nozzle contour
    :param Rup: radius of curvature just upstream of throat (Rupstream / Rthroat)
    :param Rd: radius of curvature just downstream of throat (Rdownstream / Rthroat)
    :param cham_conv_ang: deg, half angle of convergent section of chamber
    :param Rc: radius of curvature at start of convergent section (Rconvergent / Rthroat)
    :param theta: deg, entrance angle of nozzle (tangent to Rd circular curve)
    :param exitAng: deg, exit angle of nozzle
    :param forceCone: flag to force nozzle to be a conical nozzle instead of bell nozzle.
    :param use_huzel_angles: flag to force use of Huzel entrance and exit angle correlation
    :type CR: float
    :type eps: float
    :type pcentBell: float
    :type Rt: float
    :type Nsegs: int
    :type Rup: float
    :type Rd: float
    :type cham_conv_ang: float
    :type Rc: float
    :type theta: float
    :type exitAng: float
    :type forceCone: bool
    :type use_huzel_angles: bool
    :return: Nozzle object
    :rtype: Nozzle    
    """
    
    def __init__(self, CR=2.5, eps=16., pcentBell=80.0,
                 Rt=1.5,  Nsegs=20,  
                 Rup=2.0, Rd=1.0, cham_conv_ang=30.0, Rc=1.0,
                 theta=None, exitAng=None, forceCone=0, use_huzel_angles=False):
                     
        if eps <= 1.00001:
            eps = 1.00001
        
        self.Rd = Rd  # Rd is dimensionless (i.e. Rd/Rt)
        self.Rup = Rup # also dimensionless (Rup/Rt)
        self.cham_conv_ang = cham_conv_ang # chamber convergence angle
        self.eps = eps
        self.pcentBell = pcentBell
        self.CR        = CR
        
        self.Nsegs = Nsegs
        
        if theta is None or exitAng is None:
            if use_huzel_angles:
                self.theta, self.exitAng = getHuzelEntranceExitAngles(eps=eps, pcBell=pcentBell)
            else:
                self.theta, self.exitAng = getOptEntranceExitAngles(eps=eps, pcentBell=pcentBell)
        else:
            self.theta   = theta # entrance angle of skewed parabola
            self.exitAng = exitAng # exit angle of skewed parabola
        
        self.forceCone = forceCone # force contour to be conical
        
        # contour is dimensionless... r=r/Rt,  z=z/Rt
        self.zContour,self.rContour,self.imaCone,self.angCone,self.i_throat = \
            ref_nozzle( Rup=Rup,  Rd=Rd, eps=eps, theta=self.theta, 
            alphaExit=self.exitAng, pcBell=pcentBell, Nsegs=self.Nsegs, 
            cham_conv_ang=cham_conv_ang, Rc=Rc, CR=CR,
            forceCone=forceCone )

        self.set_abs_Rt( Rt )
        
    def set_abs_Rt(self, Rt ):
        """Use throat radius to create an absolute contour from the dimensionless contour."""
        
        self.Rt = Rt
        self.zExit = self.zContour[-1] * Rt # absolute units
        self.rExit = self.rContour[-1] * Rt
        self.At    = pi * Rt**2
        
        self.Acham = self.At * self.CR
        self.Rcham = sqrt( self.Acham / pi )
                
        # make a z and r contour in absolute unites (scaled by Rt)
        self.abs_zContour = [z*Rt for z in self.zContour]
        self.abs_rContour = [r*Rt for r in self.rContour]
        # ............. create interpolators for nozzle contour .........
        self.epsContour = [r**2 for r in self.rContour]
        
        # make contour interpolators
        #  ...NOTE... Z,R and area are in ABSOLUTE  UNITS .....
        self.z2r_terp    = InterpProp( self.abs_zContour, self.abs_rContour )
        self.z2area_terp    = InterpProp( self.abs_zContour, [pi*r**2 for r in self.abs_rContour] )
        
        # NOTICE sqrt of eps for interpolators
        self.z2_eps_terp  = InterpProp( self.abs_zContour, self.epsContour )
        self.z2_logeps_terp  = InterpProp( self.abs_zContour, [log(e) for e in self.epsContour] )
        #self.z2_logarea_terp = InterpProp( self.abs_zContour, [log(self.At*e) for e in self.epsContour] )
        
        # NOTICE sqrt of eps for interpolators
        # make interpolators for convergent and divergent sections of nozzle
        self.conv_logeps2z_terp = InterpProp( [log(e) for e in self.epsContour[:self.i_throat+1]],  
                                              self.abs_zContour[:self.i_throat+1], extrapOK=False )
        self.div_logeps2z_terp  = InterpProp( [log(e) for e in self.epsContour[self.i_throat:]],    
                                              self.abs_zContour[self.i_throat:], extrapOK=False )
    
    def get_eps_from_z(self, z):
        # interpolation can fall below 1.0 if not careful
        return max(1.0, self.z2_eps_terp( z ))
        
    def get_area_from_z(self, z):
        return self.z2area_terp( z )
        
    def get_dadz_from_z(self, z):
        return self.z2area_terp.deriv( z )
    
    def get_conv_zL_epsL(self):
        """
        Returns 2 lists for the convergent contour, 
        the z contour and the area ratio contour starting at 
        the injector and going to the throat, but
        NOT including Throat
        """
        return self.abs_zContour[:self.i_throat], self.epsContour[:self.i_throat]
    
    def get_div_zL_epsL(self):
        """
        Returns 2 lists for the divergent nozzle contour, 
        the z contour and the area ratio contour starting at 
        the throat and going to the nozzle exit, but
        NOT including Throat
        """
        return self.abs_zContour[self.i_throat+1:], self.epsContour[self.i_throat+1:]
    
    def get_z_from_div_eps(self, eps):
        log_eps = log(eps)
        return self.div_logeps2z_terp( log_eps )
    
    def get_z_from_conv_eps(self, eps):
        log_eps = log(eps)
        return self.conv_logeps2z_terp( log_eps )
    
    def get_z_from_eps_for_gas(self, gas, eps):
        if gas.M <= 1.0:
            return self.get_z_from_conv_eps( eps )
        else:
            return self.get_z_from_div_eps( eps )
    
    def z_min(self):
        return self.abs_zContour[0]
        
    def z_max(self):
        return self.abs_zContour[-1]
    
    def z_range(self):
        """return (zmin, zmax)"""
        return self.abs_zContour[0], self.abs_zContour[-1]
        
    def plot_geom(self, do_show=True, save_to_png=False, Lchamber=None):
        import matplotlib.pyplot as plt
        
        if self.imaCone:
            title = "Absolute Dimension Conical Contour\n(eps=%g, %%Bell=%g, ConeAng=%.1f deg)"%\
                   ( self.eps, self.pcentBell, self.angCone)
        else:
            title = "Absolute Dimension Parabolic Contour\n(eps=%g, %%Bell=%g, entAng=%.1f deg, exitAng=%.1f deg)"%\
                   ( self.eps, self.pcentBell, self.theta, self.exitAng)
                   
        if Lchamber is None:
            zL =  self.abs_zContour
            rL =  self.abs_rContour
            eL =  self.epsContour
        else:
            zL = [-Lchamber] + self.abs_zContour
            rL = [self.Rcham] + self.abs_rContour
            eL = [self.CR] + self.epsContour


        fig = plt.figure()
        ax = plt.axes()
        ax.set_aspect('equal')
        ax.set_ylim( (0, round(self.abs_rContour[-1]+1)) )
        ax.tick_params(axis='y', colors='red')
        ax.yaxis.label.set_color('red')
        plt.plot( zL, rL, '-r.', label='Radius' )
        plt.grid()
        plt.legend(loc='upper left')
        plt.ylabel( 'Nozzle Radius (len units)' )
        plt.xlabel( 'Nozzle Axial Position (len units)' )
        
        ax2=ax.twinx()
        ax2.set_aspect('auto')
        ax2.tick_params(axis='y', colors='green')
        ax2.yaxis.label.set_color('green')
        ax2.set_ylim( (0, round(self.epsContour[-1]+1) ) )
        ax2.plot( zL, eL, '-g.', label='Area Ratio' )
        ax2.set_ylabel("Area Ratio")

        plt.title( title )

        plt.legend(loc='lower right')
        fig.tight_layout()

        if save_to_png:
            plt.savefig( 'nozzle_geom.png' )
        if do_show:
            plt.show()

        

def sinDeg( ang ):
    return sin( ang*pi/180.0 )

def cosDeg( ang ):
    return cos( ang*pi/180.0 )

def tanDeg( ang ):
    return tan( ang*pi/180.0 )

def bell_net_halfAngle( Rd=1.0, eps=16., pcBell=80., theta=30. ):
    Rt=1.0  # ONLY allow dimensionless contour

    if eps <= 1.00001:
        eps = 1.00001
        
        
    zT = Rd * sinDeg(theta)
    rT = Rt + Rd*(1.-cosDeg(theta))

    z100 = Rt * ( sqrt(eps) - 1.0 ) / tanDeg(15.)
    zE = z100 * pcBell / 100.0
    rE = Rt * sqrt(eps)
    
    angCone = atan( (rE-rT)/(zE-zT) ) * 180.0 / pi
    return angCone

def ref_nozzle( Rup=2.0,  Rd=1.0, eps=16., theta=30., 
    alphaExit=10., pcBell=80., Nsegs=30, forceCone=0, 
    cham_conv_ang=30.0, Rc=1.0, CR=2.5 ):
    '''DIMENSIONLESS Parabolic Nozzle Contour (Rthroat = 1.0)'''
    
    Rt=1.0  # ONLY allow dimensionless contour

    if eps <= 1.00001:
        eps = 1.00001
        
        
    zT = Rd * sinDeg(theta)
    rT = Rt + Rd*(1.-cosDeg(theta))

    z100 = Rt * ( sqrt(eps) - 1.0 ) / tanDeg(15.)
    zE = z100 * pcBell / 100.0
    rE = Rt * sqrt(eps)
    
    angCone = atan( (rE-rT)/(zE-zT) ) * 180.0 / pi
    
    
    if theta>angCone and theta>alphaExit and not forceCone:
        zQ = (rE + zT*tanDeg(theta) - rT - zE*tanDeg(alphaExit)) / \
             (tanDeg(theta)-tanDeg(alphaExit))
        rQ = rT + (zQ-zT)*tanDeg(theta)
        imaCone = 0
    else: # can't make a parabola, so make a cone
        angConeMin = atan( (rE-Rt)/zE ) * 180.0 / pi # solve for cone angle
        angConeMax = atan( rE/zE ) * 180.0 / pi
        for i in range(20):
            angCone = (angConeMin + angConeMax) / 2.0
            zT = Rd * sinDeg(angCone)
            rT = Rt + Rd*(1.-cosDeg(angCone))
            angConeTest = atan( (rE-rT)/(zE-zT) ) * 180.0 / pi
            if angConeTest<angCone:
                angConeMax = angCone
            else:
                angConeMin = angCone
            zQ = zT + (zE-zT)/2.
            rQ = rT + (rE-rT)/2.
        imaCone = 1

    
    z1L = []
    r1L = []
    z2L = []
    r2L = []
    NsegP1 = Nsegs+1
    for i in range(1, NsegP1):
        z1L.append( zT + float(i) * (zQ-zT) / NsegP1 )
        r1L.append( rT + float(i) * (rQ-rT) / NsegP1 )
        z2L.append( zQ + float(i) * (zE-zQ) / NsegP1 )
        r2L.append( rQ + float(i) * (rE-rQ) / NsegP1 )

    # ......... start countour at tangent point (zT, rT) .........
    rContour = [rT]
    zContour = [zT]
            
    # this approach is more efficient, than the obvious, brute-force approach.
    #    (see parabola_v1.py for brute-force approach)
    # ...works for both parabola and cone using (z1L, r1L, z2L, r2L)
    for i in range(Nsegs):
        rContour.append( r1L[i] + float(i+1) * (r2L[i]-r1L[i]) / NsegP1 )
        zContour.append( z1L[i] + float(i+1) * (z2L[i]-z1L[i]) / NsegP1 )
    
    # append portion past tangent point (zT, rT)
    rContour.append( rE )
    zContour.append( zE )


    # ........ set integer angle steps .........
    idang = int(5)

    # ........ create convergent section .........
    Rchm = Rt * sqrt(CR)
    cosA = cosDeg( cham_conv_ang )
    sinA = sinDeg(cham_conv_ang)
    tanA = tanDeg(cham_conv_ang)
    
    htSeg = Rchm - Rup*(1.0-cosA) - Rc*(1.0-cosA) - Rt # ht of linear segment
    if htSeg < 0.0:
        # radii are too big for CR... reduce radii
        htSeg = 0.1 * (Rchm - Rt) # let linear segment be 10% of ht 
        
        hr = 0.9 * (Rchm - Rt) / 2.0 # make radii equal
        Rup = hr / (1.0-cosA)
        Rc  = Rup
        
    htSeg = Rchm - Rup*(1.0-cosA) - Rc*(1.0-cosA) - Rt # ht of linear segment
    wdSeg = htSeg / tanA
    
    zstart_conv = -( (Rc + Rup) * sinA + wdSeg )
    zconvL = []
    rconvL = []
    
    ang = 0
    while ang < cham_conv_ang-1:
        zconvL.append( zstart_conv + Rc*sinDeg(ang) )
        rconvL.append( Rchm - Rc*(1.-cosDeg(ang)) )
        ang += idang

    zconvL.append( zstart_conv + Rc*sinDeg(cham_conv_ang) )
    rconvL.append( Rchm - Rc*(1.-cosDeg(cham_conv_ang)) )
    
    # make a short linear section
    zconvL.append( zconvL[-1] + wdSeg/2.0 )
    rconvL.append( rconvL[-1] - htSeg/2.0 )

    #print( 'zconvL:', zconvL)
    #print( 'rconvL:', rconvL)

    # ......... create throat section (Rup and Rd) .........
    zthrtL = []
    rthrtL = []
    if imaCone:
        throat_angle = angCone
    else:
        throat_angle = theta
        
    angStart = -cham_conv_ang
    angL = [angStart]
    iang = round( angStart )
    if abs( iang - angStart ) < float(idang) / 2.0:
        iang += idang
    angL.extend( [i for i in range(iang, 0, idang) ] ) # note zero is omitted
    for ang in angL:
        zthrtL.append( Rup*sinDeg(ang)*Rt )
        rthrtL.append( (1.0 + Rup*(1.-cosDeg(ang)))*Rt )

    i_throat = len( zthrtL ) + len(zconvL) # save index of throat position
    # start at throat
    ang = 0.0
    while ang<throat_angle: # omit tangent point. (i.e. use "<" instead of "<=")
        zthrtL.append( Rd*sinDeg(ang)*Rt )
        rthrtL.append( (1.0 + Rd*(1.-cosDeg(ang)))*Rt )
        ang += idang

    #print( '\nzthrtL:', zthrtL)
    #print( 'rthrtL:', rthrtL)

    # ......... connect all the pieces .........
    rContour = rconvL + rthrtL + rContour
    zContour = zconvL + zthrtL + zContour
    
    #print( 'i_throat=%i,  R at i_throat=%g'%(i_throat, rContour[i_throat]) )
    for i in range(1, i_throat+1):
        if rContour[i-1] <= rContour[i]:
            print( 'R out of sequence at i=%i, R[i-1]=%g, R[i]=%g '%(i,rContour[i-1], rContour[i] ))
            
        if zContour[i-1] >= zContour[i]:
            print( 'Z out of sequence at i=%i, Z[i-1]=%g, Z[i]=%g '%(i,zContour[i-1], zContour[i] ))
    
    for i in range(i_throat+1, len(rContour)):
        if rContour[i-1] >= rContour[i]:
            print( 'R out of sequence at i=%i, R[i-1]=%g, R[i]=%g '%(i,rContour[i-1], rContour[i] ))
            
        if zContour[i-1] >= zContour[i]:
            print( 'Z out of sequence at i=%i, Z[i-1]=%g, Z[i]=%g '%(i,zContour[i-1], zContour[i] ))
    
    
    return zContour,rContour,imaCone,angCone,i_throat
       

if __name__ == "__main__": #Self Test
    
    noz = Nozzle(CR=2.5, eps=60.0, pcentBell=80.0,
                 Rt=2.54,  Nsegs=20,  
                 Rup=2.0, Rd=1.0, cham_conv_ang=30.0, Rc=1.0,
                 theta=None, exitAng=None, forceCone=0, use_huzel_angles=False)
                 
    noz.plot_geom( do_show=True, save_to_png=True )
    