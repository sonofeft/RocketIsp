"""
model the SSME
"""
from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.examples.compare_vals import compare_header, compare

xxx = 0
Fvac = 512300
FseaLevel = 418000 # lbf

MRcore = 6.05485
Rthrt = 5.1527 # in
Tc = xxx # R
Pc = 3225 # 2994 # psia
wdotFuel =  xxx # lbm/sec
wdotOx   = xxx # lbm/sec

cstarEff = xxx
cstar = xxx # ft/sec
Isp = 452.3 # sec
IspSL = 366 # sec
cstarODE = xxx / 12.0 # ft/sec
eps = 77.5
CR = 3.0
Lnoz = 121 # in


geomObj = Geometry(Rthrt=Rthrt,
                   CR=CR, eps=eps,  pcentBell=80, LnozInp=Lnoz,
                   RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
                   LchmOvrDt=2.4842/2, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()
effObj.set_const('ERE', 0.99 )

core = CoreStream( geomObj, effObj, oxName='LOX', fuelName='LH2',  MRcore=MRcore,
             Pc=Pc, ignore_noz_sep=True)
             

R = RocketThruster(name='SSME, RS-25',coreObj=core, injObj=None, pulse_sec=float('inf'), pulse_quality=0.8)
             
R.scale_Rt_to_Thrust( Fvac , Pamb=0.0  , use_scipy=False )

compare_header()
compare('Fvacuum',Fvac, core('FvacTotal'))
compare('Isp Vacuum', Isp, core('IspDel'))

core.reset_attr( 'Pamb', 14.7, re_evaluate=True)
compare('Isp SeaLevel', IspSL, core('IspAmb'))
compare('FseaLevel', FseaLevel, core('Fambient'))
core.reset_attr( 'Pamb', 0, re_evaluate=True)

#compare('Cstar ODE', cstarODE, core('cstarODE'))
#print()
#compare('Fuel Flow Rate', wdotFuel, core('wdotFlCore'))
#compare('Ox Flow Rate', wdotOx, core('wdotOxCore'))

R.summ_print()

