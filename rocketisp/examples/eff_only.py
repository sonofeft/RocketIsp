from rocketisp.efficiencies import Efficiencies

E = Efficiencies( Isp=0.95 )
#E = Efficiencies( ERE=0.98, Noz=0.97 )
E.summ_print()
