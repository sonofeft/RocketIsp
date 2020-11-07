from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.rocket_isp import RocketThruster
from rocketisp.goldSearch import search_max

class PerfInjThruster:
    
    
    def __init__(self, name='PI Thruster', geomObj=Geometry(), ERE=0.98,
                 oxName='N2O4', fuelName='MMH', MRcore=1.9, Pc=500,
                 isRegenCham=0, noz_regen_eps=1.0, calc_CdThroat=True): 
    
        # create a perfect injector CoreStream
        coreObj = CoreStream( geomObj=geomObj, 
                              effObj=Efficiencies(ERE=ERE), 
                              oxName=oxName, fuelName=fuelName, 
                              MRcore=MRcore, Pc=Pc)
        
        self.R = RocketThruster( name=name,
                 coreObj=coreObj, injObj=None, 
                 isRegenCham=isRegenCham, noz_regen_eps=noz_regen_eps, 
                 calc_CdThroat=calc_CdThroat)
        
    def summ_print(self):
        self.R.summ_print()
    def scale_Rt_to_Thrust(self, ThrustLbf=500.0, Pamb=0.0, use_scipy=False):
        """
        Adjust throat size in order to get total thrust at specified ambient pressure exactly

        :param ThrustLbf: lbf, desired thrust at specified ambient pressure (Pamb)
        :param Pamb: psia, ambient pressure
        :param use_scipy: flag to indicate the need for more sophisticated root finder
        :type ThrustLbf: float
        :type Pamb: float
        :type use_scipy: bool
        :return: None
        :rtype: None        """

        self.R.scale_Rt_to_Thrust( ThrustLbf=ThrustLbf, Pamb=Pamb, use_scipy=use_scipy )
        
    def set_to_optimum_MR(self):
        """Starting with MR for ER=1 find max Isp MR"""
        C = self.R.coreObj # core object
        
        # get MR for equivalence ratio = 1
        MRstart = C.ceaObj.getMRforER( ERr=1.0 )
        
        MRlo = MRstart / 3.0
        MRhi = MRstart * 3.0
        
        def get_ispdel( MR ):
            C.reset_attr('MRcore', MR, re_evaluate=True)
            self.R.calc_all_eff()
            return C.IspDel
            
        MRopt, IspMax  = search_max(get_ispdel, MRlo, MRhi, tol=0.01)
        print('MRopt=%g, IspMax=%g sec'%(MRopt, IspMax) )
        # use MRopt to reset everything
        get_ispdel( MRopt )
        
        return MRopt
        
        

if __name__ == '__main__':
    
    # Apollo SPS geometry
    geomObj = Geometry(Rthrt=6,
              CR=2.5, eps=62.5,  pcentBell=72.3,
              RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
              LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)

    PI = PerfInjThruster(geomObj=geomObj, oxName='N2O4', fuelName='A50',  
                         MRcore=1.6, Pc=100)
    
    PI.set_to_optimum_MR()
    PI.summ_print()
    
