import os, sys
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

import pandas as pd
import numpy as np
from numpy import log10, log
import matplotlib.pyplot as plt
import random
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from joblib import dump, load
from mlp_R2_curve import get_R2_curve

    
df = pd.read_csv('mlp_example.csv', sep=None, engine='python', index_col=None)
scaled = StandardScaler().fit_transform( df )
df_scaled = pd.DataFrame(scaled, columns=df.columns)

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

png_name = os.path.join(up_one, '_static', 'mlp_example_plot_dep.png')
plt.savefig( png_name, dpi=300 )

plt.show()


