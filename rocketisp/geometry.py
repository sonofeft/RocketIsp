from math import pi, sqrt, cos, sin, tan, radians
from rocketisp.nozzle.nozzle import Nozzle


def solidCylVol( D, L ):
    '''calculates a cylinder volume'''
    return D**2 * pi * L / 4.0
        
def solidFrustrumVol(  D1, D2, h ):
    '''calculates cone frustrum'''
    r1 = D1/2.0
    r2 = D2/2.0
    V = pi*h*(r1**2 + r1*r2 + r2**2)/3.0
    return  V


class Geometry:
    """
    The Geometry object holds all the major thrust chamber geometry values.

    :param Rthrt: in, throat radius
    :param CR: chamber contraction ratio (Ainj / Athroat)
    :param eps: nozzle area ratio (Aexit / Athroat)
    :param pcentBell: nozzle percent bell (Lnoz / L_15deg_cone)
    :param LnozInp: in, user input nozzle length (will override pcentBell)
    :param RupThroat: radius of curvature just upstream of throat (Rupstream / Rthrt)
    :param RdwnThroat: radius of curvature just downstream of throat (Rdownstream / Rthrt)
    :param RchmConv: radius of curvature at start of convergent section (Rconv / Rthrt)
    :param cham_conv_deg: deg, half angle of conical convergent section
    :param LchmOvrDt: ratio of chamber length to throat diameter (Lcham / Dthrt)
    :param LchmMin: in, minimum chamber length (will override LchmOvrDt)
    :param LchamberInp: in, user input value of chamber length (will override all other entries)
    :type Rthrt: float
    :type CR: float
    :type eps: float
    :type pcentBell: float
    :type LnozInp: float
    :type RupThroat: float
    :type RdwnThroat: float
    :type RchmConv: float
    :type cham_conv_deg: float
    :type LchmOvrDt: float
    :type LchmMin: float
    :type LchamberInp: float
    :return: Geometry object
    :rtype: Geometry        
    """
    def __init__(self,  Rthrt=1,
                 CR=2.5, eps=20,  pcentBell=80, LnozInp=None,
                 RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                 LchmOvrDt=3.0, LchmMin=1.0, LchamberInp=None):
        """
        Initialize thrust chamber geometry
        """
        
        
        self.Rthrt         = Rthrt
        self.CR            = CR
        self.eps           = eps
        self.pcentBell     = pcentBell
        self.LnozInp       = LnozInp
        self.RupThroat     = RupThroat
        self.RdwnThroat    = RdwnThroat
        self.RchmConv      = RchmConv
        self.cham_conv_deg = cham_conv_deg
        self.cham_conv_rad  = radians( cham_conv_deg )
        self.LchmOvrDt     = LchmOvrDt
        self.LchmMin       = LchmMin
        self.LchamberInp   = LchamberInp
        
        self.nozObj        = None # only instantiated if needed.
        
        self.evaluate()
        
    def reset_attr(self, name, value, re_evaluate=True):
        """Resets Geometry object attribute by name if that attribute already exists."""
        if hasattr( self, name ):
            setattr( self, name, value )
        else:
            raise Exception('Attempting to set un-authorized Geometry attribute named "%s"'%name )
            
        if re_evaluate:
            self.evaluate()
        
    def __call__(self, name):
        return getattr(self, name ) # let it raise exception if no name attr.
        
    def evaluate(self):
        """
        Uses basic geometry input values to determine derived geometry values.
        (for example, throat area, nozzle length, injector area, etc.)
        """
        self.At = pi * self.Rthrt**2
        
        z100 = self.Rthrt * ( sqrt(self.eps) - 1.0 ) / tan( radians(15.) )
        if self.LnozInp is None:
            # calc nozzle length
            self.Lnoz = z100 * self.pcentBell / 100.0
        else:
            # calc nozzle pcentBell
            self.Lnoz = self.LnozInp
            self.pcentBell = 100.0 * self.LnozInp / z100
            
        
        self.Rexit = self.Rthrt * sqrt( self.eps )
        
        # calc injector area
        self.Ainj = self.At * self.CR
        self.Rinj = self.Rthrt * sqrt( self.CR )
        self.Dinj = self.Rinj * 2.0
        if self.LchamberInp is None:
            self.Lcham = max( self.LchmMin, self.LchmOvrDt * self.Rthrt * 2.0 )
            if self.Lcham == self.LchmMin:
                self.Lcham_desc = '(user minimum allowed Lcham)'
            else:
                self.Lcham_desc = '(set by user Lcham/Dt = %g)'%self.LchmOvrDt
        else:
            self.Lcham = self.LchamberInp
            self.Lcham_desc = '(user input)'

        self.calc_convergent_section() # may reset Lcham to longer value
        
        self.Ltotal = self.Lcham + self.Lnoz

        # estimate chamber volume with simple cylinder and frustrum
        Vcyl  = solidCylVol( self.Dinj, self.Lcham_cyl )
        Vconv = solidFrustrumVol(  self.Dinj, self.Rthrt*2.0, self.Lcham_conv )
        self.Vcham = Vcyl + Vconv
        
    
    def LprimeOvRcham(self):
        """return chamber length / chamber radius"""
        return self.Lcham / self.Rinj
    
    def getNozObj( self ):
        """Create and return a Nozzle object."""
        if self.nozObj is not None:
            return self.nozObj
        
        noz = Nozzle(CR=self.CR, eps=self.eps, pcentBell=self.pcentBell,
                     Rt=self.Rthrt,  Nsegs=30,  
                     Rup=self.RupThroat, Rd=self.RdwnThroat, 
                     cham_conv_ang=self.cham_conv_deg, Rc=self.RchmConv,
                     theta=None, exitAng=None, forceCone=0, use_huzel_angles=False)
        self.nozObj = noz
        return noz
    
    def plot_geometry(self, title='Geometry', png_name='', do_show=True, show_grid=True):
        import matplotlib.pyplot as plt
        noz = self.getNozObj()
        
        zL = [-self.Lcham] + noz.abs_zContour
        rL = [self.Dinj/2.0] + noz.abs_rContour
        
        zL = list(reversed(zL)) + zL
        rL = list(reversed(rL)) + [-r for r in rL]
        
        fig = plt.figure()
        ax = plt.axes()
        ax.set_aspect('equal')
        ax.set_ylim( (-round(noz.abs_rContour[-1]+1), round(noz.abs_rContour[-1]+1)) )
        #ax.tick_params(axis='y', colors='red')
        #ax.yaxis.label.set_color('red')
        plt.plot( zL, rL, '-k' )
        if show_grid:
            plt.grid()
        plt.ylabel( 'Radius (in)' )
        plt.xlabel( 'Axial Position (in)' )
        plt.title( title )
        fig.tight_layout()
        
        if png_name:
            if not png_name.endswith('.png'):
                png_name = png_name + '.png'
            plt.savefig( png_name )
        
        if do_show:
            plt.show()
    
    
    def calc_convergent_section(self):
        Rt   = 1.0 # dimensionless calcs
        Rchm = Rt * sqrt(self.CR) # dimensionless calcs
        cosA = cos( self.cham_conv_rad )
        sinA = sin( self.cham_conv_rad )
        tanA = tan( self.cham_conv_rad )
        
        htSeg = Rchm - self.RupThroat*(1.0-cosA) - self.RchmConv*(1.0-cosA) - Rt # ht of linear segment
        if htSeg < 0.0:
            # radii are too big for CR... reduce radii or inc CR
            print('='*30, ' ERROR ','='*30)
            print('              Error in Convergent Section... ')
            print('      Rup, Rchm, CR, cham_conv_deg are INCONSISTENT !!!')
            print('      (i.e. conical convergent section has length < 0)')
            print('     decrease (Rup, Rchm) or increase (CR, cham_conv_deg)')
            print('='*30, ' ERROR ','='*30)
            raise Exception( 'Geometry Error... RI, RWTU and THETAI are INCONSISTENT' )
            
            
        wdSeg = htSeg / tanA
        
        zstart_conv = -( (self.RchmConv + self.RupThroat) * sinA + wdSeg )
        zstart_conv *= self.Rthrt # convert back to inches.
                
        self.Lcham_conv = abs( zstart_conv )
        self.Lcham_cyl = self.Lcham - self.Lcham_conv
        if self.Lcham_cyl < 0.0:
            self.Lcham_cyl = 0.0
            self.Lcham = self.Lcham_conv
            self.Lcham_desc = '(convergent section limited)'
        
    def summ_print(self):
        """
        print to standard output, the current state of Geometry instance.
        """
        def maybe_show_ft( val ):
            if val > 12.0:
                ft = int( val / 12 )
                i = val - ft*12.0
                s = ' (%g ft %.3f in)'%(ft, i  )
            else:
                s = ''
            return s
            
        
        print('---------------geometry-----------------------')
        print('        Rthrt =', '%.3f'%self.Rthrt, 'in (Dthrt=%.3f in)'%(self.Rthrt*2))
        print('         Rinj =', '%.3f'%self.Rinj, 'in (Dinj=%.3f in)'%(self.Rinj*2))
        print('        Rexit =', '%.3f'%self.Rexit, 'in (Dexit=%.3f in)'%(self.Rexit*2))
        print('           At =', '%g'%self.At, 'in**2')
        print('          eps =', '%g'%self.eps, '')
        
        if self.LnozInp is None:
            print('    pcentBell =', '%g'%self.pcentBell, '%')
        else:
            print('    pcentBell =', '%g'%self.pcentBell, '%%, calculated from Lnoz=%g in'%self.LnozInp)
            
        print('           CR =', '%g'%self.CR, 'injector area / throat area')
        print('         Dinj =', '%g'%self.Dinj, 'in', maybe_show_ft( self.Dinj ))
        print('         Ainj =', '%g'%self.Ainj, 'in**2')
        print(' cham_conv_deg=', '%g'%self.cham_conv_deg, 'deg convergent section half angle' )
        
        noz = self.getNozObj()
        print('entrance_angle=', '%g'%noz.theta, 'deg nozzle initial expansion angle' )
        print('    exit_angle=', '%g'%noz.exitAng, 'deg nozzle exit angle' )
                    
        print('        Lcham =', '%g'%self.Lcham, 'in',self.Lcham_desc, maybe_show_ft( self.Lcham ))
        print('    Lcham_cyl =', '%g'%self.Lcham_cyl, 'in', maybe_show_ft( self.Lcham_cyl ))
        print('   Lcham_conv =', '%g'%self.Lcham_conv, 'in', maybe_show_ft( self.Lcham_conv ))
        
        print('       Ltotal =', '%g'%self.Ltotal, 'in', maybe_show_ft( self.Ltotal ))
        
        if self.LnozInp is None:
            print('         Lnoz =', '%g'%self.Lnoz, 'in', maybe_show_ft( self.Lnoz ))
        else:
            print('         Lnoz =', '%g'%self.Lnoz, 'in, set by user with LnozInp', maybe_show_ft( self.Lnoz ))
        
        
        print('     RchmConv =', '%g'%self.RchmConv, 'convergent section turn radius / throat radius')
        print('    RupThroat =', '%g'%self.RupThroat, 'upstream radius / throat radius')
        print('   RdwnThroat =', '%g'%self.RdwnThroat, 'downstream radius / throat radius')
        print('    LchmOvrDt =', '%g'%self.LchmOvrDt, 'chamber length / throat diameter')
        print('      LchmMin =', '%g'%self.LchmMin, 'in, minimum allowed chamber length')
        print('        Vcham =', '%g'%self.Vcham, 'in**3, approximate chamber volume')
        
        
        
if __name__ == '__main__':
    import sys
    do_show = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'suppress_show':
            do_show = False

    geom = Geometry(Rthrt=1.5,
                    CR=2.5, eps=20,  pcentBell=80, 
                    RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                    LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
    geom.summ_print()
    geom.plot_geometry( png_name='geometry.png', do_show=do_show, show_grid=False )
