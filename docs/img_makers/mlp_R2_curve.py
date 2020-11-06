import sys, os
from sklearn.neural_network import MLPRegressor

def get_best_added_indep_var( df_scaled, target_var, currentL, candidateL, hidden_layer_sizes=(10,10) ):
    
    scoreL = [] # list of (score, candidate)
    
    for candidate in candidateL:
        if candidate in currentL:
            continue # skip any duplicates
        
        
        X = df_scaled[ currentL + [candidate] ]
        y = df_scaled[target_var]
                                   
        regr = MLPRegressor( hidden_layer_sizes=hidden_layer_sizes, validation_fraction=0.2, 
               random_state=7, early_stopping=False)

        regr.fit(X, y)
        score = regr.score(X,y)
        scoreL.append( (score, candidate) )
        
        print( '%20s'%candidate, score, currentL )
    
    if scoreL:
        scoreL.sort()
        return scoreL[-1] # return highest score and name of best candidate
    else:
        return (None, None)

def get_R2_curve( df_scaled, target_var, candidateL, hidden_layer_sizes=(10,10) ):
    
    currentL = []
    scoreL = []
    while True:
        (score, best_var) = get_best_added_indep_var( df_scaled, target_var, currentL, candidateL, 
                                                      hidden_layer_sizes=hidden_layer_sizes )
        if score is None:
            break
            
        scoreL.append( score )
        currentL.append( best_var )
    print('------------------------------------------------')
    return scoreL, currentL

