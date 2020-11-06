from math import pi, sqrt, radians, sin, cos, tan
from rocketisp.nozzle.cd_throat import get_Cd
from rocketisp.nozzle.nozzle import Nozzle

class Chamber:
    
    def __init__(self, thruster, # BasicThruster object
        FvacLbf=500, # can be float or None (None indicates constant throat area)
        CR=2.5, RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0,
        LchmOvrDt=4.0, LchmMin=1.0, LchamberInp=None, cham_conv_deg=30,
        isRegenCham=0):
        """
        Chamber object holds basic information about the chamber portion of the
        thrust chamber and nozzle under investigation.

        :param thruster: BasicThruster object 
        :param FvacLbf" lbf, thrust of thruster (None indicates constant throat area)
        :param CR: contraction ratio (injector area / throat area)
        :param RupThroat: throat upstream radius ratio (upstream radius / throat radius)
        :param RdwnThroat: throat downstream radius ratio (downstream radius / throat radius)
        :param RchmConv: convergent radius ratio (convergent radius / throat radius)
        :param LchmOvrDt: chamber length / throat diam (Lchm / Dt)
        :param LchmMin: in, minimum chamber length
        :param LchamberInp: in or None, input chamber length
        :param cham_conv_deg: deg, chamber convergent section half angle
        :param isRegenCham: flag to indicate chamber is regen cooled
        :type thruster: BasicThruster
        :type FvacLbf: float or None
        :type CR: float
        :type RupThroat: float
        :type RdwnThroat: float
        :type RchmConv: float
        :type LchmOvrDt: float
        :type LchmMin: float
        :type LchamberInp: float or None
        :type cham_conv_deg: float
        :type isRegenCham: bool
        :return: Chamber object
        :rtype: Chamber        
        """
        self.thruster       = thruster
        self.FvacLbf        = FvacLbf # (None indicates constant throat area)
        self.CR             = CR
        self.RupThroat      = RupThroat
        self.RdwnThroat     = RdwnThroat
        self.RchmConv       = RchmConv
        self.LchmOvrDt      = LchmOvrDt
        self.LchmMin        = LchmMin
        self.LchamberInp    = LchamberInp
        self.cham_conv_deg  = cham_conv_deg
        self.cham_conv_rad  = radians( cham_conv_deg )
        self.isRegenCham    = isRegenCham     
                
        self.calc_overall()

    def calc_overall(self):
        
        # recalc BasicThruster in case a basic parameter has changed.
        self.thruster.calc_overall()
        if self.FvacLbf is not None:
            self.thruster.solve_Rthrt( FvacLbf=self.FvacLbf, Ftol=0.001, max_iter=10)

        # calc injector area
        self.Ainj = self.thruster.At * self.CR
        
        self.Dinj = sqrt( self.Ainj / pi ) * 2.0
        if self.LchamberInp is None:
            self.Lcham = max( self.LchmMin, self.LchmOvrDt * self.thruster.Rthrt * 2.0 )
        else:
            self.Lcham = self.LchamberInp
        self.calc_convergent_section() # may reset Lcham to longer value
        
        # calc Cd of throat
        CdThroat = get_Cd( RWTU=self.RupThroat, gamma=self.thruster.gammaChm )
        self.thruster.reset_attr( 'CdThroat', CdThroat, call_calc_overall=True)
                                          
        if self.FvacLbf is not None:
            self.thruster.solve_Rthrt( FvacLbf=self.FvacLbf, Ftol=0.001, max_iter=10)
            
    def calc_convergent_section(self):
        Rt   = 1.0 # dimensionless calcs
        Rchm = Rt * sqrt(self.CR) # dimensionless calcs
        cosA = cos( self.cham_conv_rad )
        sinA = sin( self.cham_conv_rad )
        tanA = tan( self.cham_conv_rad )
        
        htSeg = Rchm - self.RupThroat*(1.0-cosA) - self.RchmConv*(1.0-cosA) - Rt # ht of linear segment
        if htSeg < 0.0:
            # radii are too big for CR... reduce radii or inc CR
            print('Warning... Convergent Section error... dec radii or inc CR')
            
        htSeg = Rchm - self.RupThroat*(1.0-cosA) - self.RchmConv*(1.0-cosA) - Rt # ht of linear segment
        wdSeg = htSeg / tanA
        
        zstart_conv = -( (self.RchmConv + self.RupThroat) * sinA + wdSeg )
        zstart_conv *= self.thruster.Rthrt # convert back to inches.
                
        self.Lcham_conv = abs( zstart_conv )
        self.Lcham_cyl = self.Lcham - self.Lcham_conv
        if self.Lcham_cyl < 0.0:
            self.Lcham_cyl = 0.0
            self.Lcham = self.Lcham_conv
        
        
        
    def summ_print(self):
        self.thruster.summ_print()
        print('---------------%s/%s chamber-----------------------'%(self.thruster.oxName, self.thruster.fuelName))
        print('            CR =', '%g'%self.CR, 'injector area / throat area')
        print('  cham_conv_deg=', '%g'%self.cham_conv_deg, 'deg convergent section half angle' )
        print('         Lcham =', '%g'%self.Lcham, 'in')
        print('     Lcham_cyl =', '%g'%self.Lcham_cyl, 'in')
        print('    Lcham_conv =', '%g'%self.Lcham_conv, 'in')
        print('          Dinj =', '%g'%self.Dinj, 'in')
        print('          Ainj =', '%g'%self.Ainj, 'in**2')
        
        print('     RupThroat =', '%g'%self.RupThroat, 'upstream radius / throat radius')
        print('     LchmOvrDt =', '%g'%self.LchmOvrDt, 'chamber length / throat diameter')
        print('       LchmMin =', '%g'%self.LchmMin, 'in, minimum chamber length')
        print('   isRegenCham =', '%s'%self.isRegenCham, '')
        
    
    def plot_contour(self,  do_show=True, save_to_png=False, show_chamber=True):
        
        noz = Nozzle(CR=self.CR, eps=self.thruster.eps, pcentBell=self.thruster.pcentBell,
                     Rt=self.thruster.Rthrt,  Nsegs=20,  
                     Rup=self.RupThroat, Rd=self.RdwnThroat, cham_conv_ang=self.cham_conv_deg, 
                     Rc=self.RchmConv,
                     theta=None, exitAng=None, forceCone=0, use_huzel_angles=False)
        
        if show_chamber:
            Lchamber = self.Lcham
        else:
            Lchamber = None
        
        noz.plot_geom( do_show=do_show, save_to_png=save_to_png, Lchamber=Lchamber )
        
        
        
if __name__ == '__main__':
    from rocketisp.basic_thruster import BasicThruster
    bt = BasicThruster( oxName='N2O4', fuelName='MMH',  MR=1.5,
        Pc=500, eps=20, Rthrt=0.5, pcentBell=80,
        effMix=1.0, effVap=1.0, effHL=1.0, effEm=1.0,
        effDiv=1.0, effTP=1.0, effKin=1.0, effBL=1.0,
        effPulse=1.0, # assume chamber is not pulsing 
        effFFC=1.0,   # Fuel Film Cooling (i.e. Barrier Cooling)
        isRegenCham=0, noz_regen_eps=1.0) # regen cooling decreases boundary layer loss.
    bt.calc_eff_nozzle()
    #bt.solve_Rthrt( FvacLbf=500, Ftol=0.001, max_iter=10)
    
    C = Chamber(bt, FvacLbf=123, RupThroat=1.0, RchmConv=1.0,)
    C.summ_print()
    #C.plot_contour( do_show=True, save_to_png=False, show_chamber=True)
    