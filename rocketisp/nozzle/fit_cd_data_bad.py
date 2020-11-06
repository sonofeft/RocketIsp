import numpy as np
from sklearn import linear_model


gammaL = [1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4]

cdD = {} # index=RWTU, value=CD
cdD[0.5] = [0.9800142, 0.9809054, 0.981803, 0.9827062, 0.9836141, 0.9845261, 0.9854414]
cdD[0.75] = [0.9857159, 0.9859911, 0.9862749, 0.9865668, 0.9868662, 0.9871727, 0.9874859]
cdD[1] = [0.9897993, 0.989885, 0.989977, 0.9900752, 0.9901793, 0.990289, 0.990404]
cdD[1.5] = [0.9942151, 0.9942037, 0.9941956, 0.9941907, 0.9941889, 0.99419, 0.9941941]
cdD[2] = [0.9963129, 0.9962867, 0.9962624, 0.9962398, 0.996219, 0.9961998, 0.9961823]

RupL = sorted( list( cdD.keys() ) )
xL = []
for i,gam in enumerate(gammaL):
    rowL = []
    for j,r in enumerate( RupL ):
        rowL.append( cdD[r][i] )
    xL.append( rowL )

X = np.array( xL )
#print(X)
y = np.array( gammaL )

regr = linear_model.LinearRegression()
regr.fit(X, y)
print('linear score:', regr.score(X,y) )

print( 'coef_ =', regr.coef_ )
print( 'intercept_ =', regr.intercept_ )

print( np.dot( X, regr.coef_ ) + regr.intercept_  )

print()
print( "regr.predict =",regr.predict( np.array([[1.2], [1.0]]) ) )

