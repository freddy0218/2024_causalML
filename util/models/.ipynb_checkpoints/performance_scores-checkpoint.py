from copy import deepcopy
# Imports
import pandas as pd
import numpy as np
import xarray as xr
import numpy as np
import glob,os
from tqdm.auto import tqdm
import math
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error

class scoreboard:
    def __init__(self,model=None):
        self.model = model

    def rSquare(self,measureds,estimations):
        SEE = ((np.array(measureds) - np.array(estimations))**2).sum()
        mMean = (np.array(measureds)).sum() / float(len(measureds))
        dErr = ((mMean - measureds)**2).sum()
        return 1-(SEE/dErr)
        
    def calc_performance(self, X=None, y=None):
        ypred = self.model.predict(X)
        r2 = self.rSquare(y,ypred)
        rmse_wind = np.sqrt(mean_squared_error(y,ypred))
        mae_wind = mean_absolute_error(y,ypred)
        return ypred, r2, rmse_wind, mae_wind

    def store_scores(self, Xdict=None, ydict=None):
        score_dict = {}
        # Training set
        train_pred, train_r2, train_rmse, train_mae = self.calc_performance(Xdict['train'],ydict['train'])
        score_dict['train'] = {
            "pred": train_pred, "r2": train_r2, "RMSE": train_rmse, "MAE": train_mae
        }
        # Validation set
        valid_pred, valid_r2, valid_rmse, valid_mae = self.calc_performance(Xdict['valid'],ydict['valid'])
        score_dict['valid'] = {
            "pred": valid_pred, "r2": valid_r2, "RMSE": valid_rmse, "MAE": valid_mae
        }
        # Test set
        test_pred, test_r2, test_rmse, test_mae = self.calc_performance(Xdict['test'],ydict['test'])
        score_dict['test'] = {
            "pred": test_pred, "r2": test_r2, "RMSE": test_rmse, "MAE": test_mae
        }
        return score_dict
        
class scores_seeds:
    def __init__(self,seed=None,target=None,lag=None):
        self.seed=seed
        self.target=target
        self.lagtime=lag
        
    def score_noFS(self,Xnorml=None,target=None):
        """
        Scoreboard for models without any feature selection
        """
        ytrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[target][self.lagtime:]) for key in Xnorml['train'].keys()],axis=0)
        Xtrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna().drop(columns=[target])[:-self.lagtime]) for key in Xnorml['train'].keys()],axis=0)
        yvalid = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[target][self.lagtime:]) for key in Xnorml['valid'].keys()],axis=0)
        Xvalid = np.concatenate([np.asarray(Xnorml['valid'][key].dropna().drop(columns=[target])[:-self.lagtime]) for key in Xnorml['valid'].keys()],axis=0)
        ytest = np.concatenate([np.asarray(Xnorml['test'][key].dropna()[target][self.lagtime:]) for key in Xnorml['test'].keys()],axis=0)
        Xtest = np.concatenate([np.asarray(Xnorml['test'][key].dropna().drop(columns=[target])[:-self.lagtime]) for key in Xnorml['test'].keys()],axis=0)
        
        Xnorml_nocausal = {'train': Xtrain, 'valid': Xvalid, 'test': Xtest}
        y = {'train': ytrain, 'valid': yvalid, 'test': ytest}
        regr = train_baseline.train_baseline_MLR(Xnorml_nocausal,y)
        
        MLR_scoreboard = performance_scores.scoreboard(regr).store_scores(Xnorml_nocausal,y)
        return {'X':Xnorml_nocausal,'y':y,'regr':regr,'scoreboard':MLR_scoreboard}

    def score_causalFS(self,PC1_results=None,Xnorml=None,target=None,var_names=None):
        """
        Scoreboard for models with causal feature selection
        """
        causal_predictor_list = [var_names[i] for i in [obj[0] for obj in PC1_results[0]]]
        
        while target in causal_predictor_list: 
            causal_predictor_list.remove(target)
            
        Xtrain_causal = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[causal_predictor_list][:-self.lagtime]) for key in Xnorml['train'].keys()],axis=0)
        Xvalid_causal = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[causal_predictor_list][:-self.lagtime]) for key in Xnorml['valid'].keys()],axis=0)
        Xtest_causal = np.concatenate([np.asarray(Xnorml['test'][key].dropna()[causal_predictor_list][:-self.lagtime]) for key in Xnorml['test'].keys()],axis=0)
        ytrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[target][self.lagtime:]) for key in Xnorml['train'].keys()],axis=0)
        yvalid = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[target][self.lagtime:]) for key in Xnorml['valid'].keys()],axis=0)
        ytest = np.concatenate([np.asarray(Xnorml['test'][key].dropna()[target][self.lagtime:]) for key in Xnorml['test'].keys()],axis=0)
        
        Xnorml_causal = {'train': Xtrain_causal, 'valid': Xvalid_causal, 'test': Xtest_causal}
        y = {'train': ytrain, 'valid': yvalid, 'test': ytest}
        regr_causal = train_baseline.train_baseline_MLR(Xnorml_causal,y)
        return {'scoreboard':performance_scores.scoreboard(regr_causal).store_scores(Xnorml_causal,y),
                'X':Xnorml_causal,
                'y':y,
                'regr':regr_causal
               }
        
    def read_stored(self):
        return miss.read_pickle('../2024_causalML_results/results/'+str(self.lagtime)+'_tmin0/'+'SHIPSonly_causal/'+'results_seed'+str(int(self.seed))+'.pkl')
        
    def run_score_noFS(self):
        store = self.read_stored()
        return self.score_noFS(store['dataframes'],self.target)
        
    def run_score_causalFS(self):
        store = self.read_stored()
        results = store['PC1_results']
        storescores = []
        for obj in results:
            storescores.append(self.score_causalFS(obj,store['dataframes'],self.target,store['var_names']))
        return storescores