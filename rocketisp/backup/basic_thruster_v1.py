
"""
Basic Thrust Chamber
"""
from math import pi, sqrt
from rocketisp.efficiency.eff_pulsing import eff_pulse
from rocketisp.efficiency.eff_divergence import eff_div
from rocketisp.efficiency.effBL_NASA_SP8120 import eff_bl_NASA
from rocketisp.efficiency.calc_All_fracKin import calc_fracKin, calc_IspODK
from rocketisp.nozzle.cd_throat import get_Cd

USER_INPUT_STR = '...user input'

class BasicThruster:
    
    def __init__(self, oxName='N2O4', fuelName='MMH',  MR=1.5,
                 Pc=500, eps=20, Rthrt=1, pcentBell=80, CR=2.5, RupThroat=1.5,
                 effMix=1.0, effVap=1.0, effHL=1.0, Em=0.8,
                 effDiv=1.0, effTP=1.0, effKin=1.0, effBL=1.0,
                 effPulse=1.0, # assume chamber is not pulsing 
                 effFFC=1.0,   # Fuel Film Cooling (i.e. Barrier Cooling)
                 isRegenCham=0, noz_regen_eps=1.0): # regen cooling decreases boundary layer loss.

        """
        Start out with user input efficiency values... improve them later.

        :param oxName: oxidizer name
        :param fuelName: fuel name
        :param MR: mixture ration (ox flowrate / fuel flowrate)
        :param Pc: psia, chamber pressure
        :param eps: nozzle area ratio (exit area / throat area)
        :param Rthrt: in, throat radius
        :param pcentBell: %, percent bell 100 * (nozzle length / 15 deg cone length)
        :param CR: contraction ratio (injector area / throat area)
        :param RupThroat: throat upstream radius ratio (upstream radius / throat radius)
        :param effMix: inter-element mixing efficiency (e.g. 2 degree rule of thumb)
        :param effVap: vaporization efficiency
        :param effHL: chamber heat loss efficiency
        :param Em: intra-element Rupe mixing factor
        :param effDiv: nozzle divergence efficiency
        :param effTP: two phase flow efficiency
        :param effKin: nozzle kinetic efficiency
        :param effBL: nozzle boundary layer efficiency
        :param effPulse: pulsing efficiency
        :param effFFC: fuel film cooling efficiency
        :param isRegenCham: flag to indicate regen cooling
        :param noz_regen_eps: nozzle area ratio where regen cooling ends
        :type oxName: str
        :type fuelName: str
        :type MR: float
        :type Pc: float
        :type eps: float
        :type Rthrt: float
        :type pcentBell: float
        :type CR: float
        :type RupThroat: float
        :type effMix: float
        :type effVap: float
        :type effHL: float
        :type Em: float
        :type effDiv: float
        :type effTP: float
        :type effKin: float
        :type effBL: float
        :type effPulse: float
        :type effFFC: float
        :type isRegenCham: bool
        :type noz_regen_eps: float
        :return: BasicThruster object
        :rtype: BasicThruster        
        """
        
        # save the input values
        self.effMix     = effMix      # inter-element mixing, perhaps use "Mixing Angle"
        self.Em        = min(1.0, Em) # intra-element mixing parameter for injector
        self.effVap    = effVap       # vaporization
        self.effHL     = effHL        # chamber heat loss
        self.effPulse  = effPulse     # chamber pulsing
        self.effDiv    = effDiv       # nozzle divergence
        self.effTP     = effTP        # nozzle two-phase flow
        self.effKin    = effKin       # nozzle kinetic
        self.effBL     = effBL        # nozzle boundary layer

        self.oxName        = oxName
        self.fuelName      = fuelName
        self.MR            = MR
        self.Pc            = Pc
        self.eps           = eps
        self.Rthrt         = Rthrt
        self.CR            = CR
        self.RupThroat     = RupThroat
        self.pcentBell     = pcentBell
        self.effFFC        = effFFC
        self.isRegenCham   = isRegenCham
        self.noz_regen_eps = noz_regen_eps
        
        self.effMix_method   = USER_INPUT_STR
        self.effEm_method    = USER_INPUT_STR
        self.effVap_method   = USER_INPUT_STR
        self.effHL_method    = USER_INPUT_STR
        self.effPulse_method = USER_INPUT_STR
        self.effDiv_method   = USER_INPUT_STR
        self.effTP_method    = USER_INPUT_STR
        self.effKin_method   = USER_INPUT_STR
        self.effBL_method    = USER_INPUT_STR
        self.effFFC_method   = USER_INPUT_STR
        
        # make CEA object
        self.ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)
        
        # calc ideal performance parameters
        self.IspODE, self.cstarODE, self.TcODE, self.MWchm, self.gammaChm = \
                self.ceaObj.get_IvacCstrTc_ChmMwGam( Pc=self.Pc, MR=self.MR, eps=self.eps)
                
        self.IspODF,_,_ = self.ceaObj.getFrozen_IvacCstrTc( Pc=self.Pc, MR=self.MR, eps=self.eps, frozenAtThroat=0)
        
        # use user effKin to set IspODK
        self.IspODK = self.IspODE * self.effKin
        self.fracKin = (self.IspODK - self.IspODF) / (self.IspODE - self.IspODF)
        
        self.CdThroat = get_Cd( RWTU=self.RupThroat, gamma=self.gammaChm )
        
        self.calc_effEm( call_calc_overall=False ) # calc inter-element mixing efficiency
        self.calc_overall()

    def calc_overall(self):
        
        # make final summary efficiencies
        self.effPerfInj = self.effKin * self.effDiv * self.effBL * self.effTP
        
        self.effERE = self.effVap * self.effMix * self.effEm * self.effHL * self.effFFC * self.effPulse
        
        self.effIsp = self.effPerfInj * self.effERE
        self.IspDel = self.effIsp * self.IspODE
        self.cstarDel = self.cstarODE * self.effERE
        
        self.At = pi * self.Rthrt**2
        self.Ainj = self.At * self.CR
        
        self.wdotTot = self.Pc * self.At * self.CdThroat * 32.174 / self.cstarDel
        self.wdotOx  = self.wdotTot * self.MR / (1.0 + self.MR)
        self.wdotFl = self.wdotTot - self.wdotOx 
        
        self.Fvac = self.wdotTot * self.IspDel
    
    def solve_Rthrt(self, FvacLbf=500, Ftol=0.001, max_iter=10):
        
        for count in range( max_iter ):
            
            At_guess = self.At * FvacLbf / self.Fvac
            self.Rthrt = (At_guess/pi)**0.5

            if self.effTP_method    != USER_INPUT_STR:
                self.calc_effTP( self.effTP_method )
            if self.effBL_method    != USER_INPUT_STR:
                self.calc_effBL( self.effBL_method )
            if self.effDiv_method   != USER_INPUT_STR:
                self.calc_effDiv( self.effDiv_method )
            if self.effKin_method   != USER_INPUT_STR:
                self.calc_effKin( self.effKin_method )
            
            if self.effMix_method   != USER_INPUT_STR:
                self.calc_effMix( self.effMix_method )
            if self.effEm_method    != USER_INPUT_STR:
                self.calc_effEm( self.effEm_method )
            if self.effVap_method   != USER_INPUT_STR:
                self.calc_effVap( self.effVap_method )
            if self.effHL_method    != USER_INPUT_STR:
                self.calc_effHL( self.effHL_method )
            if self.effPulse_method != USER_INPUT_STR:
                self.calc_effPulse( pulse_sec=self.pulse_sec, 
                                    pulse_quality=self.pulse_quality,  
                                    method=self.effPulse_method )
            if self.effFFC_method   != USER_INPUT_STR:
                self.calc_effFFC( self.effFFC_method )
                
            if abs(self.Fvac - FvacLbf) < Ftol:
                #print('count =',count)
                break
    
    def calc_eff_nozzle(self):
        self.calc_effDiv( call_calc_overall=False )
        self.calc_effBL(  call_calc_overall=False )
        self.calc_effKin( call_calc_overall=False )
        self.calc_overall()
    
    def calc_effEm(self, call_calc_overall=True):
        # calc inter-element mixing efficiency
        if self.Em >= 1.0:
            self.effEm = 1.0
            self.effEm_method = USER_INPUT_STR
            return
        
        mrLow = self.MR * self.Em
        mrHi = self.MR / self.Em
        
        IspODK = calc_IspODK(self.ceaObj, Pc=self.Pc, eps=self.eps, Rthrt=self.Rthrt, 
                                    pcentBell=self.pcentBell, MR=self.MR)
        
        odkLowIsp = calc_IspODK(self.ceaObj, Pc=self.Pc, eps=self.eps, Rthrt=self.Rthrt, 
                                     pcentBell=self.pcentBell, MR=mrLow)
        odkHiIsp = calc_IspODK(self.ceaObj, Pc=self.Pc, eps=self.eps, Rthrt=self.Rthrt, 
                                    pcentBell=self.pcentBell, MR=mrHi)
                                  
        xm1=(1.+mrLow)/(1.+self.Em)/(1.+self.MR)
        xm2=1.0-xm1
        self.effEm = (xm1*odkLowIsp + xm2*odkHiIsp) / IspODK
        self.effEm_method = 'RocketIsp (Em=%g)'%self.Em
            
        if call_calc_overall:
            self.calc_overall()
    
    def calc_effDiv(self, method='RocketIsp', call_calc_overall=True):
        if method == 'RocketIsp':
            self.effDiv = eff_div( eps=self.eps, pcBell=self.pcentBell)
            self.effDiv_method = method
        else:
            raise Exception('Divergence Loss Method "%s", NOT recognized'%method)
            
        if call_calc_overall:
            self.calc_overall()
    
    def calc_effKin(self, method='RocketIsp', call_calc_overall=True):
        if method == 'RocketIsp':
            self.fracKin = calc_fracKin(self.ceaObj, Pc=self.Pc, eps=self.eps, 
                                        Rthrt=self.Rthrt, pcentBell=self.pcentBell, 
                                        MR=self.MR)
                                        
            self.IspODK = self.IspODF + self.fracKin * (self.IspODE-self.IspODF)

            self.effKin = self.IspODK / self.IspODE
            self.effKin_method = method
        else:
            raise Exception('Kinetic Loss Method "%s", NOT recognized'%method)
            
        if call_calc_overall:
            self.calc_overall()
    
    def calc_effBL(self, method='RocketIsp', call_calc_overall=True):
        if method == 'RocketIsp':
            self.effBL = eff_bl_NASA( Dt=self.Rthrt*2.0, Pc=self.Pc, eps=self.eps)
            if self.noz_regen_eps > 1.0:
                self.eff_BL = regen_corrected_bl( eff_bl=self.eff_BL, eps=self.eps, noz_regen_eps=self.noz_regen_eps )
            
            self.effBL_method = method
        else:
            raise Exception('Nozzle Boundary Layer Loss Method "%s", NOT recognized'%method)
            
        if call_calc_overall:
            self.calc_overall()
    
    def calc_effPulse(self, pulse_sec=0.1, pulse_quality=0.8, method='RocketIsp', call_calc_overall=True):
        
        if method.startswith('RocketIsp'):
            self.pulse_sec = pulse_sec
            self.pulse_quality = pulse_quality
            self.effPulse = eff_pulse( pulse_sec=pulse_sec, pulse_quality=pulse_quality)
            self.effPulse_method = 'RocketIsp (%g sec, Q=%g)'%(pulse_sec, pulse_quality)
        else:
            raise Exception('Pulse Loss Method "%s", NOT recognized'%method)
            
        if call_calc_overall:
            self.calc_overall()
    
    
    def calc_effXXX(self, method='RocketIsp', call_calc_overall=True):
        if method == 'RocketIsp':
            self.effXXX = XXX
            self.effXXX_method = method
        else:
            raise Exception('XXX Loss Method "%s", NOT recognized'%method)
            
        if call_calc_overall:
            self.calc_overall()
    
    
    def summ_print(self):
        print('       IspDel =', '%.2f'%self.IspDel, 'sec')
        print('       IspODF =', '%.2f'%self.IspODF, 'sec')
        print('       IspODK =', '%.2f'%self.IspODK, 'sec (fracKin=%g)'%self.fracKin)
        print('       IspODE =', '%.2f'%self.IspODE, 'sec')
        print('     cstarDel =', '%.1f'%self.cstarDel, 'ft/sec')
        print('     cstarODE =', '%.1f'%self.cstarODE, 'ft/sec')
        print()
        print('       effIsp =', '%.5f'%self.effIsp, '')
        print()
        print('____effERE____=', '%.5f'%self.effERE, '')
        print('       effVap =', '%.5f'%self.effVap, self.effVap_method, ' vaporization')
        print('       effMix =', '%.5f'%self.effMix, self.effMix_method, ' intra-element mixing')
        print('        effEm =', '%.5f'%self.effEm, self.effEm_method, ' inter-element mixing')
        print('        effHL =', '%.5f'%self.effHL, self.effHL_method, ' chamber heat loss')
        print('     effPulse =', '%.5f'%self.effPulse, self.effPulse_method, ' pulsing')
        print('       effFFC =', '%.5f'%self.effFFC, self.effFFC_method, ' fuel film cooling')
        print()
        print('__effPerfInj__=', '%.5f'%self.effPerfInj, '')
        print('       effDiv =', '%.5f'%self.effDiv, self.effDiv_method, ' divergence')
        print('        effTP =', '%.5f'%self.effTP, self.effTP_method, ' two phase')
        print('       effKin =', '%.5f'%self.effKin, self.effKin_method, ' kinetic')
        print('        effBL =', '%.5f'%self.effBL, self.effBL_method, ' boundary layer')
        print()
        print('       oxName =', '%s'%self.oxName, '')
        print('     fuelName =', '%s'%self.fuelName, '')
        print('           MR =', '%g'%self.MR, '')
        print('           Pc =', '%g'%self.Pc, 'psia')
        print('          eps =', '%g'%self.eps, '')
        print('        Rthrt =', '%g'%self.Rthrt, 'in')
        print('           CR =', '%g'%self.CR, '')
        print('           At =', '%g'%self.At, 'in**2')
        print('         Ainj =', '%g'%self.Ainj, 'in**2')
        
        print('    RupThroat =', '%g'%self.RupThroat)
        print('     CdThroat =', '%g'%self.CdThroat)
        print('      wdotTot =', '%g'%self.wdotTot, 'lbm/sec')
        print('       wdotOx =', '%g'%self.wdotOx, 'lbm/sec')
        print('       wdotFl =', '%g'%self.wdotFl, 'lbm/sec')
        print('         Fvac =', '%g'%self.Fvac, 'lbf')
        
        print('    pcentBell =', '%g'%self.pcentBell, '%')
        print('  isRegenCham =', '%s'%self.isRegenCham, '')
        if self.noz_regen_eps > 1.0:
            print('noz_regen_eps =', '%g'%self.noz_regen_eps, '')

        print('        TcODE =', '%.1f'%self.TcODE, 'degR')
        print('        MWchm =', '%g'%self.MWchm, 'g/gmole')
        print('     gammaChm =', '%g'%self.gammaChm, '')
        
if __name__ == "__main__":
    
    from rocketcea.cea_obj import CEA_Obj
    
    ceaObj = CEA_Obj(oxName='N2O4', fuelName='MMH', useFastLookup=0)

    bt = BasicThruster( oxName='N2O4', fuelName='MMH',  MR=1.5,
        Pc=500, eps=20, Rthrt=1, pcentBell=80,
        effMix=1.0, effVap=1.0, effHL=1.0, Em=0.8,
        effDiv=1.0, effTP=1.0, effKin=1.0, effBL=1.0,
        effPulse=1.0, # assume chamber is not pulsing 
        effFFC=1.0,   # Fuel Film Cooling (i.e. Barrier Cooling)
        isRegenCham=0, noz_regen_eps=1.0) # regen cooling decreases boundary layer loss.
    bt.calc_eff_nozzle()
    bt.calc_effPulse( pulse_sec=0.1, pulse_quality=0.8, method='RocketIsp', call_calc_overall=True)
    bt.solve_Rthrt( FvacLbf=5000, Ftol=0.001, max_iter=10)
    bt.summ_print()
        