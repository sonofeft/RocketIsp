import os, sys
import numpy as np
from numpy import log10
from sklearn.neural_network import MLPRegressor
from joblib import dump, load

regr = load( 'mlp_example.joblib' ) 

def calc_black_box( Pc=100.0, Fvac=1000.0, eps=20.0):
    """
    Return Black Box value
    where: Pc=psia, Fvac=lbf, eps=dimensionless
    """
    # scale the inputs
    inpPc = (log10(Pc) - 2.0) / 1.5
    inpFvac = (log10(Fvac) - 0.6) / 5.0
    inpEps = (log10(eps) - 0.3) / 2
    
    # note that a list is returned... select zeroth value.
    outEffBL = regr.predict(  [[inpPc, inpFvac, inpEps]]  )[0]
    
    # unscale the result
    effBL = outEffBL*0.05 + 0.95
    
    return effBL
    
if __name__ == "__main__":
    
    print( 'calc_black_box(Pc=100.0, Fvac=1000.0, eps=20.0) =',
            calc_black_box(Pc=100.0, Fvac=1000.0, eps=20.0) )