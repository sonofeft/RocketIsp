import copy
from scipy.optimize import brentq

import warnings
# Filter by the start of the message string instead of the category class
# In NumPy 2.4, they tightened the rules: align must be a boolean. 
# Passing an integer is now deprecated and will eventually cause a hard crash.
warnings.filterwarnings("ignore", message=".*align should be passed as Python or NumPy boolean.*")


def solve_FFC_for_TgasWall( coreObj, TwallGasReqmt=2800.0, do_print=False ):
    """
        Args:
        coreObj (CoreStream): starting CoreStream object
        TwallGasReqmt (float, optional): Required gas wall temperature (degR). Defaults to 3000.0 R
        Returns:
        core_out: CoreStream object with Twallgas == TwallGasReqmt

        If calculation fails, return the input coreObj and print WARNING.
    """

    core_out = copy.deepcopy(  coreObj )

    def objective( new_ffc ):

        core_out.set_new_pcentFFC( new_ffc )

        if do_print:
            print( "new_ffc=%g"%new_ffc, '  Twallgas=%g'%core_out.barrierObj.Twallgas )

        return TwallGasReqmt - core_out.barrierObj.Twallgas
    
    # Solve FFC to give TwallGasReqmt
    try:
        ffc, info = brentq(objective, 0.01, 70, xtol=0.0001, full_output=True) # xtol on pcentFFC
    except:
        print("WARNING: Failed to converge on FFC for TwallGasReqmt=%g."%TwallGasReqmt)
        print( '    Assuming: FFC=%g with TwallGasReqmt=%g'%( coreObj.barrierObj.pcentFFC ,coreObj.barrierObj.Twallgas ) )
        return coreObj

    # Check the success flag
    if info.converged:
        if do_print:
            print( "Success: ffc=%g"%ffc, '  Twallgas=%g'%core_out.barrierObj.Twallgas )
        return core_out
    else:
        print("WARNING: Failed to converge on FFC for TwallGasReqmt=%g."%TwallGasReqmt)
        print( '    Assuming: FFC=%g with TwallGasReqmt=%g'%( coreObj.barrierObj.pcentFFC ,coreObj.barrierObj.Twallgas ) )
        return coreObj




def dev_tests():
    
    from rocketisp.geometry import Geometry
    from rocketisp.efficiencies import Efficiencies
    from rocketisp.stream_tubes import CoreStream

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
    
    core_2 = solve_FFC_for_TgasWall( core, TwallGasReqmt=2800.0, do_print=True )

    # core_2.summ_print()


if __name__ == "__main__":
    dev_tests()
