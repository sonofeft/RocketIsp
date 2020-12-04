from math import pi
import os
from rocketisp.model_summ import ModelSummary
from rocketisp.parse_docstring import get_desc_and_units


if 'READTHEDOCS' not in os.environ:
    from rocketcea.cea_obj import CEA_Obj
    from rocketcea.separated_Cf import sepNozzleCf
else:
    from rocketisp.mock.cea_obj import CEA_Obj
    from rocketisp.mock.separated_Cf import sepNozzleCf

from rocketisp.efficiency.calc_noz_kinetics import calc_IspODK
from rocketisp.efficiencies import Efficiencies
from rocketisp.geometry import Geometry

def shapeFactor( WentrOvWcool ):
    '''Subsonic Shape Factor from COMBUSTION EFFECTS ON FILM COOLING manual Figure 5, page 88
       https://ntrs.nasa.gov/citations/19770014416
       "Mixing Layer Profile Shape Factor Correlations"'''
    if WentrOvWcool > 1.4:
        return 1.0 / 1.32  
    elif WentrOvWcool < 0.06:
        # from the definintion of effectiveness and the fact that effectiveness=1
        return 1.0 / (1.0 + WentrOvWcool) 
    else:
        # curve fit of COMBUSTION EFFECTS ON FILM COOLING manual figure 5 subsonic curve
        return (0.962+(0.299*WentrOvWcool))/(1+(0.67*WentrOvWcool)+(-0.06*WentrOvWcool**2))

def solve_At_split( MRc, MRb, ffc, cstar_c, cstar_b ):
    """
    Given MRcore, MRbarrier, fracFFC, cstar_c and cstar_b, solve the throat area split
    between the core and barrier.
    """
    MReng = MRc * (1.0 - ffc)
    fAtc_min = 0.0
    fAtc_max = 1.0
    ccm = cstar_c * (MRc + 1.0)
    cbm = cstar_b * (MRb + 1.0)
    for _ in range(40):
        fAtc = (fAtc_min + fAtc_max)/2.0
        
        Atc = fAtc
        Atb = 1.0 - fAtc
        mre = (Atc*MRc/ccm + Atb*MRb/cbm) / (Atc/ccm + Atb/cbm)
        
        if mre < MReng:
            fAtc_min = fAtc
        else:
            fAtc_max = fAtc
    return (fAtc_min + fAtc_max)/2.0
        

class BarrierStream:
    """
    A BarrierStream is typically used to evaluate fuel film cooling, 
    see: https://ntrs.nasa.gov/citations/19770014416
    COMBUSTION EFFECTS ON FILM COOLING, 24 Feb 1977 by Aerojet Liquid Rocket Co.
    
    :param coreObj: core stream tube object, CoreStream
    :param pcentFFC: percent fuel film cooling ( FFC flowrate / total fuel flowrate)
    :param ko: entrainment constant (typical value is 0.035, range from 0.03 to 0.06)
    :type coreObj: CoreStream
    :type pcentFFC: float
    :type ko: float
    :return: BarrierStream object
    :rtype: BarrierStream

    :ivar MRbarrier: barrier mixture ratio
    :ivar MRwall: mixture ratio at wall
    :ivar Twallgas: degR, temperature of gas at wall
    :ivar TcODE_b: degR, average ideal ODE temperature of barrier gas
    :ivar WentrOvWcool: ratio of entrained flow rate to FFC flow rate
    :ivar IspDel_b: sec, delivered vacuum barrier Isp
    :ivar IspODF_b: sec, ideal frozen barrier Isp
    :ivar IspODK_b: sec, vacuum kinetic Isp of barrier
    :ivar fracKin_b: fraction of kinetic completion in barrier
    :ivar IspODE_b:  sec. ideal equilibrium barrier Isp
    :ivar cstarERE_b: ft/s, delivered cstar
    :ivar cstarODE_b: ft/s, ideal equilibrium cstar    
    """
    def __init__(self, coreObj, pcentFFC=10.0, ko=0.035):
        """
        A BarrierStream, see: https://ntrs.nasa.gov/citations/19770014416
        COMBUSTION EFFECTS ON FILM COOLING, 24 Feb 1977 by Aerojet Liquid Rocket Co.
        
        """
        self.coreObj  = coreObj
        self.geomObj  = coreObj.geomObj
        self.ceaObj   = coreObj.ceaObj
        self.pcentFFC = pcentFFC
        self.ko        = ko
        self.warningL  = [] # list of any evaluate warnings
        
        self.evaluate()
        
        # get input descriptions and units from doc string
        self.inp_descD, self.inp_unitsD, self.is_inputD = get_desc_and_units( self.__doc__ )
        
    def __call__(self, name):
        return getattr(self, name ) # let it raise exception if no name attr.
        
    def evaluate(self):
        """
        Estimate entrained core flow into film cooled stream tube and calculate
        performance of barrier stream tube.
        """
        
        self.warningL  = []
        
        # figure out entrainment fraction and MRbarrier based on geometry and pcentFFC
        LprimeOvRcham = self.geomObj.Lcham / self.geomObj.Rinj
        
        # an approximation for equation 27 in COMBUSTION EFFECTS ON FILM COOLING, page 20
        fracEntr = 2.0*(LprimeOvRcham*self.ko) - (LprimeOvRcham*self.ko)**2
        
        fracFFC = self.pcentFFC / 100.0
        MReng = self.coreObj.MRcore * (1.0 - fracFFC)
        
        # use a ref. flow rate of 1.0... will generate ratios from ref flow rate
        wdotCoreInj = 1.0 # a ref flow rate
        wdotFuelCoreInj = wdotCoreInj / (1.0 + self.coreObj.MRcore)
        wdotOxCoreInj = wdotCoreInj - wdotFuelCoreInj
        wdotFuelTot = MReng * wdotOxCoreInj
        
        wdotFFC = fracFFC * wdotFuelTot # relative to ref wdotCoreInj
        wdotEntr = fracEntr * wdotCoreInj
        
        self.WentrOvWcool = wdotEntr / wdotFFC
    
        # shape factor comes from a curve fit of COMBUSTION EFFECTS ON FILM COOLING Figure 5, page 88
        SFact = shapeFactor(self.WentrOvWcool)
        
        # effectiveness come from equation 17 in COMBUSTION EFFECTS ON FILM COOLING, page 15
        self.effnessFC = 1.0/(SFact * (1.0 + self.WentrOvWcool))
        
        #wdotFuelEntr = wdotFuelTot * (fracEntr - (fracEntr * fracFFC))
        wdotFuelEntr = wdotFuelCoreInj * fracEntr
        wdotOxEntr = wdotOxCoreInj * fracEntr
        
        self.MRbarrier = wdotOxEntr / (wdotFuelEntr + wdotFFC)

        #print('self.WentrOvWcool=%g'%self.WentrOvWcool,'    fracEntr=%g'%fracEntr, 
        #      '   MRcore=%g'%self.coreObj.MRcore, '    effnessFC=%g'%self.effnessFC, 
        #      '   MRbarrier=%g'%self.MRbarrier, '   MReng=%g'%MReng)

        
        # using eqn (2) on page 7 (pdf 21) of COMBUSTION EFFECTS ON FILM COOLING
        # film cooling effectiveness is always equal to the
        # mass fraction of the injected film coolant gas within the gas mixture directly
        # adjacent to the wall.
        massfracOxWall = (1.0 - self.effnessFC) * self.MRbarrier / (1.0 + self.MRbarrier)
        self.MRwall = massfracOxWall / (1.0 - massfracOxWall)
        
        self.Twallgas = self.ceaObj.get_Tcomb( Pc=self.coreObj.Pc, MR=self.MRwall)
        
        # ........... calc ideal performance parameters
        self.IspODE_b, self.cstarODE_b, self.TcODE_b, self.MWchm_b, self.gammaChm_b = \
                self.ceaObj.get_IvacCstrTc_ChmMwGam( Pc=self.coreObj.Pc, MR=self.MRbarrier, 
                                                     eps=self.geomObj.eps)
        
        self.cstarODE_b *= self.coreObj.adjCstarODE
        self.IspODE_b *= self.coreObj.adjIspIdeal
        
        self.IspODF_b,_,_ = self.ceaObj.getFrozen_IvacCstrTc( Pc=self.coreObj.Pc, MR=self.MRbarrier, 
                                                            eps=self.geomObj.eps)
        self.IspODF_b *= self.coreObj.adjIspIdeal
        
        if self.IspODF_b < 10.0: # there's an error in frozen low MR CEA, so estimate from core 
            self.warningL.append( 'WARNING... CEA failed frozen Isp for MR=%g'%self.MRbarrier  )
            
            self.IspODF_b = self.IspODE_b * (self.coreObj.IspODF / self.coreObj.IspODE)
            
            self.IspODK_b = self.IspODF_b + self.coreObj.fracKin*(self.IspODE_b - self.IspODF_b)
            self.warningL.append( '           Estimated IspODF_b = %g sec'%self.IspODF_b  )
        
        else:
            # use user effKin to set IspODK
            self.IspODK_b = calc_IspODK(self.ceaObj, Pc=self.coreObj.Pc, eps=self.geomObj.eps, 
                                        Rthrt=self.geomObj.Rthrt, 
                                        pcentBell=self.geomObj.pcentBell, 
                                        MR=self.MRbarrier)
            self.IspODK_b *= self.coreObj.adjIspIdeal
            
        self.fracKin_b = (self.IspODK_b - self.IspODF_b) / (self.IspODE_b - self.IspODF_b)
        
        self.effKin_b = self.IspODK_b / self.IspODE_b
        
        # ........ make final summary efficiencies
        effObj = self.coreObj.effObj
        
        if effObj.effD['Noz'].is_const:
            self.effNoz_b = self.effKin_b * effObj('Noz')
        else:
            self.effNoz_b = self.effKin_b * effObj('Div') * effObj('BL') * effObj('TP')
        
        if effObj.effD['ERE'].is_const:
            self.effERE_b = effObj('ERE')
        else:
            self.effERE_b = effObj('Vap') * effObj('Mix') * effObj('Em') * effObj('HL')
        
        self.effIsp_b = self.effNoz_b * self.effERE_b
        self.IspDel_b = self.effIsp_b * self.IspODE_b
        self.cstarERE_b = self.cstarODE_b * self.effERE_b
        
    
    def summ_print(self):
        """
        print to standard output, the current state of BarrierStream instance.
        """
        print( self.get_summ_str() )
        
    def get_summ_str(self, alpha_ordered=True, numbered=False, add_trailer=True, 
                     fillchar='.', max_banner=76, intro_str=''):
        
        """
        return string of the current state of BarrierStream instance.
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
        return ModelSummary object for current state of BarrierStream instance.
        """
        
        M = ModelSummary( 'Barrier Stream Tube' )
        M.add_alt_units('ft/s', 'm/s')
        M.add_alt_units('sec', ['N-sec/kg', 'km/sec'])
        M.add_alt_units('degR', ['degK','degC','degF'])
                
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
            if name not in ['coreObj']:
                add_param( name )
        '''
        add_param('MRbarrier', desc='barrier mixture ratio')
        add_param('MRwall', desc='mixture ratio at wall')
        add_param('Twallgas', units='degR', desc='temperature of gas at wall', fmt='%.0f')
        add_param('TcODE_b', units='degR', desc='average ideal ODE temperature of barrier gas', fmt='%.0f')
        #add_param('effnessFC', desc='effectiveness from equation 17 in COMBUSTION EFFECTS ON FILM COOLING, page 15')
        add_param('WentrOvWcool', desc='ratio of entrained flow rate to FFC flow rate')
        add_param('IspDel_b', units='sec', desc='delivered vacuum barrier Isp', fmt='%.1f')
        add_param('IspODF_b', units='sec', desc='ideal frozen barrier Isp', fmt='%.1f')
        add_param('IspODK_b', units='sec', desc='vacuum kinetic Isp of barrier', fmt='%.1f')
        add_param('fracKin_b', desc='fraction of kinetic completion in barrier')
        add_param('IspODE_b',  units='sec', desc='ideal equilibrium barrier Isp', fmt='%.1f')
        add_param('cstarERE_b', units='ft/s', desc='delivered cstar', fmt='%.1f')
        add_param('cstarODE_b', units='ft/s', desc='ideal equilibrium cstar', fmt='%.1f')
        '''
        return M
        
class CoreStream:
    """
        Core stream tube of liquid bipropellant thruster.

        :param geomObj: Geometry that describes thruster
        :param effObj: Efficiencies object to hold individual efficiencies
        :param oxName: name of oxidizer (e.g. N2O4, LOX)
        :param fuelName: name of fuel (e.g. MMH, LH2)
        :param MRcore: mixture ratio of core flow (ox flow rate / fuel flow rate)
        :param Pc: psia, chamber pressure
        :param CdThroat: Cd of throat (RocketThruster object may override)
        :param Pamb: psia, ambient pressure (for example sea level is 14.7 psia)
        :param adjCstarODE: multiplier on NASA CEA code value of cstar ODE (default is 1.0)
        :param adjIspIdeal: multiplier on NASA CEA code value of Isp ODE (default is 1.0)
        :param pcentFFC: percent fuel film cooling (if > 0 then add BarrierStream)
        :param ko: entrainment constant (passed to BarrierStream object, range from 0.03 to 0.06)
        :param ignore_noz_sep: flag to force nozzle flow separation to be ignored (USE WITH CAUTION)
        :type geomObj: Geometry
        :type effObj: Efficiencies
        :type oxName: str
        :type fuelName: str
        :type MRcore: float
        :type Pc: float
        :type CdThroat: float
        :type Pamb: float
        :type adjCstarODE: float
        :type adjIspIdeal: float
        :type pcentFFC: float
        :type ko: float
        :type ignore_noz_sep: bool
        :return: CoreStream object
        :rtype: CoreStream 
        
        :ivar FvacTotal: lbf, total vacuum thrust
        :ivar FvacCore: lbf, vacuum thrust due to core stream tube
        :ivar MRthruster: total thruster mixture ratio')
        :ivar IspDel: sec, <=== thruster delivered vacuum Isp ===>
        :ivar Pexit: psia, nozzle exit pressure
        :ivar IspDel_core: sec, delivered Isp of core stream tube
        :ivar IspODF: sec, core frozen Isp
        :ivar IspODK: sec, core one dimensional kinetic Isp
        :ivar IspODE: sec, core one dimensional equilibrium Isp
        :ivar cstarERE: ft/s, delivered core cstar
        :ivar cstarODE: ft/s, core ideal cstar
        :ivar CfVacIdeal: ideal vacuum thrust coefficient
        :ivar CfVacDel: delivered vacuum thrust coefficient
        :ivar CfAmbDel: delivered ambient thrust coefficient
        :ivar wdotTot: lbm/s, total propellant flow rate (ox+fuel)
        :ivar wdotOx: lbm/s, total oxidizer flow rate
        :ivar wdotFl: lbm/s, total fuel flow rate
        :ivar TcODE: degR, ideal core gas temperature
        :ivar MWchm: g/gmole, core gas molecular weight
        :ivar gammaChm: core gas ratio of specific heats (Cp/Cv)
        
    """
    
    def __init__(self, geomObj=Geometry(), effObj=Efficiencies(),  #ERE=0.98, Noz=0.97), 
                 oxName='N2O4', fuelName='MMH',  MRcore=1.9,
                 Pc=500, CdThroat=0.995, Pamb=0.0, adjCstarODE=1.0, adjIspIdeal=1.0,
                 pcentFFC=0.0, ko=0.035, ignore_noz_sep=False): 

        self.geomObj  = geomObj
        self.effObj   = effObj
        self.oxName   = oxName
        self.fuelName = fuelName
        self.MRcore   = MRcore
        self.Pc       = Pc
        self.Pamb     = Pamb # ambient pressure
        self.noz_mode = ''
        self.CdThroat = CdThroat
        
        self.CdThroat_method   = 'default'
        self.ignore_noz_sep    = ignore_noz_sep # ignore any nozzle separation
        
        self.adjCstarODE = adjCstarODE # may want to adjust ODE cstar value
        self.adjIspIdeal = adjIspIdeal # may want to adjust ODE and ODF Isp values
        
        # make CEA object
        self.ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)
        
        # ... if pcentFFC > 0.0, then there's barrier cooling
        if pcentFFC > 0.0:
            self.add_barrier = True
        else:
            self.add_barrier = False
        
        # barrier might need some performance parameters from CoreStream
        self.calc_cea_perf_params()
        
        if self.add_barrier:
            self.barrierObj = BarrierStream(self, pcentFFC=pcentFFC, ko=ko)
        else:
            self.barrierObj = None
        
        self.evaluate()
        
        # get input descriptions and units from doc string
        self.inp_descD, self.inp_unitsD, self.is_inputD = get_desc_and_units( self.__doc__ )
        
    def __call__(self, name):
        return getattr(self, name ) # let it raise exception if no name attr.
    
    def reset_CdThroat(self, value, method_name='RocketIsp', re_evaluate=True):
        """
        reset the value of CdThroat
        If re_evaluate is True, then call self.evaluate() after resetting the efficiency.
        """
        self.CdThroat = value
        self.CdThroat_method = method_name
            
        if re_evaluate:
            self.evaluate()
            
    def reset_attr(self, name, value, re_evaluate=True):
        """
        reset the value of any existing attribute of CoreStream instance.
        If re_evaluate is True, then call self.evaluate() after resetting the value of the attribute.
        """
        if hasattr( self, name ):
            setattr( self, name, value )
        else:
            raise Exception('Attempting to set un-authorized CoreStream attribute named "%s"'%name )
            
        if name in ['oxName','fuelName']:
            # make CEA object
            self.ceaObj = CEA_Obj(oxName=self.oxName, fuelName=self.fuelName)

            
        if re_evaluate:
            self.evaluate()
    
    def calc_cea_perf_params(self):
        """Calc basic Isp values from CEA and calc implied IspODK from current effKin value."""
        
        # calc ideal CEA performance parameters
        self.IspODE, self.cstarODE, self.TcODE, self.MWchm, self.gammaChm = \
                self.ceaObj.get_IvacCstrTc_ChmMwGam( Pc=self.Pc, MR=self.MRcore, eps=self.geomObj.eps)
        
        self.cstarODE *= self.adjCstarODE
        self.IspODE *= self.adjIspIdeal
        
        self.IspODF,_,_ = self.ceaObj.getFrozen_IvacCstrTc( Pc=self.Pc, MR=self.MRcore, 
                                                            eps=self.geomObj.eps)
        self.IspODF *= self.adjIspIdeal
        
        # use user effKin to set IspODK (or most recent update)
        self.IspODK = self.IspODE * self.effObj('Kin')
        #self.IspODK = calc_IspODK(self.ceaObj, Pc=self.Pc, eps=self.geomObj.eps, 
        #                          Rthrt=self.geomObj.Rthrt, 
        #                          pcentBell=self.geomObj.pcentBell, 
        #                          MR=self.MRcore)
        
        # fraction of equilibrium kinetics obtained
        self.fracKin = (self.IspODK - self.IspODF) / (self.IspODE - self.IspODF)
        
        
        self.Pexit = self.Pc / self.ceaObj.get_PcOvPe( Pc=self.Pc, MR=self.MRcore, eps=self.geomObj.eps)
        
        self.CfVacIdeal = 32.174 * self.IspODE / self.cstarODE
        
    
    def evaluate(self):
        """
        Assume that all efficiencies have been set, either by original user value
        or an update by an efficiency model.
        """
        self.effObj.evaluate()
        self.calc_cea_perf_params()
                
        # make final summary efficiencies
        effNoz = self.effObj('Noz')

        # want a Core-Only ERE in case a barrier calc is done
        effERE_core = self.effObj('ERE')
        if not self.add_barrier: # if no barrier, user may have input FFC
            effERE_core = effERE_core * self.effObj('FFC')

        cstarERE_core = self.cstarODE * effERE_core
        
        effIsp_core = effNoz * effERE_core
        self.IspDel_core = effIsp_core * self.IspODE

        if self.add_barrier:
            self.barrierObj.evaluate()
            
            fAtc = solve_At_split( self.MRcore, self.barrierObj.MRbarrier, 
                                   self.barrierObj.pcentFFC / 100.0, 
                                   cstarERE_core, self.barrierObj.cstarERE_b )
            
            self.frac_At_core = fAtc # core shares throat area with barrier stream
            
            self.frac_At_barrier = 1.0 - self.frac_At_core
            self.At_b = self.frac_At_barrier * self.geomObj.At
            
            self.wdotTot_b = self.Pc * self.At_b * self.CdThroat * 32.174 / self.barrierObj.cstarERE_b
            self.wdotOx_b  = self.wdotTot_b * self.barrierObj.MRbarrier / (1.0 + self.barrierObj.MRbarrier)
            self.wdotFl_b = self.wdotTot_b - self.wdotOx_b
            
            self.FvacBarrier = self.wdotTot_b * self.barrierObj.IspDel_b
            self.MRthruster = self.MRcore * (1.0 - self.barrierObj.pcentFFC / 100.0)
        else:
            self.frac_At_core = 1.0 # core gets all of throat area if no barrier stream
            self.frac_At_barrier = 0.0
            self.FvacBarrier = 0.0
            self.MRthruster = self.MRcore

            self.wdotTot_b = 0.0
            self.wdotOx_b  = 0.0
            self.wdotFl_b  = 0.0

        
        self.Atcore = self.frac_At_core * self.geomObj.At
        
        self.wdotTot_c = self.Pc * self.Atcore * self.CdThroat * 32.174 / cstarERE_core
        self.wdotOx_c  = self.wdotTot_c * self.MRcore / (1.0 + self.MRcore)
        self.wdotFl_c = self.wdotTot_c - self.wdotOx_c
        
        self.FvacCore = self.wdotTot_c * self.IspDel_core
        self.FvacTotal = self.FvacCore + self.FvacBarrier

        self.wdotTot = self.wdotTot_c + self.wdotTot_b
        self.wdotOx  = self.wdotOx_c + self.wdotOx_b
        self.wdotFl = self.wdotFl_c + self.wdotFl_b
        
        if self.add_barrier:
            self.wdotFlFFC = (self.barrierObj.pcentFFC/100.0) * self.wdotFl
            self.wdotFl_cInit = self.wdotFl - self.wdotFlFFC
            self.wdotTot_cInit = self.wdotOx + self.wdotFl_cInit
        else:
            self.wdotFlFFC = 0.0
            self.wdotFl_cInit = self.wdotFl
            self.wdotTot_cInit = self.wdotTot

        self.IspDel = self.FvacTotal / self.wdotTot
        
        self.IspDelPulse = self.IspDel* self.effObj('Pulse')
        
        if self.add_barrier: # if barrier is analysed, assume it is in addition to user input effERE
            effFFC = self.IspDel / self.IspDel_core
            self.effObj.set_value('FFC', effFFC, value_src='barrier calc' )
        
        self.cstarERE = self.cstarODE * self.effObj('ERE')
        #self.cstarDel = self.Pc * self.Atcore * self.CdThroat * 32.174 / self.wdotTot
        
        
        # do any nozzle ambient performance calcs here
        if self.Pamb < 0.000001:
            self.IspAmb = self.IspDel
            self.noz_mode = '(Pexit=%g psia)'%self.Pexit
        else:
            CfOvCfvacAtEsep, CfOvCfvac, Cfsep, CfiVac, CfiAmbSimple, CfVac, epsSep, self.Psep = \
                 sepNozzleCf(self.gammaChm, self.geomObj.eps, self.Pc, self.Pamb)
            #print('epsSep=%g, Psep=%g'%(epsSep, self.Psep))
            #print('========= Pexit=%g'%self.Pexit, '    Psep=%g'%self.Psep, '  epsSep=%g'%epsSep)
            
            if self.Pexit > self.Psep or self.ignore_noz_sep:
                # if not separated, use theoretical equation for back-pressure correction
                self.IspAmb = self.IspDel - self.cstarERE * self.Pamb * self.geomObj.eps / self.Pc / 32.174
                #print('---------------->  subtraction term =', self.cstarERE * self.Pamb * self.geomObj.eps / self.Pc / 32.174)
            else:
                # if separated, use Kalt and Badal estimate of ambient thrust coefficient
                # NOTE: there are better, more modern methods available
                IspODEepsSep, CstarODE, Tc = \
                    self.ceaObj.get_IvacCstrTc(Pc=self.Pc, MR=self.MRcore, eps=epsSep)
                    
                effPamb = IspODEepsSep / self.IspODE
                #print('--------------> effPamb=%g'%effPamb, '    IspODEepsSep=%g'%IspODEepsSep, '   IspODE=%g'%self.IspODE)
                
                self.IspAmb = effPamb * self.IspDel
            
            #print('========= Pamb=%g'%self.Pamb, '    IspAmb=%g'%self.IspAmb)
            # figure out mode of nozzle operation
            if self.Pexit > self.Psep:
                if self.Pexit > self.Pamb + 0.05:
                    self.noz_mode = 'UnderExpanded (Pexit=%g)'%self.Pexit
                elif self.Pexit < self.Pamb - 0.05:
                    self.noz_mode = 'OverExpanded (Pexit=%g)'%self.Pexit
                else:
                    self.noz_mode = 'Pexit=%g'%self.Pexit
            else:
                self.noz_mode = 'Separated (Psep=%g, epsSep=%g)'%(self.Psep,epsSep)
                
        self.Fambient = self.FvacTotal * self.IspAmb / self.IspDel

        self.CfVacDel = self.FvacTotal / (self.geomObj.At * self.Pc) # includes impact of CdThroat
        self.CfAmbDel = self.Fambient  / (self.geomObj.At * self.Pc) # includes impact of CdThroat
    
    def summ_print(self):
        """
        print to standard output, the current state of CoreStream instance.
        """
        print( self.get_summ_str() )
        
    def get_summ_str(self, alpha_ordered=True, numbered=False, add_trailer=True, 
                     fillchar='.', max_banner=76, intro_str=''):
        """
        return string of the current state of CoreStream instance.
        """
        
        M = self.get_model_summ_obj()
        
        Me = self.effObj.get_model_summ_obj()
        se = '\n' + Me.summ_str(alpha_ordered=False, fillchar=' ', assumptions_first=False)
        
        if self.add_barrier:
            Mb = self.barrierObj.get_model_summ_obj()
            sb = '\n' + Mb.summ_str(alpha_ordered=alpha_ordered, numbered=numbered, 
                                   add_trailer=add_trailer, fillchar=fillchar, 
                                   max_banner=max_banner, intro_str=intro_str)
        else:
            sb = ''
        
        return M.summ_str(alpha_ordered=alpha_ordered, numbered=numbered, 
                          add_trailer=add_trailer, fillchar=fillchar, 
                          max_banner=max_banner, intro_str=intro_str) + se + sb
    
    def get_html_str(self, alpha_ordered=True, numbered=False, intro_str=''):
        M = self.get_model_summ_obj()
        
        
        Me = self.effObj.get_model_summ_obj()
        se = '\n' + Me.html_table_str(alpha_ordered=False, assumptions_first=False)
        
        if self.add_barrier:
            Mb = self.barrierObj.get_model_summ_obj()
            sb = '\n' + Mb.html_table_str(alpha_ordered=alpha_ordered, numbered=numbered, 
                                   intro_str=intro_str)
        else:
            sb = ''
        
        
        return M.html_table_str( alpha_ordered=alpha_ordered, numbered=numbered, intro_str=intro_str)\
                + se + sb
    
    def get_model_summ_obj(self):
        """
        return ModelSummary object for current state of CoreStream instance.
        """
        
        M = ModelSummary( '%s/%s Core Stream Tube'%(self.oxName, self.fuelName) )
        M.add_alt_units('psia', ['MPa','atm','bar'])
        M.add_alt_units('lbf', 'N')
        M.add_alt_units('lbm/s', 'kg/s')
        M.add_alt_units('ft/s', 'm/s')
        M.add_alt_units('sec', ['N-sec/kg', 'km/sec'])
        M.add_alt_units('degR', ['degK','degC','degF'])
        
        M.add_param_fmt('Pexit', '%.4f')
        M.add_param_fmt('Pc', '%.1f')
        
        M.add_out_category( '' ) # show unlabeled category 1st
                
        
        def add_param( name, desc='', fmt='', units='', value=None, category=''):
            
            if name in self.inp_unitsD:
                units = self.inp_unitsD[name]
                
            if desc=='' and name in self.inp_descD:
                desc = self.inp_descD[name]
            
            if value is None:
                value = getattr( self, name )
            
            if self.is_inputD.get(name, False):
                M.add_inp_param( name, value, units, desc, fmt=fmt)
            else:
                M.add_out_param( name, value, units, desc, fmt=fmt, category=category)
        
        for name in self.is_inputD.keys():
            if name not in ['pcentFFC','ko', 'geomObj', 'effObj']:
                add_param( name )
        
        # parameters that are NOT attributes OR are conditional
        if self.add_barrier:
            add_param('FvacBarrier', units='lbf', desc='vacuum thrust due to barrier stream tube')
            
        if self.Pamb > 14.5:
            add_param('Fambient', units='lbf', desc='total sea level thrust')
            add_param('IspAmb', units='sec', desc='delivered sea level Isp' )
            M.add_out_comment('Fambient', '%s'%self.noz_mode )
            M.add_out_comment('IspAmb', '%s'%self.noz_mode )
        elif self.Pamb > 0.0:
            add_param('Fambient', units='lbf', desc='total ambient thrust')
            add_param('IspAmb', units='sec', desc='delivered ambient Isp' )
            M.add_out_comment('Fambient', '%s'%self.noz_mode)
            M.add_out_comment('IspAmb', '%s'%self.noz_mode )
        
        
        if self.effObj('Pulse') < 1.0:
            add_param('IspDelPulse', units='sec', desc='delivered pulsing Isp')

        
        if self.CdThroat_method != 'default':
            M.add_inp_comment('CdThroat', '(%s)'%self.CdThroat_method)
            
        
        if self.add_barrier:
            add_param('wdotFlFFC', units='lbm/s', desc='fuel film coolant flow rate injected at perimeter',
                      category='At Injector Face')
            add_param('wdotFl_cInit', units='lbm/s', desc='initial core fuel flow rate (before any entrainment)',
                      category='At Injector Face')
            add_param('wdotTot_cInit', units='lbm/s', desc='initial core total flow rate (before any entrainment)',
                      category='At Injector Face')
            
            add_param('wdotTot_b', units='lbm/s', desc='total barrier propellant flow rate (includes entrained)',
                      category='After Entrainment')
            add_param('wdotOx_b', units='lbm/s', desc='barrier oxidizer flow rate (all entrained)',
                      category='After Entrainment')
            add_param('wdotFl_b', units='lbm/s', desc='barrier fuel flow rate (FFC + entrained)',
                      category='After Entrainment')
        
            add_param('wdotTot_c', units='lbm/s', desc='total final core propellant flow rate (injected - entrained)',
                      category='After Entrainment')
            add_param('wdotOx_c', units='lbm/s', desc='final core oxidizer flow rate (injected - entrained)',
                      category='After Entrainment')
            add_param('wdotFl_c', units='lbm/s', desc='final core fuel flow rate (injected - entrained)',
                      category='After Entrainment')
            
        
        #add_param('xxx', units='xxx', desc='xxx')
        
        return M

        
if __name__ == '__main__':
    from rocketisp.geometry import Geometry
    from rocketisp.efficiencies import Efficiencies

    geomObj = Geometry(Rthrt=5.868/2,
                       CR=2.5, eps=150,  pcentBell=80, 
                       RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                       LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=16)
    
    effObj = Efficiencies()
    effObj.set_const('Mix', 0.997329)
    effObj.set_const('Em',  0.99644)
    effObj.set_const('Kin', 0.975011)
    effObj.set_const('BL',  0.9795)
    effObj.set_const('Div', 0.994775)
    
    core = CoreStream( geomObj, effObj, oxName='N2O4', fuelName='MMH',  MRcore=1.85,
                 Pc=150, CdThroat=0.995, Pamb=14.7,
                 pcentFFC=14.0, ko=0.035)
    #core.reset_attr('Pc', 456)
    core.summ_print()
