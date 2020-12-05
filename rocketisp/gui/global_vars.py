
import os
from rocketisp.cast import is_bool, is_int, is_float, boolCast, intCast, floatCast

USER_HOME_DIR = os.path.dirname( os.path.expanduser('~/') )
print( 'User Home Directory =',USER_HOME_DIR )
print('')


user_valueD    = {} # key=variable name, value=user's input value
user_unitsD    = {} # key=variable name, value=user's input units
cat_unitsD     = {} # key=variable name, value=category of units (e.g. Length, Mass)
default_valueD = {} # key=variable name, value=default value
unitsD         = {} # key=variable name, value=internal units
descriptionD   = {} # key=variable name, value=long description

efficiencyD    = {} # key=efficiency name, value=efficiency value
eff_constD     = {} # key=efficiency name, value=True/False for is_constant
eff_descD      = {} # key=efficiency name, value=long description

eff_default_valD    = {} # key=efficiency name, value=default efficiency value
eff_default_constD  = {} # key=efficiency name, value=defaullt True/False for is_constant

value_clampD        = {} # key=efficiency name, value=clamp range tuple, e.g. (0.0, 1.0)

# list of propellants in RocketProps
fuelL = ['A50','Ethane','Ethanol','CH4','Methanol','MMH','MHF3','N2H4',
         'NH3','LH2','Propane','UDMH','RP1']
oxidizerL = ['CLF5','F2','IRFNA','LOX','MON10','MON25','MON30','N2O','N2O4']

def reset_vars_to_default():
    for name, v in user_valueD.items():
        user_valueD[name] = default_valueD[name]
        user_unitsD[name] = unitsD[name]
    for name, v in efficiencyD.items():
        efficiencyD[name] = eff_default_valD[name]
        eff_constD[name]  = eff_default_constD[name]

def parse_value( v ):
        #print('parse_value RECEIVING',v, type(v))
        if is_float(v):
            #print( '   passed is_float' )
            v = floatCast(v)
        elif is_int(v):
            #print( '   passed is_int' )
            v = intCast(v)
        elif is_bool( v ):
            #print( '   passed is_bool' )
            v = boolCast( v )
        elif v=='None':
            v = None
        elif v=='False':
            v = False
        elif v=='True':
            v = True
        elif v=='inf':
            v = float('inf')
            
        #print('parse_value returning',v, type(v))
        return v

def set_user_vals_and_units( valD, unitD ):
    for name,v in valD.items():
        v = parse_value( v )    
        #print(name,'=',v,'   type=',type(v))
        user_valueD[name] = v
        
        user_unitsD[name] = unitD.get(name, unitsD[name])
        # if user units not supplied, use default units
        if (not user_unitsD[name]) and unitsD[name]:
            user_unitsD[name] = unitsD[name]
        
def set_eff_vals_and_const( valD, constD ):
    for name,v in valD.items():
        v = parse_value( v )
        #print(name,'=',v,'   type=',type(v))
        efficiencyD[name] = v
        eff_constD[name]  = parse_value( constD.get(name, eff_constD[name]) )
        #print('in set_eff_vals_and_const, ',name,'constant=',eff_constD[name],
        #      type(eff_constD[name]))

GeometryL =  ['Rthrt', 'CR', 'eps', 'pcentBell', 'LnozInp', 'RupThroat', 'RdwnThroat', 
              'RchmConv', 'cham_conv_deg', 'LchmOvrDt', 'LchmMin', 'LchamberInp']
              
CoreStreamL =  [ 'oxName', 'fuelName', 'MRcore', 'Pc', 'CdThroat', 
                 'Pamb', 'adjCstarODE', 'adjIspIdeal', 'ignore_noz_sep']
              
BarrierL =  [  'pcentFFC', 'ko']
                
RocketThrusterL =  ['name',  'noz_regen_eps', 'pulse_sec', 
                    'pulse_quality', 'isRegenCham', 'calc_CdThroat']

InjectorL = ['Tox', 'Tfuel', 'elemEm', 'fdPinjOx', 'fdPinjFuel', 'dpOxInp', 'dpFuelInp', 
             'setNelementsBy', 'elemDensInp', 'NelementsInp', 'OxOrfPerEl', 'FuelOrfPerEl', 
             'lolFuelElem', 'setAcousticFreqBy', 'desAcousMode', 'desFreqInp', 
             'CdOxOrf', 'CdFuelOrf', 'dropCorrOx', 'dropCorrFuel', 'DorfMin', 
             'LfanOvDorfOx', 'LfanOvDorfFuel']


Injector_1L = ['Tox', 'Tfuel']
Injector_2L = ['fdPinjOx', 'fdPinjFuel', 'dpOxInp', 'dpFuelInp'] 
Injector_3L = ['elemEm', 'setNelementsBy', 'elemDensInp', 'NelementsInp', 
               'lolFuelElem',  'DorfMin', 
               'OxOrfPerEl', 'FuelOrfPerEl', 
               'CdOxOrf', 'CdFuelOrf', 'dropCorrOx', 'dropCorrFuel',
               'LfanOvDorfOx', 'LfanOvDorfFuel']
                
Injector_4L = ['setAcousticFreqBy', 'desAcousMode', 'desFreqInp']


class EfficiencyHierarchy:
    def __init__(self, name):
        self.name = name
        self.members_objL = [] # list of member EfficiencyHierarchy objects.
        self.level = 0
    def add_member(self, member):
        self.members_objL.append( member )
    def __str__(self):
        return '<%s, %i members:%s>'%(self.name, self.level, ','.join([m.name for m in self.members_objL]) )

EfficienciesD = {} # key=name, value=EfficiencyHierarchy object

EfficienciesL = ['Isp',  'Noz', 'Div','Kin','BL','TP',   'ERE', 'Mix','Em','Vap','HL',  'FFC','Pulse']

for name in ['IspPulsing'] + EfficienciesL:
    EfficienciesD[name] = EfficiencyHierarchy(name)
EfficienciesD['IspPulsing'].level = 3

for name in ['Div','Kin','BL','TP']:
    EfficienciesD['Noz'].add_member( EfficienciesD[name] )

for name in ['Mix','Em','Vap','HL']:
    EfficienciesD['ERE'].add_member( EfficienciesD[name] )

for name in ['ERE','Noz','FFC']:
    EfficienciesD['Isp'].add_member( EfficienciesD[name] )

for name in ['Isp', 'Pulse']:
    EfficienciesD['IspPulsing'].add_member( EfficienciesD[name] )

# set level of each member
for _ in range(3):
    for n,m in EfficienciesD.items():
        for c in m.members_objL:
            c.level = EfficienciesD[n].level - 1

# clamp input values to indicated range
value_clampD['Rthrt'] = (0.0001, 1.0E6)
value_clampD['CR']    = (1.0, 1.0E6)
value_clampD['eps']   = (1.0, 1.0E6)
value_clampD['pcentBell'] = (40.0, 140.0)
value_clampD['LnozInp'] = (0.0001, 1.0E6)
value_clampD['RupThroat']  = (0.1, 10.0)
value_clampD['RdwnThroat'] = (0.1, 10.0)
value_clampD['RchmConv']   = (0.1, 10.0)
value_clampD['cham_conv_deg'] = (1.0, 80.0)
value_clampD['LchmOvrDt'] = (0.0001, 1.0E6)
value_clampD['LchmMin'] = (0.0001, 1.0E6)
value_clampD['LchamberInp'] = (0.0001, 1.0E6)

value_clampD['MRcore'] = (0.0, 1.0E6)
value_clampD['Pc'] = (0.0001, 1.0E6)
value_clampD['CdThroat'] = (0.0, 1.0)
value_clampD['Pamb'] = (0.0, 1.0E6)
value_clampD['adjCstarODE'] = (0.0001, 1.0E6)
value_clampD['adjIspIdeal'] = (0.0001, 1.0E6)

value_clampD['noz_regen_eps'] = (1.0, 1.0E6)
value_clampD['pulse_sec'] = (0.0001, float('inf'))
value_clampD['pulse_quality'] = (0.0, 1.0)

for eff_name in EfficienciesL:
    value_clampD[eff_name] = (0.0, 1.0)

# ------------ Geometry --------------------
default_valueD["Rthrt"] = 1.0
user_valueD["Rthrt"]    = 1.0
user_unitsD["Rthrt"]    = "in"
unitsD["Rthrt"]         = "in"
descriptionD["Rthrt"]   = "throat radius"
cat_unitsD["Rthrt"]     = "Length"

default_valueD["CR"] = 2.5
user_valueD["CR"]    = 2.5
user_unitsD["CR"]    = ""
unitsD["CR"]         = ""
descriptionD["CR"]   = "chamber contraction ratio (Ainj / Athroat)"
cat_unitsD["CR"]     = ""

default_valueD["eps"] = 20.0
user_valueD["eps"]    = 20.0
user_unitsD["eps"]    = ""
unitsD["eps"]         = ""
descriptionD["eps"]   = "nozzle area ratio (Aexit / Athroat)"
cat_unitsD["eps"]     = ""

default_valueD["pcentBell"] = 80.0
user_valueD["pcentBell"]    = 80.0
user_unitsD["pcentBell"]    = ""
unitsD["pcentBell"]         = ""
descriptionD["pcentBell"]   = "nozzle percent bell (Lnoz / L_15deg_cone)"
cat_unitsD["pcentBell"]     = ""

default_valueD["LnozInp"] = None
user_valueD["LnozInp"]    = None
user_unitsD["LnozInp"]    = "in"
unitsD["LnozInp"]         = "in"
descriptionD["LnozInp"]   = "user input nozzle length (will override pcentBell)"
cat_unitsD["LnozInp"]     = "Length"

default_valueD["RupThroat"] = 1.5
user_valueD["RupThroat"]    = 1.5
user_unitsD["RupThroat"]    = ""
unitsD["RupThroat"]         = ""
descriptionD["RupThroat"]   = "radius of curvature just upstream of throat (Rupstream / Rthrt)"
cat_unitsD["RupThroat"]     = ""

default_valueD["RdwnThroat"] = 1.0
user_valueD["RdwnThroat"]    = 1.0
user_unitsD["RdwnThroat"]    = ""
unitsD["RdwnThroat"]         = ""
descriptionD["RdwnThroat"]   = "radius of curvature just downstream of throat (Rdownstream / Rthrt)"
cat_unitsD["RdwnThroat"]     = ""

default_valueD["RchmConv"] = 1.0
user_valueD["RchmConv"]    = 1.0
user_unitsD["RchmConv"]    = ""
unitsD["RchmConv"]         = ""
descriptionD["RchmConv"]   = "radius of curvature at start of convergent section (Rconv / Rthrt)"
cat_unitsD["RchmConv"]     = ""

default_valueD["cham_conv_deg"] = 30.0
user_valueD["cham_conv_deg"]    = 30.0
user_unitsD["cham_conv_deg"]    = "deg"
unitsD["cham_conv_deg"]         = "deg"
descriptionD["cham_conv_deg"]   = "half angle of conical convergent section"
cat_unitsD["cham_conv_deg"]     = "Angle"

default_valueD["LchmOvrDt"] = 3.0
user_valueD["LchmOvrDt"]    = 3.0
user_unitsD["LchmOvrDt"]    = ""
unitsD["LchmOvrDt"]         = ""
descriptionD["LchmOvrDt"]   = "ratio of chamber length to throat diameter (Lcham / Dthrt)"
cat_unitsD["LchmOvrDt"]     = ""

default_valueD["LchmMin"] = 1.0
user_valueD["LchmMin"]    = 1.0
user_unitsD["LchmMin"]    = "in"
unitsD["LchmMin"]         = "in"
descriptionD["LchmMin"]   = "minimum chamber length (will override LchmOvrDt)"
cat_unitsD["LchmMin"]     = "Length"

default_valueD["LchamberInp"] = None
user_valueD["LchamberInp"]    = None
user_unitsD["LchamberInp"]    = "in"
unitsD["LchamberInp"]         = "in"
descriptionD["LchamberInp"]   = "user input value of chamber length (will override all other entries)"
cat_unitsD["LchamberInp"]     = "Length"

# ------------ CoreStream -----------------
default_valueD["geomObj"] = "Object"
user_valueD["geomObj"]    = "Object"
user_unitsD["geomObj"]    = ""
unitsD["geomObj"]         = ""
descriptionD["geomObj"]   = "Geometry that describes thruster"
cat_unitsD["geomObj"]     = ""

default_valueD["effObj"] = "Object"
user_valueD["effObj"]    = "Object"
user_unitsD["effObj"]    = ""
unitsD["effObj"]         = ""
descriptionD["effObj"]   = "Efficiencies object to hold individual efficiencies"
cat_unitsD["effObj"]     = ""

default_valueD["oxName"] = "N2O4"
user_valueD["oxName"]    = "N2O4"
user_unitsD["oxName"]    = ""
unitsD["oxName"]         = ""
descriptionD["oxName"]   = "name of oxidizer (e.g. N2O4, LOX)"
cat_unitsD["oxName"]     = ""

default_valueD["fuelName"] = "MMH"
user_valueD["fuelName"]    = "MMH"
user_unitsD["fuelName"]    = ""
unitsD["fuelName"]         = ""
descriptionD["fuelName"]   = "name of fuel (e.g. MMH, LH2)"
cat_unitsD["fuelName"]     = ""

default_valueD["MRcore"] = 1.9
user_valueD["MRcore"]    = 1.9
user_unitsD["MRcore"]    = ""
unitsD["MRcore"]         = ""
descriptionD["MRcore"]   = "mixture ratio of core flow (ox flow rate / fuel flow rate)"
cat_unitsD["MRcore"]     = ""

default_valueD["Pc"] = 500.0
user_valueD["Pc"]    = 500.0
user_unitsD["Pc"]    = "psia"
unitsD["Pc"]         = "psia"
descriptionD["Pc"]   = "chamber pressure"
cat_unitsD["Pc"]     = "Pressure"

default_valueD["CdThroat"] = 0.995
user_valueD["CdThroat"]    = 0.995
user_unitsD["CdThroat"]    = ""
unitsD["CdThroat"]         = ""
descriptionD["CdThroat"]   = "Cd of throat (RocketThruster object may override if calc_CdThroat is True)"
cat_unitsD["CdThroat"]     = ""

default_valueD["Pamb"] = 0.0
user_valueD["Pamb"]    = 0.0
user_unitsD["Pamb"]    = "psia"
unitsD["Pamb"]         = "psia"
descriptionD["Pamb"]   = "ambient pressure (for example sea level is 14.7 psia)"
cat_unitsD["Pamb"]     = "Pressure"

default_valueD["adjCstarODE"] = 1.0
user_valueD["adjCstarODE"]    = 1.0
user_unitsD["adjCstarODE"]    = ""
unitsD["adjCstarODE"]         = ""
descriptionD["adjCstarODE"]   = "multiplier on NASA CEA code value of cstar ODE (default is 1.0)"
cat_unitsD["adjCstarODE"]     = ""

default_valueD["adjIspIdeal"] = 1.0
user_valueD["adjIspIdeal"]    = 1.0
user_unitsD["adjIspIdeal"]    = ""
unitsD["adjIspIdeal"]         = ""
descriptionD["adjIspIdeal"]   = "multiplier on NASA CEA code value of Isp ODE (default is 1.0)"
cat_unitsD["adjIspIdeal"]     = ""

default_valueD["pcentFFC"] = 0.0
user_valueD["pcentFFC"]    = 0.0
user_unitsD["pcentFFC"]    = ""
unitsD["pcentFFC"]         = ""
descriptionD["pcentFFC"]   = "percent fuel film cooling (if > 0 then add BarrierStream)"
cat_unitsD["pcentFFC"]     = ""

default_valueD["ko"] = 0.035
user_valueD["ko"]    = 0.035
user_unitsD["ko"]    = ""
unitsD["ko"]         = ""
descriptionD["ko"]   = "entrainment constant (passed to BarrierStream object, range from 0.03 to 0.06)"
cat_unitsD["ko"]     = ""

default_valueD["ignore_noz_sep"] = False
user_valueD["ignore_noz_sep"]    = False
user_unitsD["ignore_noz_sep"]    = ""
unitsD["ignore_noz_sep"]         = ""
descriptionD["ignore_noz_sep"]   = "flag to force nozzle flow separation to be ignored (USE WITH CAUTION)"
cat_unitsD["ignore_noz_sep"]     = ""


# ----------- RocketThruster -------------

default_valueD["name"] = "RocketIsp Thruster"
user_valueD["name"]    = "RocketIsp Thruster"
user_unitsD["name"]    = ""
unitsD["name"]         = ""
descriptionD["name"]   = "name of RocketThruster"
cat_unitsD["name"]     = ""

default_valueD["coreObj"] = "Object"
user_valueD["coreObj"]    = "Object"
user_unitsD["coreObj"]    = ""
unitsD["coreObj"]         = ""
descriptionD["coreObj"]   = "CoreStream object"
cat_unitsD["coreObj"]     = ""

default_valueD["injObj"] = "Object"
user_valueD["injObj"]    = "Object"
user_unitsD["injObj"]    = ""
unitsD["injObj"]         = ""
descriptionD["injObj"]   = "Injector object (optional)"
cat_unitsD["injObj"]     = ""

default_valueD["noz_regen_eps"] = 1.0
user_valueD["noz_regen_eps"]    = 1.0
user_unitsD["noz_regen_eps"]    = ""
unitsD["noz_regen_eps"]         = ""
descriptionD["noz_regen_eps"]   = "regen cooled nozzle area ratio"
cat_unitsD["noz_regen_eps"]     = ""

default_valueD["pulse_sec"] = float('inf')
user_valueD["pulse_sec"]    = float('inf')
user_unitsD["pulse_sec"]    = "s"
unitsD["pulse_sec"]         = "s"
descriptionD["pulse_sec"]   = "duration of pulsing engine (default = infinity)"
cat_unitsD["pulse_sec"]     = "Time"

default_valueD["pulse_quality"] = 0.8
user_valueD["pulse_quality"]    = 0.8
user_unitsD["pulse_quality"]    = ""
unitsD["pulse_quality"]         = ""
descriptionD["pulse_quality"]   = "on a scale of 0.0 to 1.0, how good is engine at pulsing"
cat_unitsD["pulse_quality"]     = ""

default_valueD["isRegenCham"] = False
user_valueD["isRegenCham"]    = False
user_unitsD["isRegenCham"]    = ""
unitsD["isRegenCham"]         = ""
descriptionD["isRegenCham"]   = "flag to indicate chamber is regen cooled"
cat_unitsD["isRegenCham"]     = ""

default_valueD["calc_CdThroat"] = True
user_valueD["calc_CdThroat"]    = True
user_unitsD["calc_CdThroat"]    = ""
unitsD["calc_CdThroat"]         = ""
descriptionD["calc_CdThroat"]   = "flag to trigger calc_CdThroat"
cat_unitsD["calc_CdThroat"]     = ""

# ------------- Injector ------------

default_valueD["Tox"] = None
user_valueD["Tox"]    = None
user_unitsD["Tox"]    = 'degR'
unitsD["Tox"]         = 'degR'
descriptionD["Tox"]   = 'temperature of oxidizer'
cat_unitsD["Tox"]     = 'Temperature'

default_valueD["Tfuel"] = None
user_valueD["Tfuel"]    = None
user_unitsD["Tfuel"]    = 'degR'
unitsD["Tfuel"]         = 'degR'
descriptionD["Tfuel"]   = 'temperature of fuel'
cat_unitsD["Tfuel"]     = 'Temperature'

default_valueD["elemEm"] = 0.8
user_valueD["elemEm"]    = 0.8
user_unitsD["elemEm"]    = ''
unitsD["elemEm"]         = ''
descriptionD["elemEm"]   = 'intra-element Rupe mixing factor (0.7 below ave, 0.8 ave, 0.9 above ave)'
cat_unitsD["elemEm"]     = ''

default_valueD["fdPinjOx"] = 0.25
user_valueD["fdPinjOx"]    = 0.25
user_unitsD["fdPinjOx"]    = ''
unitsD["fdPinjOx"]         = ''
descriptionD["fdPinjOx"]   = 'fraction of Pc used as oxidizer injector pressure drop'
cat_unitsD["fdPinjOx"]     = ''

default_valueD["fdPinjFuel"] = 0.25
user_valueD["fdPinjFuel"]    = 0.25
user_unitsD["fdPinjFuel"]    = ''
unitsD["fdPinjFuel"]         = ''
descriptionD["fdPinjFuel"]   = 'fraction of Pc used as fuel injector pressure drop'
cat_unitsD["fdPinjFuel"]     = ''

default_valueD["dpOxInp"] = None
user_valueD["dpOxInp"]    = None
user_unitsD["dpOxInp"]    = 'psia'
unitsD["dpOxInp"]         = 'psia'
descriptionD["dpOxInp"]   = 'input value of injector pressure drop for oxidizer (overrides fdPinjOx)'
cat_unitsD["dpOxInp"]     = ''

default_valueD["dpFuelInp"] = None
user_valueD["dpFuelInp"]    = None
user_unitsD["dpFuelInp"]    = 'psia'
unitsD["dpFuelInp"]         = 'psia'
descriptionD["dpFuelInp"]   = 'input value of injector pressure drop for fuel (overrides fdPinjFuel)'
cat_unitsD["dpFuelInp"]     = ''

default_valueD["setNelementsBy"] = 'acoustics'
user_valueD["setNelementsBy"]    = 'acoustics'
user_unitsD["setNelementsBy"]    = ''
unitsD["setNelementsBy"]         = ''
descriptionD["setNelementsBy"]   = 'flag determines how to calculate number of elements ( "acoustics", "elem_density", "input")'
cat_unitsD["setNelementsBy"]     = ''

default_valueD["elemDensInp"] = 5.0
user_valueD["elemDensInp"]    = 5.0
user_unitsD["elemDensInp"]    = 'elem/in**2'
unitsD["elemDensInp"]         = 'elem/in**2'
descriptionD["elemDensInp"]   = 'input value for element density (setNelementsBy == "elem_density")'
cat_unitsD["elemDensInp"]     = 'ElementDensity'

default_valueD["NelementsInp"] = 100
user_valueD["NelementsInp"]    = 100
user_unitsD["NelementsInp"]    = ''
unitsD["NelementsInp"]         = ''
descriptionD["NelementsInp"]   = 'input value for number of elements (setNelementsBy == "input")'
cat_unitsD["NelementsInp"]     = ''

default_valueD["OxOrfPerEl"] = 1.0
user_valueD["OxOrfPerEl"]    = 1.0
user_unitsD["OxOrfPerEl"]    = ''
unitsD["OxOrfPerEl"]         = ''
descriptionD["OxOrfPerEl"]   = 'number of oxidizer orifices per element'
cat_unitsD["OxOrfPerEl"]     = ''

default_valueD["FuelOrfPerEl"] = 1.0
user_valueD["FuelOrfPerEl"]    = 1.0
user_unitsD["FuelOrfPerEl"]    = ''
unitsD["FuelOrfPerEl"]         = ''
descriptionD["FuelOrfPerEl"]   = 'number of fuel orifices per element'
cat_unitsD["FuelOrfPerEl"]     = ''

default_valueD["lolFuelElem"] = False
user_valueD["lolFuelElem"]    = False
user_unitsD["lolFuelElem"]    = ''
unitsD["lolFuelElem"]         = ''
descriptionD["lolFuelElem"]   = 'flag for like-on-like fuel element (determines strouhal multiplier)'
cat_unitsD["lolFuelElem"]     = ''

default_valueD["setAcousticFreqBy"] = 'mode'
user_valueD["setAcousticFreqBy"]    = 'mode'
user_unitsD["setAcousticFreqBy"]    = ''
unitsD["setAcousticFreqBy"]         = ''
descriptionD["setAcousticFreqBy"]   = 'flag indicating how to determine design frequency. (can be "mode" or "freq")'
cat_unitsD["setAcousticFreqBy"]     = ''

default_valueD["desAcousMode"] = '3T'
user_valueD["desAcousMode"]    = '3T'
user_unitsD["desAcousMode"]    = ''
unitsD["desAcousMode"]         = ''
descriptionD["desAcousMode"]   = 'driving acoustic mode of injector OR acoustic mode multiplier (setNelementsBy=="acoustics" and setAcousticFreqBy=="mode")'
cat_unitsD["desAcousMode"]     = ''

default_valueD["desFreqInp"] = 5000.0
user_valueD["desFreqInp"]    = 5000.0
user_unitsD["desFreqInp"]    = 'Hz'
unitsD["desFreqInp"]         = 'Hz'
descriptionD["desFreqInp"]   = 'Hz, driving acoustic frequency of injector (sets D/V if setNelementsBy=="acoustics" and setAcousticFreqBy=="freq")'
cat_unitsD["desFreqInp"]     = ''

default_valueD["CdOxOrf"] = 0.75
user_valueD["CdOxOrf"]    = 0.75
user_unitsD["CdOxOrf"]    = ''
unitsD["CdOxOrf"]         = ''
descriptionD["CdOxOrf"]   = 'flow coefficient of oxidizer orifices'
cat_unitsD["CdOxOrf"]     = ''

default_valueD["CdFuelOrf"] = 0.75
user_valueD["CdFuelOrf"]    = 0.75
user_unitsD["CdFuelOrf"]    = ''
unitsD["CdFuelOrf"]         = ''
descriptionD["CdFuelOrf"]   = 'flow coefficient of fuel orifices'
cat_unitsD["CdFuelOrf"]     = ''

default_valueD["dropCorrOx"] = 0.33
user_valueD["dropCorrOx"]    = 0.33
user_unitsD["dropCorrOx"]    = ''
unitsD["dropCorrOx"]         = ''
descriptionD["dropCorrOx"]   = 'oxidizer drop size multiplier (showerhead=3.0, like-doublet=1.0, vortex=0.5, unlike-doublet=0.33)'
cat_unitsD["dropCorrOx"]     = ''

default_valueD["dropCorrFuel"] = 0.33
user_valueD["dropCorrFuel"]    = 0.33
user_unitsD["dropCorrFuel"]    = ''
unitsD["dropCorrFuel"]         = ''
descriptionD["dropCorrFuel"]   = 'fuel drop size multiplier (showerhead=3.0, like-doublet=1.0, vortex=0.5, unlike-doublet=0.33)'
cat_unitsD["dropCorrFuel"]     = ''

default_valueD["DorfMin"] = 0.008
user_valueD["DorfMin"]    = 0.008
user_unitsD["DorfMin"]    = 'in'
unitsD["DorfMin"]         = 'in'
descriptionD["DorfMin"]   = 'minimum orifice diameter (lower limit)'
cat_unitsD["DorfMin"]     = 'Length'

default_valueD["LfanOvDorfOx"] = 20.0
user_valueD["LfanOvDorfOx"]    = 20.0
user_unitsD["LfanOvDorfOx"]    = ''
unitsD["LfanOvDorfOx"]         = ''
descriptionD["LfanOvDorfOx"]   = 'fan length / oxidizer orifice diameter'
cat_unitsD["LfanOvDorfOx"]     = ''

default_valueD["LfanOvDorfFuel"] = 20.0
user_valueD["LfanOvDorfFuel"]    = 20.0
user_unitsD["LfanOvDorfFuel"]    = ''
unitsD["LfanOvDorfFuel"]         = ''
descriptionD["LfanOvDorfFuel"]   = 'fan length / fuel orifice diameter'
cat_unitsD["LfanOvDorfFuel"]     = ''


# ------------- efficiency ------------
efficiencyD["Div"] = 1.0
efficiencyD["Kin"] = 1.0
efficiencyD["BL"] = 1.0
efficiencyD["TP"] = 1.0
efficiencyD["Mix"] = 1.0
efficiencyD["Em"] = 1.0
efficiencyD["Vap"] = 1.0
efficiencyD["HL"] = 1.0
efficiencyD["FFC"] = 1.0
efficiencyD["Pulse"] = 1.0
efficiencyD["ERE"] = 0.98
efficiencyD["Noz"] = 1.0
efficiencyD["Isp"] = 1.0
efficiencyD["Pulse"] = 1.0

eff_constD["Div"] = False
eff_constD["Kin"] = False
eff_constD["BL"] = False
eff_constD["TP"] = False
eff_constD["Mix"] = False
eff_constD["Em"] = False
eff_constD["Vap"] = False
eff_constD["HL"] = False
eff_constD["FFC"] = False
eff_constD["Pulse"] = False
eff_constD["ERE"] = False
eff_constD["Noz"] = False
eff_constD["Isp"] = False
eff_constD["Pulse"] = False

eff_descD["Div"] = "Divergence Efficiency of Nozzle"
eff_descD["Kin"] = "Kinetic Efficiency of Nozzle"
eff_descD["BL"] = "Boundary Layer Efficiency of Nozzle"
eff_descD["TP"] = "Two Phase Efficiency of Nozzle"
eff_descD["Mix"] = "Inter-Element Mixing Efficiency of Injector"
eff_descD["Em"] = "Intra-Element Mixing Efficiency of Injector"
eff_descD["Vap"] = "Vaporization Efficiency of Injector"
eff_descD["HL"] = "Heat Loss Efficiency of Chamber"
eff_descD["FFC"] = "Fuel Film Cooling Efficiency of Chamber"
eff_descD["Pulse"] = "Pulsing Efficiency of Thruster"
eff_descD["ERE"] = "Energy Release Efficiency of Chamber"
eff_descD["Noz"] = "Nozzle Efficiency"
eff_descD["Isp"] = "Overall Isp Efficiency"
eff_descD["Pulse"] = "Pulsing Isp Efficiency"

for name in efficiencyD.keys():
    eff_default_valD[name]    = efficiencyD[name]   #{} # key=efficiency name, value=default efficiency value
    eff_default_constD[name]  = eff_constD[name] #{} # key=efficiency name, value=defaullt True/False for is_constant

if __name__ == "__main__":

    for n,m in EfficienciesD.items():
        print( n, m )
