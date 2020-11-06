from math import pi, sqrt, atan
from rocketcea.cea_obj import CEA_Obj
from rocketprops.rocket_prop import get_prop
from rocketprops.unit_conv_data import get_value # for any units conversions
from rocketisp.efficiency.calc_All_fracKin import calc_IspODK
from rocketisp.efficiency.eff_vaporization import calc_C1_C2, fracVaporized
from rocketisp.efficiency.eff_fuel_film_cooling import solveFractionBarrierFlow
from rocketisp.basic_thruster import USER_INPUT_STR

# acoustic mode multipliers
modeSvnD = {'1T':1.8413,'2T':3.0543,'1R':3.8317,'3T':4.2012,'4T':5.3175,
    '1T1R':5.3313,'2T1R':6.7060,'2R':7.0156,'3T1R':8.0151,'1T2R':8.5263}


class Injector:
    
    def __init__(self, chamber, # Chamber object
        Tox=None, Tfuel=None, Em=0.8,
        fdPinjOx=0.25, fdPinjFuel=0.25,
        elemDensInp=None, NelementsInp=None,
        OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
        lolFuelElem=True, desAcousMode='3T',
        CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
        pcentFFC=None, mrBarrier=1.2,DorfMin=0.008,
        LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0, 
        isRegenCham=0,
        calc_effEm=True, calc_effMix=True, calc_effVap=True, calc_effHL=True, 
        calc_effPulse=True, calc_effFFC=True):
        """
        Injector object holds basic information about the injector portion of the
        thrust chamber and nozzle under investigation.

        :param chamber: Chamber object 
        :param Tox: degR, temperature of oxidizer
        :param Tfuel: degR, temperature of fuel
        :param Em: intra-element Rupe mixing factor
        :param fdPinjOx: fraction of Pc used as oxidizer injector pressure drop
        :param fdPinjFuel: fraction of Pc used as fuel injector pressure drop
        :param elemDensInp: elem/in**2, input value for element density (if None then calculate)
        :param NelementsInp: input value for number of elements (if None then calculate)
        :param OxOrfPerEl: number of oxidizer orifices per element
        :param FuelOrfPerEl: number of fuel orifices per element
        :param lolFuelElem: flag for like-on-like fuel element (determines strouhal multiplier)
        :param desAcousMode: driving acoustic mode of injector OR acoustic mode multiplier
        :param CdOxOrf: flow coefficient of oxidizer orifices
        :param CdFuelOrf: flow coefficient of fuel orifices
        :param dropCorrOx: oxidizer drop size multiplier
        :param dropCorrFuel: fuel drop size multiplier
        :param pcentFFC: percent fuel film cooling ( FFC flowrate / total fuel flowrate)
        :param mrBarrier: mixture ratio of FFC barrier
        :param DorfMin: in, minimum orifice diameter (lower limit)
        :param LfanOvDorfOx: fan length / oxidizer orifice diameter
        :param LfanOvDorfFuel: fan length / fuel orifice diameter
        :param isRegenCham: flag to indicate chamber is regen cooled
        :param calc_effEm: flag to trigger calc_effEm
        :param calc_effMix: flag to trigger calc_effMix
        :param calc_effVap: flag to trigger calc_effVap
        :param calc_effHL: flag to trigger calc_effHL
        :param calc_effPulse: flag to trigger calc_effPulse
        :param calc_effFFC: flag to trigger calc_effFFC
        :type chamber: Chamber
        :type Tox: float
        :type Tfuel: float
        :type Em: float
        :type fdPinjOx: float
        :type fdPinjFuel: float
        :type elemDensInp: float or None
        :type NelementsInp: float or None
        :type OxOrfPerEl: float
        :type FuelOrfPerEl: float
        :type lolFuelElem: bool
        :type desAcousMode: str or float
        :type CdOxOrf: float
        :type CdFuelOrf: float
        :type dropCorrOx: float
        :type dropCorrFuel: float
        :type pcentFFC: float
        :type mrBarrier: float
        :type DorfMin: float
        :type LfanOvDorfOx: float
        :type LfanOvDorfFuel: float
        :type isRegenCham: bool
        :type calc_effEm: bool
        :type calc_effMix: bool
        :type calc_effVap: bool
        :type calc_effHL: bool
        :type calc_effPulse: bool
        :type calc_effFFC: bool
        :return: Injector object
        :rtype: Injector        
        """
        self.chamber        = chamber
        self.thruster       = chamber.thruster
        if Tox is None: Tox = 530.0
        self.Tox            = Tox
        if Tfuel is None: Tfuel = 530.0
        self.Tfuel          = Tfuel
        
        self.Em             = min(1.0, Em) # intra-element mixing parameter for injector
        self.fdPinjOx       = fdPinjOx
        self.fdPinjFuel     = fdPinjFuel
        
        self.elemDensInp    = elemDensInp
        self.NelementsInp   = NelementsInp
        self.OxOrfPerEl     = OxOrfPerEl
        self.FuelOrfPerEl   = FuelOrfPerEl
        
        self.lolFuelElem    = lolFuelElem
        if lolFuelElem:
            self.strouhal_mult = 0.1 # LOL element uses 0.1 strouhal multiplier
        else:
            self.strouhal_mult = 0.2 # unlike element uses 0.2 strouhal multiplier
        
        self.desAcousMode   = desAcousMode
        if desAcousMode in modeSvnD:
            self.desAcousMult = modeSvnD[ desAcousMode ]
        else:
            self.desAcousMult = float( desAcousMode ) # let it raise exception if not a float
        
        self.CdOxOrf        = CdOxOrf
        self.CdFuelOrf      = CdFuelOrf
        self.dropCorrOx     = dropCorrOx
        self.dropCorrFuel   = dropCorrFuel
        self.pcentFFC       = pcentFFC
        self.mrBarrier      = mrBarrier
        self.DorfMin        = DorfMin
        self.LfanOvDorfOx   = LfanOvDorfOx
        self.LfanOvDorfFuel = LfanOvDorfFuel
        self.isRegenCham    = isRegenCham     
        self.calc_effEm    = calc_effEm
        self.calc_effMix   = calc_effMix
        self.calc_effVap   = calc_effVap
        self.calc_effHL    = calc_effHL
        self.calc_effPulse = calc_effPulse
        self.calc_effFFC   = calc_effFFC        

        # build propellant and CEA objects
        self.oxProp = pObj = get_prop( self.thruster.oxName )
        self.fuelProp = pObj = get_prop( self.thruster.fuelName )
        
        # get oxidizer propellant properties
        self.sgOx = self.oxProp.SG_compressed( Tox, self.thruster.Pc )  # g/ml
        self.dHvapOx = self.oxProp.HvapAtTdegR( Tox )     # BTU/lbm
        self.surfOx = self.oxProp.SurfAtTdegR( Tox )      # lbf/in
        
        self.viscOx = self.oxProp.ViscAtTdegR( Tox )      # poise
        self.viscOx = get_value( self.viscOx, 'poise', 'lbm/s/ft')
        
        self.MolWtOx = self.oxProp.MolWt
        
        # get fuel propellant properties
        self.sgFuel = self.fuelProp.SG_compressed( Tfuel, self.thruster.Pc )  # g/ml
        self.dHvapFuel = self.fuelProp.HvapAtTdegR( Tfuel )     # BTU/lbm
        self.surfFuel = self.fuelProp.SurfAtTdegR( Tfuel )      # lbf/in
        self.viscFuel = self.fuelProp.ViscAtTdegR( Tfuel )      # poise
        self.viscFuel = get_value( self.viscFuel, 'poise', 'lbm/s/ft')
        
        self.MolWtFuel = self.fuelProp.MolWt
        
        # --------- start vaporization calcs --------
        self.rhoOx = rho = get_value( self.sgOx, 'SG', 'lbm/in**3' )
        self.rhoFuel = rho = get_value( self.sgFuel, 'SG', 'lbm/in**3' )
        
        self.calc_overall()

    def calc_overall(self):
        
        # recalc Chamber in case a basic parameter has changed.
        self.chamber.calc_overall()
        
        self.calc_element_attr() # e.g. Nelements, injection velocities, elements diam, etc.
        
        # calc intra-element mixing efficiency and reset BasicThruster effEm
        if self.calc_effEm:
            effEm = self.calculate_effEm() # calc intra-element mixing efficiency
            self.thruster.reset_attr( 'effEm', effEm, method_name='RocketIsp (Em=%g)'%self.Em, 
                                      call_calc_overall=True)
                                      
        # calc inter-element mixing efficiency
        if self.calc_effMix:
            effMix = self.calculate_effMix() # calc inter-element mixing efficiency (2 deg estimate)
            self.thruster.reset_attr( 'effMix', effMix, method_name='RocketIsp (mixAngle=%.2f deg)'%self.mixAngle, 
                                      call_calc_overall=True)
        
        # vaporization efficiency
        if self.calc_effVap:
            effVap = self.calculate_effVap()
            self.thruster.reset_attr( 'effVap', effVap, method_name='RocketIsp', 
                                      call_calc_overall=True)
        
        # fuel film cooling
        if self.calc_effFFC:
            if self.pcentFFC is None:
                raise Exception('Can not calculate effFFC if input value of pcentFFC is None')
            effFFC = self.calculate_effFFC()
            self.thruster.reset_attr( 'effFFC', effFFC, method_name='RocketIsp (%%FFC=%g)'%self.pcentFFC, 
                                      call_calc_overall=True)
        
        # recalc Chamber in case a basic parameter has changed.
        self.chamber.calc_overall()
    
    def calculate_effFFC(self, call_basic_calc_overall=True):
        self.mrEngine = self.thruster.MR * (100.0 - self.pcentFFC)/100.0
        self.fracWdotBarr = solveFractionBarrierFlow(self.pcentFFC, self.thruster.MR, self.mrBarrier)

        barrIsp = self.thruster.ceaObj.get_Isp( Pc=self.thruster.Pc, MR=self.mrBarrier, eps=self.thruster.eps)
        fCore = 1.0 - self.fracWdotBarr
        etaFFC = (self.fracWdotBarr * barrIsp + fCore * self.thruster.IspODE) / self.thruster.IspODE
        
        self.Tbarrier = self.thruster.ceaObj.get_Tcomb(Pc=self.thruster.Pc, MR=self.mrBarrier)
        
        return etaFFC

    
    def calculate_effVap(self, call_basic_calc_overall=True):
        # calculate vaporization efficiency
        self.C1fuel, self.C2fuel = calc_C1_C2(self.fuelProp, self.Tfuel, self.rhoFuel, self.dHvapFuel, 
                                              self.surfFuel, self.viscFuel, self.MolWtFuel)
        print('C1fuel=%g, C2fuel=%g'%(self.C1fuel, self.C2fuel)  )
        
        self.C1ox, self.C2ox = calc_C1_C2(self.oxProp, self.Tox, self.rhoOx, self.dHvapOx, 
                                          self.surfOx, self.viscOx, self.MolWtOx)
        print('C1ox=%g, C2ox=%g'%(self.C1ox, self.C2ox)  )
            
        # now figure out dropo sizes
        #C  MEDIAN DROPLET RADIUS
        self.rDropOx = 0.05 * self.DorfOx * self.C1ox * self.dropCorrOx
        self.rDropFuel = 0.05 * self.DorfFuel * self.C1fuel * self.dropCorrFuel
        
        CR = self.chamber.CR
        #C  CHAMBER SHAPE FACTOR
        self.ShapeFact = (1.0 + 1.0/sqrt(CR) + 1./ CR )/3.

        #C  GENERALIZED VAPORIZATION LENGTH
        CFX = (self.chamber.Lcham_cyl/CR**.44 + .83*self.chamber.Lcham_conv/(CR**.22 * self.ShapeFact**.33))\
            *(self.thruster.Pc/300.)**.66
        self.genVapLenOx = CFX/(self.C2ox*(self.rDropOx/.003)**1.45 * (self.velOx_ips/1200.)**.75)
        self.genVapLenFuel = CFX/(self.C2fuel*(self.rDropFuel/.003)**1.45 * (self.velFuel_ips/1200.)**.75)
        
        self.fracVapOx = fracVaporized( self.genVapLenOx )
        self.fracVapFuel = fracVaporized( self.genVapLenFuel )

        
        # get vaporized MR
        self.mrVap = self.thruster.MR * self.fracVapOx / self.fracVapFuel
        
        self.fracVapTot = (self.fracVapOx*self.thruster.wdotOx + self.fracVapFuel*self.thruster.wdotFl) / \
                          self.thruster.wdotTot
        
        if self.fracVapTot < 1.0:
            vapIsp = self.thruster.ceaObj.get_Isp( Pc=self.thruster.Pc, MR=self.mrVap, eps=self.thruster.eps)
            effVap = min(1.0, self.fracVapTot * vapIsp / self.thruster.IspODE)
        else:
            effVap = 1.0
            
        return effVap

    
    def calculate_effEm(self, call_basic_calc_overall=True):
        # calc inter-element mixing efficiency
        if self.Em >= 1.0:
            self.effEm = 1.0
            return 1.0
        
        mrLow = self.thruster.MR * self.Em
        mrHi = self.thruster.MR / self.Em
        
        IspODK = calc_IspODK(self.thruster.ceaObj, Pc=self.thruster.Pc, eps=self.thruster.eps, Rthrt=self.thruster.Rthrt, 
                                    pcentBell=self.thruster.pcentBell, MR=self.thruster.MR)
        
        odkLowIsp = calc_IspODK(self.thruster.ceaObj, Pc=self.thruster.Pc, eps=self.thruster.eps, Rthrt=self.thruster.Rthrt, 
                                     pcentBell=self.thruster.pcentBell, MR=mrLow)
        odkHiIsp = calc_IspODK(self.thruster.ceaObj, Pc=self.thruster.Pc, eps=self.thruster.eps, Rthrt=self.thruster.Rthrt, 
                                    pcentBell=self.thruster.pcentBell, MR=mrHi)
                                  
        xm1=(1.+mrLow)/(1.+self.Em)/(1.+self.thruster.MR)
        xm2=1.0-xm1
        effEm = (xm1*odkLowIsp + xm2*odkHiIsp) / IspODK

        return effEm
            
    def calculate_effMix(self):
        """calc inter-element mixing efficiency"""
        
        DiamElem =  self.chamber.Dinj * sqrt(pi/4.0/self.Nelements) - (self.DorfOx+self.DorfFuel)/2.0
        DiamElem = max(DiamElem,0.0)
        self.mixAngle = atan( DiamElem / self.chamber.Lcham )*(180.0/pi)
        effMix = 1. - .01*(self.mixAngle/2.)**2
        return effMix
    
    def calc_element_attr(self):
        """calc Nelements, injection velocities, elements diam, etc."""
        self.dpOx = self.fdPinjOx * self.thruster.Pc
        self.dpFuel = self.fdPinjFuel * self.thruster.Pc
        
        # calc chamber sonic velocity
        aODE = self.thruster.ceaObj.get_SonicVelocities(Pc=self.thruster.Pc, 
                                                       MR=self.thruster.MR,
                                                       eps=self.thruster.eps)[0]
        self.sonicVel = aODE * 0.9
        
        velFl_ips = sqrt( 24.0 * 32.174 * self.dpFuel / self.rhoFuel ) # in/sec
        
        self.des_freq = self.desAcousMult * self.sonicVel / pi / (self.chamber.Dinj/12.0)
        self.dOrifFl_desHz = self.strouhal_mult * velFl_ips / self.des_freq
        
        self.dOrifMin = max(self.DorfMin, self.dOrifFl_desHz)
        
        # calc number of elements and element density
        if self.NelementsInp:
            self.Nelements = self.NelementsInp
            self.NOxOrf = max( 1.0, self.Nelements * self.OxOrfPerEl)
            self.NFuelOrf = max( 1.0, self.Nelements * self.FuelOrfPerEl)
            self.elemDensCalc = self.Nelements / self.chamber.Ainj
        
        elif self.elemDensInp == None:
            wdotFlOrif = velFl_ips * self.rhoFuel * self.CdFuelOrf * self.dOrifMin**2 * pi / 4.0
            
            self.NFuelOrf = float(int( 0.5 + max(1.0, self.thruster.wdotFl / wdotFlOrif)))
            self.Nelements = max(1.0, self.NFuelOrf / self.FuelOrfPerEl)
            self.NOxOrf = max( 1.0, self.Nelements * self.OxOrfPerEl)
            self.elemDensCalc = self.Nelements / self.chamber.Ainj
            
        else:
            self.Nelements =float(int( 0.5 +  max( 1.0, self.elemDensInp * self.chamber.Ainj )))
            self.NOxOrf = max( 1.0, self.Nelements * self.OxOrfPerEl)
            self.NFuelOrf = max( 1.0, self.Nelements * self.FuelOrfPerEl)
            self.elemDensCalc = self.elemDensInp
            
        gcc = 32.174 * 12.0 * 2.0
        PIO4 = pi / 4.0
        self.velOx_ips = sqrt(gcc*self.dpOx/self.rhoOx)  # in/sec
        self.velFuel_ips = sqrt(gcc*self.dpFuel/self.rhoFuel) # in/sec
        self.AfloOx = self.thruster.wdotOx/(self.rhoOx*self.CdOxOrf*self.velOx_ips)
        self.AfloFuel = self.thruster.wdotFl/(self.rhoFuel*self.CdFuelOrf*self.velFuel_ips)
        self.DorfOx = sqrt(self.AfloOx/(PIO4*self.NOxOrf))
        self.DorfFuel = sqrt(self.AfloFuel/(PIO4*self.NFuelOrf))

        self.velOx_fps   = self.velOx_ips / 12.0  # convert from in/sec to ft/sec
        self.velFuel_fps = self.velFuel_ips / 12.0 # convert from in/sec to ft/sec

        
    def summ_print(self):
        self.chamber.summ_print()
        print('---------------%s/%s injector-----------------------'%(self.thruster.oxName, self.thruster.fuelName))

        if self.DorfFuel < self.dOrifMin:
            print( 'WARNING... Fuel Orifice is Less Than D/V Requirement of %g inches'%self.dOrifFl_desHz )
        else:
            print( 'Fuel Orifice Meets D/V Requirement of Greater Than %g inches'%self.dOrifFl_desHz )
        print('-------------------------------------------------------')
        
        
        
        print('           Tox =', '%g'%self.Tox, 'degR, temperature of oxidizer')
        print('         Tfuel =', '%g'%self.Tfuel, 'degR, temperature of fuel')
        print('            Em =', '%s'%self.Em, 'Rupe factor of injector')
        print('      fdPinjOx =', '%g'%self.fdPinjOx, '')
        print('    fdPinjFuel =', '%g'%self.fdPinjFuel, '')
        print('    OxOrfPerEl =', '%g'%self.OxOrfPerEl, '')
        print('  FuelOrfPerEl =', '%g'%self.FuelOrfPerEl, '')
        print('   lolFuelElem =', '%s'%self.lolFuelElem, '')
        print('  desAcousMode =', '%s'%self.desAcousMode, '(mult=%g)'%self.desAcousMult)
        print('       CdOxOrf =', '%g'%self.CdOxOrf, '')
        print('     CdFuelOrf =', '%g'%self.CdFuelOrf, '')
        print('    dropCorrOx =', '%g'%self.dropCorrOx, '')
        print('  dropCorrFuel =', '%g'%self.dropCorrFuel, '')
        print('       DorfMin =', '%g'%self.DorfMin, 'in')
        print('  LfanOvDorfOx =', '%g'%self.LfanOvDorfOx, '')
        print('LfanOvDorfFuel =', '%g'%self.LfanOvDorfFuel, '')
        print('   isRegenCham =', '%s'%self.isRegenCham, '')
        print()
        print('          sgOx =', '%g'%self.sgOx, 'g/ml')
        print('       dHvapOx =', '%g'%self.dHvapOx, 'BTU/lbm')
        print('        surfOx =', '%g'%self.surfOx, 'lbf/in')
        print('        viscOx =', '%g'%self.viscOx, 'poise')
        print('       MolWtOx =', '%g'%self.MolWtOx, 'g/gmole')
        print()
        print('        sgFuel =', '%g'%self.sgFuel, 'g/ml')
        print('     dHvapFuel =', '%g'%self.dHvapFuel, 'BTU/lbm')
        print('      surfFuel =', '%g'%self.surfFuel, 'lbf/in')
        print('      viscFuel =', '%g'%self.viscFuel, 'poise')
        print('     MolWtFuel =', '%g'%self.MolWtFuel, 'g/gmole') 
        print(' cham sonicVel =', '%g'%self.sonicVel, 'ft/sec') 
        print()
        print('          dpOx =', '%g'%self.dpOx, 'psid') 
        print('        dpFuel =', '%g'%self.dpFuel, 'psid') 
        
        
        print(' cham des_freq =', '%g'%self.des_freq, 'Hz') 
        print(' dOrifFl_desHz =', '%.4f'%self.dOrifFl_desHz, 'in, fuel orifice designed by Hewitt Corr.') 
        print('      dOrifMin =', '%.4f'%self.dOrifMin, 'in, minimum orifice diam allowed by stability') 

        print('     Nelements =', '%g'%self.Nelements, '') 
        print('      NFuelOrf =', '%g'%self.NFuelOrf, '') 
        print('        NOxOrf =', '%g'%self.NOxOrf, '') 
        print('      elemDens =', '%g'%self.elemDensCalc, 'elem/in**2') 
        
        print('         velOx =', '%g'%self.velOx_fps, 'ft/sec') 
        print('       velFuel =', '%g'%self.velFuel_fps, 'ft/sec') 
        print('        AfloOx =', '%g'%self.AfloOx, 'in**2') 
        print('      AfloFuel =', '%g'%self.AfloFuel, 'in**2') 
        print('        DorfOx =', '%.4f'%self.DorfOx, 'in') 
        print('      DorfFuel =', '%.4f'%self.DorfFuel, 'in') 
        
        if self.calc_effFFC:
            print('        ---')
            print('      pcentFFC =', '%s'%self.pcentFFC, '%')
            print('        mrCore =', '%g'%self.thruster.MR, '')
            print('     mrBarrier =', '%g'%self.mrBarrier, '')
            print('      mrEngine =', '%g'%self.mrEngine, 'weighted ave of core and barrier')
            print('      Tbarrier =', '%g'%self.Tbarrier, 'degR')
            
            print('  fracWdotBarr =', '%g'%self.fracWdotBarr, '')

        if self.calc_effVap:
            # only print internal vaporization values if calc'd
            print('        ---')
            print('       rDropOx =', '%g'%get_value(self.rDropOx,'inch','mil'), 'mil, median ox droplet radius') 
            print('     rDropFuel =', '%g'%get_value(self.rDropFuel,'inch','mil'), 'mil, median fuel droplet radius') 
            
            print(' chamShapeFact =', '%g'%self.ShapeFact, '') 
            
            print('   genVapLenOx =', '%g'%self.genVapLenOx, '')
            print(' genVapLenFuel =', '%g'%self.genVapLenFuel, '')
            print('     fracVapOx =', '%g'%self.fracVapOx, '')
            print('   fracVapFuel =', '%g'%self.fracVapFuel, '')
            
            print('         mrVap =', '%g'%self.mrVap, 'vaporized mixture ratio')
        
        
        #print(' xxx =', '%g'%self.xxx, 'xxx')
        

if __name__ == '__main__':
    from rocketisp.basic_thruster import BasicThruster
    from rocketisp.chamber import Chamber
    
    bt = BasicThruster( oxName='N2O4', fuelName='MMH',  MR=1.85,
        Pc=150, eps=150, Rthrt=0.5, pcentBell=80,
        effMix=1.0, effVap=1.0, effHL=0.978, effEm=1.0,
        effDiv=0.992194, effTP=1.0, effKin=1.0, effBL=0.979593,
        effPulse=1.0, # assume chamber is not pulsing 
        effFFC=1.0,   # Fuel Film Cooling (i.e. Barrier Cooling)
        isRegenCham=0, noz_regen_eps=1.0) # regen cooling decreases boundary layer loss.
    bt.calc_eff_nozzle()
    C = Chamber(bt, FvacLbf=7635.25, LchamberInp=16.0)
    
    I = Injector(C, Em=0.8, fdPinjOx=0.3, fdPinjFuel=0.3, elemDensInp=10.0, #NelementsInp=676,
                 calc_effEm=True, calc_effMix=True, calc_effVap=True, calc_effHL=True, 
                 calc_effPulse=True, calc_effFFC=True, pcentFFC=14, mrBarrier=0.7)
    I.summ_print()
    