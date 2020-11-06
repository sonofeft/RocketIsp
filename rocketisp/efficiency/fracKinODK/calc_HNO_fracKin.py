
import os
from math import log10, sqrt, tan, radians
import numpy as np
from scipy import sparse

# NOTE: requires numpy npz file: calc_HNO_fracKin.npz in local folder (i.e. here)
here = os.path.abspath(os.path.dirname(__file__))

speciesL = ['*H', '*H2', '*N', '*N2', '*NH', '*NO', '*O', '*O2', '*OH', 'H2O', 'H2O(L)', 'H2O(cr)', 'H2O2', 'HNO', 'HNO2', 'HO2', 'N2O', 'NH2', 'NH3', 'NO2']

def calc_IspODK(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5):
    
        fracKin = calc_fracKin(ceaObj, Pc=Pc, eps=eps, 
                                    Rthrt=Rthrt, pcentBell=pcentBell, 
                                    MR=MR)
                                    
        IspODE,cstarODE,TcODE = ceaObj.get_IvacCstrTc( Pc=Pc, MR=MR, eps=eps)
        IspODF,_,_ = ceaObj.getFrozen_IvacCstrTc( Pc=Pc, MR=MR, eps=eps, frozenAtThroat=0)
        IspODK = IspODF + fracKin*(IspODE-IspODF)
        
        eff_kin = IspODK / IspODE
        return IspODK


def calc_fracKin(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5):
    
    
    massWtD, masseFracD = ceaObj.get_SpeciesMassFractions( Pc=Pc, MR=MR, eps=eps, 
                            frozen=0, frozenAtThroat=0, min_fraction=0.000005)
    
    _, _, TcCham, MolWt, gammaInit = ceaObj.get_IvacCstrTc_ChmMwGam( Pc=Pc, MR=MR, eps=eps)

    #asonic = ceaObj.get_Chamber_SonicVel( Pc=Pc, MR=MR, eps=eps)
    #tauRt = Rthrt / asonic
    
    #z100 = Rthrt * ( sqrt(eps) - 1.0 ) / tan( radians(15.) )
    #Lnoz = z100 * pcentBell / 100.0
    #tauLnoz = Lnoz / asonic
    
    # condition Pc, eps, Rthrt, pcentBell, gammaInit, TcCham
    inpL = [log10(Pc)/4.0, log10(eps)/3.0, (2.0+log10(Rthrt))/4.0, 
            (pcentBell-60)/60.0, (gammaInit-1.1)/0.57, TcCham/7000.0, MolWt/30.0]
            
    #log10(tauRt)/6.0, log10(tauLnoz)/5.0]
    
    for sp in speciesL:
        vL = masseFracD.get( sp, [0.,0.] )
        inpL.append( vL[1] ) # chamber mass frac for species
    
    ypred = predict( np.array(inpL).reshape(1, -1) )
    return ypred


def predict( X ):
    activations = [X]
    layer_units = [X.shape[1]] + hidden_layer_sizes + [n_outputs_]
                
    for i in range(n_layers_ - 1):
        activations.append(np.empty((X.shape[0], layer_units[i + 1])))

    # ----------- start forward pass ------------
    hidden_activation = relu
    for i in range(n_layers_ - 1):
        activations[i + 1] = safe_sparse_dot(activations[i],
                                             coefs_[i])
        activations[i + 1] += intercepts_[i]
        # For the hidden layers
        if (i + 1) != (n_layers_ - 1):
            activations[i + 1] = hidden_activation(activations[i + 1])
    # For the last layer
    output_activation = identity
    activations[i + 1] = output_activation(activations[i + 1])

    y_pred = activations[-1][-1][-1]
    ypred = max(0., min(1.0, y_pred ))
    
    return ypred


def relu(X):
    """Compute the rectified linear unit function inplace.
    Parameters
    ----------
    X : array-like, sparse matrix, shape (n_samples, n_features)
        The input data.
    Returns
    -------
    X_new : array-like, sparse matrix, shape (n_samples, n_features)
        The transformed data.
    """

    np.clip(X, 0, np.finfo(X.dtype).max, out=X)
    return X

def identity(X):
    """Simply return the input array.
    Parameters
    ----------
    X : array-like, sparse matrix, shape (n_samples, n_features)
        Data, where n_samples is the number of samples
        and n_features is the number of features.
    Returns
    -------
    X : array-like, sparse matrix, shape (n_samples, n_features)
        Same as the input data.
    """
    return X

def safe_sparse_dot(a, b, *, dense_output=False):
    """Dot product that handle the sparse matrix case correctly
    Parameters
    ----------
    a : array or sparse matrix
    b : array or sparse matrix
    dense_output : boolean, (default=False)
        When False, ``a`` and ``b`` both being sparse will yield sparse output.
        When True, output will always be a dense array.
    Returns
    -------
    dot_product : array or sparse matrix
        sparse if ``a`` and ``b`` are sparse and ``dense_output=False``.
    """
    if a.ndim > 2 or b.ndim > 2:
        if sparse.issparse(a):
            # sparse is always 2D. Implies b is 3D+
            # [i, j] @ [k, ..., l, m, n] -> [i, k, ..., l, n]
            b_ = np.rollaxis(b, -2)
            b_2d = b_.reshape((b.shape[-2], -1))
            ret = a @ b_2d
            ret = ret.reshape(a.shape[0], *b_.shape[1:])
        elif sparse.issparse(b):
            # sparse is always 2D. Implies a is 3D+
            # [k, ..., l, m] @ [i, j] -> [k, ..., l, j]
            a_2d = a.reshape(-1, a.shape[-1])
            ret = a_2d @ b
            ret = ret.reshape(*a.shape[:-1], b.shape[1])
        else:
            ret = np.dot(a, b)
    else:
        ret = a @ b
    if (sparse.issparse(a) and sparse.issparse(b)
            and dense_output and hasattr(ret, "toarray")):
        return ret.toarray()
    return ret

n_layers_ = 5
n_outputs_ = 1

hidden_layer_sizes = (36, 36, 36)
hidden_layer_sizes = hidden_layer_sizes
if not hasattr(hidden_layer_sizes, "__iter__"):
    hidden_layer_sizes = [hidden_layer_sizes]
hidden_layer_sizes = list(hidden_layer_sizes)


activation = 'relu'
if activation != 'relu':
    raise Exception('Need to add activation other than relu')
    
out_activation_ = 'identity'
if out_activation_ != 'identity':
    raise Exception('Need to add out_activation_ other than identity')

npz_filename =  os.path.join( here, 'calc_HNO_fracKin.npz')
with np.load(npz_filename, allow_pickle=True) as data:
    coefs_ = data['c']
    intercepts_ = data['i']
    
if __name__ == "__main__":
    
    from rocketcea.cea_obj import CEA_Obj
    
    ceaObj = CEA_Obj(oxName='N2O4', fuelName='N2H4', useFastLookup=0)
    
    ypred = calc_fracKin(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=2)
    print( 'ypred fracKin =', ypred )
    
    IspODK = calc_IspODK(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=2)
    print('IspODK =', IspODK)
