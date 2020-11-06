
import os, sys
import importlib
from rocketisp.efficiency.get_elements import get_ox_fuel_groupname

"""
Import the appropriate fracKin file from the subdirectory fracKinODK and call it.
First look for group (e.g. CHO or CHNO) if not found use calc_All_fracKin.
"""

here = os.path.abspath(os.path.dirname(__file__))

kin_dir = os.path.join( here, 'fracKinODK' )
if kin_dir not in sys.path[:2]:
    sys.path.insert(0, kin_dir)

module_by_idD = {} # index = id(ceaObj), value=kin_module

def get_kin_module( ceaObj ):

    groupName = get_ox_fuel_groupname( ceaObj.oxName, ceaObj.fuelName )
    
    try:
        kin_module_name = 'calc_%s_fracKin'%groupName
        #print('group Name: "%s"'%groupName, '    kin_module_name=',kin_module_name)
        kin_module = importlib.import_module(kin_module_name)
    except:
        print('WARNING... Import of group "%s" failed... using group "All"'%groupName)
        kin_module_name = 'calc_All_fracKin'
        print('group Name: "All"', '    kin_module_name=',kin_module_name)
        kin_module = importlib.import_module(kin_module_name)
    
    # add kin_module to module_by_idD
    module_by_idD[ id(ceaObj) ] = kin_module
    
    return kin_module


def calc_IspODK(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5):
    
    # if already have kin_module imported, use it... otherwise import it now
    try:
        kin_module = module_by_idD[ id(ceaObj) ]
    except:
        kin_module = get_kin_module( ceaObj )
    
    return kin_module.calc_IspODK(ceaObj, Pc=Pc, eps=eps, Rthrt=Rthrt, pcentBell=pcentBell, MR=MR)


def calc_fracKin(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5):
    
    # if already have kin_module imported, use it... otherwise import it now
    try:
        kin_module = module_by_idD[ id(ceaObj) ]
    except:
        kin_module = get_kin_module( ceaObj )

    return kin_module.calc_fracKin(ceaObj, Pc=Pc, eps=eps, Rthrt=Rthrt, pcentBell=pcentBell, MR=MR)


if __name__ == "__main__":
    from rocketcea.cea_obj import CEA_Obj
    
    ceaObj = CEA_Obj(oxName='N2O4', fuelName='MMH')
    
    print('module_by_idD =',module_by_idD)
    print()
    
    IspODK = calc_IspODK(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5)
    print('IspODK = ', IspODK)
    print()
    
    IspODK = calc_IspODK(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5)
    fracKin = calc_fracKin(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5)
    print('IspODK = ', IspODK, '   fracKin=',fracKin)
    print()
    
    print('module_by_idD =',module_by_idD)
    

    

