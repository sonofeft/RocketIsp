from math import pi, sqrt
from rocketcea.cea_obj import CEA_Obj
from rocketprops.rocket_prop import get_prop
from rocketprops.unit_conv_data import get_value # for any units conversions

# acoustic mode multipliers
modeSvnD = {'1T':1.8413,'2T':3.0543,'1R':3.8317,'3T':4.2012,'4T':5.3175,
    '1T1R':5.3313,'2T1R':6.7060,'2R':7.0156,'3T1R':8.0151,'1T2R':8.5263}


class Chamber:
    
    def __init__(self, oxName='N2O4', fuelName='MMH', 
        Pc=500, MR=1.5, 
        FvacLbf=500., CR=2.5, LchmOvrDt=4.0, LchmMin=1.0,
        Tox=None, Tfuel=None, Em=0.8,
        fdPinjOx=0.25, fdPinjFuel=0.25, 
        OxOrfPerEl=1.0, FuelOrfPerEl=1.0, lolFuelElem=True, desAcousMode='3T',
        CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
        pcentFFC=None, mrBarrier=1.2,DorfMin=0.008,
        LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0, 
        isRegenCham=0):
        """
        Chamber object holds basic information about the chamber portion of the
        thrust chamber and nozzle under investigation.

        :param oxName: oxidizer name
        :param fuelName: fuel name
        :param Pc: psia, chamber pressure
        :param MR: mixture ratio (ox flowrate / fuel flowrate)
        :param FvacLbf: lbf, vacuum thrust
        :param CR: chamber contraction ratio (Ainj / At)
        :param LchmOvrDt: chamber length / throat diam (Lchm / Dt)
        :param LchmMin: in, minimum chamber length
        :param Tox: degR, temperature of oxidizer
        :param Tfuel: degR, temperature of fuel
        :param Em: description of Em
        :param fdPinjOx: fraction of Pc used as oxidizer injector pressure drop
        :param fdPinjFuel: fraction of Pc used as fuel injector pressure drop
        :param OxOrfPerEl: number of oxidizer orifices per element
        :param FuelOrfPerEl: number of fuel orifices per element
        :param lolFuelElem: flag for like-on-like fuel element (determines strouhal number)
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
        :type oxName: str
        :type fuelName: str
        :type Pc: float
        :type MR: float
        :type FvacLbf: float
        :type CR: float
        :type LchmOvrDt: float
        :type LchmMin: float
        :type Tox: float
        :type Tfuel: float
        :type Em: float
        :type fdPinjOx: float
        :type fdPinjFuel: float
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
        :return: Chamber object
        :rtype: Chamber        
        """
        self.oxName         = oxName
        self.fuelName       = fuelName
        self.Pc             = Pc
        self.MR             = MR
        self.FvacLbf        = FvacLbf
        self.CR             = CR
        self.LchmOvrDt      = LchmOvrDt
        self.LchmMin        = LchmMin
        if Tox is None: Tox = 530.0
        self.Tox            = Tox
        if Tfuel is None: Tfuel = 530.0
        self.Tfuel          = Tfuel
        self.Em             = Em
        self.fdPinjOx        = fdPinjOx
        self.fdPinjFuel      = fdPinjFuel
        self.OxOrfPerEl     = OxOrfPerEl
        self.FuelOrfPerEl   = FuelOrfPerEl
        self.lolFuelElem    = lolFuelElem
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

        # build propellant and CEA objects
        self.oxProp = pObj = get_prop( oxName )
        self.fuelProp = pObj = get_prop( fuelName )
        self.ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)
        
        # get oxidizer propellant properties
        self.sgOx = self.oxProp.SG_compressed( Tox, Pc )  # g/ml
        self.dHvapOx = self.oxProp.HvapAtTdegR( Tox )     # BTU/lbm
        self.surfOx = self.oxProp.SurfAtTdegR( Tox )      # lbf/in
        self.viscOx = self.oxProp.ViscAtTdegR( Tox )      # poise
        self.MolWtOx = self.oxProp.MolWt
        
        # get fuel propellant properties
        self.sgFuel = self.fuelProp.SG_compressed( Tfuel, Pc )  # g/ml
        self.dHvapFuel = self.fuelProp.HvapAtTdegR( Tfuel )     # BTU/lbm
        self.surfFuel = self.fuelProp.SurfAtTdegR( Tfuel )      # lbf/in
        self.viscFuel = self.fuelProp.ViscAtTdegR( Tfuel )      # poise
        self.MolWtFuel = self.fuelProp.MolWt
        
        # --------- start vaporization calcs --------
        self.rhoOx = rho = get_value( self.sgOx, 'SG', 'lbm/in**3' )
        self.rhoFuel = rho = get_value( self.sgFuel, 'SG', 'lbm/in**3' )
        
    def summ_print(self):
        print('        oxName =', '%s'%self.oxName, '')
        print('      fuelName =', '%s'%self.fuelName, '')
        print('            Pc =', '%g'%self.Pc, 'psia')
        print('            MR =', '%g'%self.MR, '')
        print('       FvacLbf =', '%g'%self.FvacLbf, 'lbf')
        print('            CR =', '%g'%self.CR, '')
        print('     LchmOvrDt =', '%g'%self.LchmOvrDt, '')
        print('       LchmMin =', '%g'%self.LchmMin, 'in')
        print('           Tox =', '%g'%self.Tox, 'degR')
        print('         Tfuel =', '%g'%self.Tfuel, 'degR')
        print('            Em =', '%g'%self.Em, '')
        print('       fdPinjOx =', '%g'%self.fdPinjOx, '')
        print('     fdPinjFuel =', '%g'%self.fdPinjFuel, '')
        print('    OxOrfPerEl =', '%g'%self.OxOrfPerEl, '')
        print('  FuelOrfPerEl =', '%g'%self.FuelOrfPerEl, '')
        print('   lolFuelElem =', '%s'%self.lolFuelElem, '')
        print('  desAcousMode =', '%s'%self.desAcousMode, '(mult=%g)'%self.desAcousMult)
        print('       CdOxOrf =', '%g'%self.CdOxOrf, '')
        print('     CdFuelOrf =', '%g'%self.CdFuelOrf, '')
        print('    dropCorrOx =', '%g'%self.dropCorrOx, '')
        print('  dropCorrFuel =', '%g'%self.dropCorrFuel, '')
        print('      pcentFFC =', '%s'%self.pcentFFC, '%')
        print('     mrBarrier =', '%g'%self.mrBarrier, '')
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
if __name__ == '__main__':
    
    C = Chamber()
    C.summ_print()
    