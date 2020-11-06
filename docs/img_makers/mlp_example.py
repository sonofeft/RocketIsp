import os, sys
import pandas as pd
import numpy as np
from numpy import log10, log
import matplotlib.pyplot as plt
import random
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from joblib import dump, load
from skhelp import pdhelp, plthelp, sklearn_help
from mlp_R2_curve import get_R2_curve

def eles_effbl( Pc=100.0, Fvac=1000.0, eps=20.0):
    """Return effBL from ELES boudary layer correlation."""
    logPF   = log(0.01*Pc*Fvac)
    effBL = 0.997 - (log(eps) * 0.01 * (1-0.065*logPF + 0.001*logPF**2))
    return effBL

def linear_rand( vmin=0, vmax=10 ):
    """Return value from uniform distribution of range_tuple"""
    return vmin + (vmax - vmin) * random.random()

def log_rand( vmin=-2, vmax=2 ):
    """Return log10(value) where value is from uniform distribution of log10(vmin), log10(vmax)"""
    val = linear_rand( log10(vmin), log10(vmax) )
    return val

def create_pandas_monte_carlo( size=10000 ):
    """Create a pandas dataframe of Monte Carlo data"""
    
    rowsL = []
    for i in range( size ):
        log10Pc = log_rand( 100.0, 3000.0 )
        log10Fvac = log_rand( 5.0, 300000.0 )
        log10eps = log_rand( 2.0, 200.0 )
        effBL = eles_effbl( Pc=10.0**log10Pc, Fvac=10.0**log10Fvac, eps=10.0**log10eps)
        tod = linear_rand( 0.0, 24.0 )
        rowsL.append( [effBL, log10Pc, log10Fvac, log10eps, tod] )
        
    df = pd.DataFrame( rowsL, columns=('effBL', 'log10(Pc)', 'log10(Fvac)', 'log10(eps)', 'timeOfDay'))
        
    #pdhelp.show_stats_all_columns(df)
    #pdhelp.show_summary(df)
    return df
    
df = create_pandas_monte_carlo( size=5000 )
scaled = StandardScaler().fit_transform( df )
df_scaled = pd.DataFrame(scaled, columns=df.columns)

pdhelp.show_stats_all_columns(df_scaled)

candidateL = ['log10(Pc)', 'log10(Fvac)', 'log10(eps)', 'timeOfDay']
scoreL, currentL = get_R2_curve( df_scaled, 'effBL', candidateL, hidden_layer_sizes=(10,10) )

print('----------- effBL ------------')
for (score, name) in zip(scoreL, currentL):
    print( '%20s %.6f'%(name, score) )
print( 'scoreL = %s'%repr( scoreL ) )
print( 'nameL  = %s'%repr( currentL ) )

fig = plt.figure( figsize=(5,4) )
ax = plt.gca()

xL = list( range(len(scoreL)) )
yL = scoreL
nameD = {  'log10(Pc)':'Pc',
           'log10(eps)':'AreaRatio',
           'log10(Fvac)':'Thrust',
           'timeOfDay':'timeOfDay' }

labelL = [nameD[name] for name in currentL]

plt.plot(xL, yL, 's-')
# You can specify a rotation for the tick labels in degrees or with keywords.
plt.xticks(xL, labelL, rotation='25')
# Pad margins so that markers don't get clipped by the axes
plt.margins(0.2)
# Tweak spacing to prevent clipping of tick-labels
plt.subplots_adjust(bottom=0.15)
plt.grid( True )
plt.ylabel( 'Correlation Coefficient (R2)' )
plt.title( 'effBL Correlation Coefficient for Monte Carlo Data\n(for Multi-layer Perceptron regressor)' )
fig.tight_layout()
#plt.savefig( 'effBL_mlp_dep_example.png', dpi=300 )

plt.show()


