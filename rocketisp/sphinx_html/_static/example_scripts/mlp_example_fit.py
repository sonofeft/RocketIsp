import os, sys
import pandas
from numpy import log10
from sklearn.neural_network import MLPRegressor
from joblib import dump, load

csv_name = 'mlp_example.csv'
df = pandas.read_csv( csv_name )

# scale all parameters to be approximately between 0 and 1
df['Pc'] = (df['log10(Pc)'] - 2.0) / 1.5
df['Fvac'] = (df['log10(Fvac)'] - 0.6) / 5.0
df['eps'] = (df['log10(eps)'] - 0.3) / 2
df['eff'] = (df['effBL'] - 0.95) / 0.05

indepL = ['Pc', 'Fvac', 'eps']
target_var = 'eff'

X = df[ indepL ]
y = df[ target_var ]

print('fitting',target_var, '  with indepL =',indepL)

# verify that scaling looks good by checking min and max values in pandas dataframes
print( X.describe() )
print('-'*44)
print( y.describe() )
print('-'*44)

regr = MLPRegressor(max_iter=50000, hidden_layer_sizes=(100,100), tol=0.000001)

regr.fit(X, y)
score = regr.score(X,y)
print('correlation coefficient:',score )
dump(regr, 'mlp_example.joblib' ) 
