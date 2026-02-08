import os, sys
import pandas as pd
from numpy import log10, log
import random
random.seed(7) # for this example make reproducible results

def eles_effbl( Pc=100.0, Fvac=1000.0, eps=20.0):
    """
    Return effBL from ELES boundary layer correlation.
    where: Pc=psia, Fvac=lbf, eps=dimensionless
    """
    logPF   = log(0.01*Pc*Fvac)
    effBL = 0.997 - (log(eps) * 0.01 * (1-0.065*logPF + 0.001*logPF**2))
    return effBL

def linear_rand( vmin=0, vmax=10 ):
    """Return value from uniform distribution within vmin to vmax"""
    return vmin + (vmax - vmin) * random.random()

def log_rand( vmin=-2, vmax=2 ):
    """Return log10(value) where value is from uniform distribution within log10(vmin) to log10(vmax)"""
    val = linear_rand( log10(vmin), log10(vmax) )
    return val

def create_pandas_monte_carlo( size=10000 ):
    """Create a pandas dataframe of Monte Carlo data"""
    
    rowsL = []
    for i in range( size ):
        # create random input values (Pc, Fvac and eps use log values)
        log10Pc   = log_rand( 100.0, 3000.0 )
        log10Fvac = log_rand( 5.0, 300000.0 )
        log10eps  = log_rand( 2.0, 200.0 )
        # timeOfDay is included as an uncorrelated input.
        tod       = linear_rand( 0.0, 24.0 )
        
        # calculate model results and add data row to pandas dataframe
        effBL     = eles_effbl( Pc=10.0**log10Pc, Fvac=10.0**log10Fvac, eps=10.0**log10eps)
        rowsL.append( [effBL, log10Pc, log10Fvac, log10eps, tod] )
        
    df = pd.DataFrame( rowsL, columns=('effBL', 'log10(Pc)', 'log10(Fvac)', 'log10(eps)', 'timeOfDay'))
        
    return df
    
df = create_pandas_monte_carlo()

print( df.describe() )

df.to_csv( 'mlp_example.csv', index=False )
