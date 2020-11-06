from math import pi
import os

if os.environ.get('READTHEDOCS',False):
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
        
        self.Twall = self.ceaObj.get_Tcomb( Pc=self.coreObj.Pc, MR=self.MRwall)
        
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
        self.effNoz_b = self.effKin_b * effObj('Div') * effObj('BL') * effObj('TP')
        
        self.effERE_b = effObj('Vap') * effObj('Mix') * effObj('Em') * effObj('HL')
        
        self.effIsp_b = self.effNoz_b * self.effERE_b
        self.IspDel_b = self.effIsp_b * self.IspODE_b
        self.cstarERE_b = self.cstarODE_b * self.effERE_b
        
    
    def summ_print(self):
        """
        print to standard output, the current state of BarrierStream instance.
        """
        
        print('---------------%s/%s barrier stream-----------------------'%\
             (self.coreObj.oxName, self.coreObj.fuelName))
             
        if self.warningL:
            for warn in self.warningL:
                print(warn)
            print('----------------------------------------------------------')
             
        print('    pcentFFC =', '%g'%self.pcentFFC, '%')
        print('   MRbarrier =', '%g'%self.MRbarrier, '')
        print('      MRwall =', '%g'%self.MRwall, '')
        print('       Twall =', '%.1f'%self.Twall, 'degR (TcBarrier=%.1f degR)'%self.TcODE_b)
        print('   effnessFC =', '%g'%self.effnessFC)
        print('WentrOvWcool =', '%g'%self.WentrOvWcool)
        print('    IspDel_b =', '%.2f'%self.IspDel_b, 'sec delivered vacuum barrier Isp')
        print('    IspODF_b =', '%.2f'%self.IspODF_b, 'sec')
        print('    IspODK_b =', '%.2f'%self.IspODK_b, 'sec (fracKin=%g)'%self.fracKin_b)
        print('    IspODE_b =', '%.2f'%self.IspODE_b, 'sec')
        print('  cstarERE_b =', '%.1f'%self.cstarERE_b, 'ft/sec')
        print('  cstarODE_b =', '%.1f'%self.cstarODE_b, 'ft/sec')
        
class CoreStream:
    """
        Core stream tube of liquid bipropellant thruster.

        :param geomObj: Geometry that describes thruster
        :param effObj: Efficiencies object to hold individual efficiencies
        :param oxName: name of oxidizer (e.g. N2O4, LOX)
        :param fuelName: name of fuel (e.g. MMH, LH2)
        :param MRcore: mixture ratio of core flow (ox flow rate / fuel flow rate)
        :param Pc: psia, chamber pressure
        :param CdThroat: Cd of throat (RocketThruster object may override if calc_CdThroat is True)
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
        
        self.evaluate()
        
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
            raise Exception('Attempting to set un-authorized Geometry attribute named "%s"'%name )
            
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
            effERE_core = effERE_core / self.effObj('FFC')

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
        
        self.wdotTotcore = self.Pc * self.Atcore * self.CdThroat * 32.174 / cstarERE_core
        self.wdotOxCore  = self.wdotTotcore * self.MRcore / (1.0 + self.MRcore)
        self.wdotFlCore = self.wdotTotcore - self.wdotOxCore
        
        self.FvacCore = self.wdotTotcore * self.IspDel_core
        self.FvacTotal = self.FvacCore + self.FvacBarrier

        self.wdotTot = self.wdotTotcore + self.wdotTot_b
        self.wdotOx  = self.wdotOxCore + self.wdotOx_b
        self.wdotFl = self.wdotFlCore + self.wdotFl_b

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
        self.geomObj.summ_print()
        print('---------------%s/%s core stream-----------------------'%(self.oxName, self.fuelName))
        print('    FvacTotal =', '%.2f'%self.FvacTotal, 'lbf')
        print('     FvacCore =', '%.2f'%self.FvacCore, 'lbf')
        if self.Pamb > 0.0:
            if self.Pamb > 14.5:
                print('     FseaLevel =', '%.2f'%self.Fambient, 'lbf, (Pamb=%g)'%self.Pamb)
            else:
                print('      Fambient =', '%.2f'%self.Fambient, 'lbf, (Pamb=%g)'%self.Pamb)
        
        if self.add_barrier:
            print('  FvacBarrier =', '%.2f'%self.FvacBarrier, 'lbf')
        print('   MRthruster =', '%g'%self.MRthruster, '')
        print('       MRcore =', '%g'%self.MRcore, '')
        if self.add_barrier:
            print('    MRbarrier =', '%g'%self.barrierObj.MRbarrier, '')
        print('           Pc =', '%g'%self.Pc, 'psia')
        
        # -------------------- Isp --------------------------
        print('=====> IspDel =', '%.2f'%self.IspDel, 'sec, ___DELIVERED VACUUM ISP___')
        
        if True:#self.Pamb > 0.0:
            print('       IspAmb =', '%.2f'%self.IspAmb, 'sec, (Pamb=%.4f) %s'%(self.Pamb, self.noz_mode))
            #print('        Pexit =', '%.4f'%self.Pexit, 'psia, Nozzle Exit Pressure')
        
        if self.effObj('Pulse') < 1.0:
            print('  IspDelPulse =', '%.2f'%self.IspDelPulse, 'sec, ___DELIVERED PULSING ISP___')
        
        print('   IspDelCore =', '%.2f'%self.IspDel_core, 'sec')
        print('       IspODF =', '%.2f'%self.IspODF, 'sec')
        print('       IspODK =', '%.2f'%self.IspODK, 'sec (fracKin=%g)'%self.fracKin)
        print('       IspODE =', '%.2f'%self.IspODE, 'sec')
        print('===> cstarERE =', '%.1f'%self.cstarERE, 'ft/sec, measured cstar = cstarERE / CdThroat')
        print('     cstarODE =', '%.1f'%self.cstarODE, 'ft/sec')
        print()
        
        print('   CfVacIdeal =', '%.5f'%self.CfVacIdeal, 'Ideal Vacuum Thrust Coefficient')
        print('     CfVacDel =', '%.5f'%self.CfVacDel, 'Delivered Vacuum Thrust Coefficient')
        print('     CfAmbDel =', '%.5f'%self.CfAmbDel, 'Delivered Ambient  Thrust Coefficient')
        print()
        
        # -------------------- efficiencies -----------------------
        self.effObj.summ_print()
        
        # --------------------- Flow Rates -------------------------
        print()
        #print('       oxName =', '%s'%self.oxName, '')
        #print('     fuelName =', '%s'%self.fuelName, '')
        print('     CdThroat =', '%g'%self.CdThroat, '(%s)'%self.CdThroat_method, 'throat flow coefficient')
        
        # -------------------------- Fuel Film Cooloing ------------------
        if self.add_barrier:
            print('      wdotTot =', '%g'%self.wdotTot, 'lbm/sec (O/F = %g)'%( self.wdotOx/self.wdotFl, ))
            print('  wdotTotCore =', '%g'%self.wdotTotcore, 'lbm/sec (O/F = %g)'%( self.wdotOxCore/self.wdotFlCore, ))
            print('  wdotTotBarr =', '%g'%self.wdotTot_b, 'lbm/sec (O/F = %g)'%( self.wdotOx_b/self.wdotFl_b, ))
            
            print('  wdotOxTotal =', '%g'%self.wdotOx, 'lbm/sec')
            print('   wdotOxCore =', '%g'%self.wdotOxCore, 'lbm/sec')
            print('   wdotOxBarr =', '%g'%self.wdotOx_b, 'lbm/sec')
            
            print('  wdotFlTotal =', '%g'%self.wdotFl, 'lbm/sec')
            print('   wdotFlCore =', '%g'%self.wdotFlCore, 'lbm/sec')
            print('   wdotFlBarr =', '%g'%self.wdotFl_b, 'lbm/sec')
        else:
            print('      wdotTot =', '%g'%self.wdotTot, 'lbm/sec (O/F = %g)'%( self.wdotOx/self.wdotFl, ))
            print('       wdotOx =', '%g'%self.wdotOx, 'lbm/sec')
            print('       wdotFl =', '%g'%self.wdotFl, 'lbm/sec')

        
        # ------------------- gas properties ------------------
        print('        TcODE =', '%.1f'%self.TcODE, 'degR')
        print('        MWchm =', '%g'%self.MWchm, 'g/gmole')
        print('     gammaChm =', '%g'%self.gammaChm, '')
        
        if self.add_barrier:
            self.barrierObj.summ_print()

        
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
                 Pc=150, CdThroat=0.995,
                 pcentFFC=14.0, ko=0.035)
    #core.reset_attr('Pc', 456)
    core.summ_print()
