
from math import pi, sqrt, cos, sin, tan, radians
from rocketisp.nozzle.nozzle import Nozzle
from rocketisp.model_summ import ModelSummary
from rocketisp.parse_docstring import get_desc_and_units

def solidCylVol( D, L ):
    '''calculates a cylinder volume'''
    return D**2 * pi * L / 4.0
        
def solidFrustrumVol(  D1, D2, h ):
    '''calculates cone frustrum'''
    r1 = D1/2.0
    r2 = D2/2.0
    V = pi*h*(r1**2 + r1*r2 + r2**2)/3.0
    return  V
    
def maybe_show_ft( val ):
    """If input inches > 12, return string with feet units."""
    if val > 12.0:
        ft = int( val / 12 )
        i = val - ft*12.0
        s = ' (%g ft %.3f in)'%(ft, i  )
    else:
        s = ''
    return s


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

    :ivar At: in**2, throat area
    :ivar Lnoz: in, nozzle length
    :ivar Ltotal: in, nozzle + chamber length
    :ivar Rinj: in, radius of injector
    :ivar Dinj: in, diameter of injector
    :ivar Ainj: in**2, area of injector
    :ivar Lcham_cyl: in, length of cylindrical section of chamber
    :ivar Lcham_conv: in, length of convergent section of chamber
    :ivar Vcham: in**3, approximate chamber volume
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
        
        # get input descriptions and units from doc string
        self.inp_descD, self.inp_unitsD, self.is_inputD = get_desc_and_units( self.__doc__ )
        
        self.evaluate()
        
    def reset_attr(self, name, value, re_evaluate=True):
        """Resets Geometry object attribute by name if that attribute already exists."""
        if hasattr( self, name ):
            setattr( self, name, value )
            self.nozObj = None # may need to reevalute nozzle contour
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
            self.LchmOvrDt = self.Lcham / (self.Rthrt * 2.0)

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
    
    def plot_geometry(self, title='Geometry', png_name='', pixel_wh=None,
                      do_show=True, show_grid=True, make_vertical=False):
        import matplotlib.pyplot as plt
        noz = self.getNozObj()
        
        zL = [-self.Lcham] + noz.abs_zContour
        rL = [self.Dinj/2.0] + noz.abs_rContour
        
        zL = list(reversed(zL)) + zL
        rL = list(reversed(rL)) + [-r for r in rL]
        
        if pixel_wh is None:
            fig, ax = plt.subplots(nrows=1, ncols=1)
        else:
            w,h = pixel_wh
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(w/100.0, h/100.0), dpi=100)
        
        ax.set_aspect('equal')
        
        if make_vertical:
            zL = [ -(z+self.Lcham) for z in zL ]
            min_z = min(zL)
            zL = [z-min_z for z in zL]
            ax.set_xlim( (-round(noz.abs_rContour[-1]+1), round(noz.abs_rContour[-1]+1)) )
            plt.plot( rL, zL, '-k' )
            plt.xlabel( 'Radius (in)' )
            plt.ylabel( 'Axial Position (in)' )
        else:
            ax.set_ylim( (-round(noz.abs_rContour[-1]+1), round(noz.abs_rContour[-1]+1)) )
            plt.plot( zL, rL, '-k' )
            plt.ylabel( 'Radius (in)' )
            plt.xlabel( 'Axial Position (in)' )
            
        if show_grid:
            plt.grid()
        plt.title( title )
        fig.tight_layout()
        
        if png_name:
            if not png_name.endswith('.png'):
                png_name = png_name + '.png'
            plt.savefig( png_name )
        
        if do_show:
            plt.show()
            
        return plt
    
    
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
    
    def get_attr_comment(self, name):
        """Some attributes may have comments associated with them"""
        
        if name=='Lnoz' and self.LnozInp is not None:
            return 'set by user with LnozInp'
        
        if name=='pcentBell' and self.LnozInp is not None:
            return 'calculated from Lnoz=%g in'%self.LnozInp
        
        # if no comment, return empty string
        return ''
    
    def summ_print(self):
        """
        print to standard output, the current state of Geometry instance.
        """
        print( self.get_summ_str() )
        
        
    def get_summ_str(self, alpha_ordered=True, numbered=False, add_trailer=True, 
                     fillchar='.', max_banner=76, intro_str=''):
        """
        return string of the current state of Geometry instance.
        """
        M = self.get_model_summ_obj()
        return M.summ_str(alpha_ordered=alpha_ordered, numbered=numbered, 
                          add_trailer=add_trailer, fillchar=fillchar, 
                          max_banner=max_banner, intro_str=intro_str)
    
    def get_html_str(self, alpha_ordered=True, numbered=False, intro_str=''):
        M = self.get_model_summ_obj()
        return M.html_table_str( alpha_ordered=alpha_ordered, numbered=numbered, intro_str=intro_str)
        
    def get_model_summ_obj(self):
        """
        return ModelSummary object for current state of Geometry instance.
        """
        
        M = ModelSummary( 'Geometry' )
        M.add_alt_units('in', ['cm','ft'])
        M.add_alt_units('in**2', 'cm**2')
        M.add_alt_units('in**3', 'cm**3')
                        
        # function to add parameters from __doc__ string to ModelSummary
        def add_param( name, desc='', fmt='', units='', value=None):
            
            if name in self.inp_unitsD:
                units = self.inp_unitsD[name]
                
            if desc=='' and name in self.inp_descD:
                desc = self.inp_descD[name]
            
            if value is None:
                value = getattr( self, name )
            
            if self.is_inputD.get(name, False):
                M.add_inp_param( name, value, units, desc, fmt=fmt)
            else:
                M.add_out_param( name, value, units, desc, fmt=fmt)
        
        for name in self.is_inputD.keys():
            add_param( name )
        
        # parameters that are NOT attributes
        add_param( 'Dexit', value=self.Rexit*2, desc='nozzle exit diameter', units='in' )
        add_param( 'Dthrt', value=self.Rthrt*2, desc='throat diameter', units='in' )

        noz = self.getNozObj()
        add_param( 'entrance_angle', value=noz.theta, desc='nozzle initial expansion angle', units='deg' )
        add_param( 'exit_angle', value=noz.exitAng, desc='nozzle exit angle', units='deg' )
            
        return M
        
        
if __name__ == '__main__':
    import sys
    do_show = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'suppress_show':
            do_show = False

    geom = Geometry(Rthrt=1.5,
                    CR=2.5, eps=20,  pcentBell=80, LnozInp=18,
                    RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                    LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
    
    #M = geom.get_model_summ_obj()
    #print( M.summ_str() )
    
    geom.summ_print()
    
    
    if 0:
        geom.plot_geometry( png_name='geometry.png', do_show=do_show, show_grid=False,
                            make_vertical=True, pixel_wh=(300,400) )
