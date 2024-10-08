# Imports
import pandas as pd
import numpy as np
import xarray as xr
import numpy as np
import glob,os
from tqdm.auto import tqdm
import math
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
import itertools
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from util.data_process import read_vars, proc_dataset, miss
from util.models import performance_scores,train_baseline,causal_settings,train_PC1

def train_rf(n_estimators=None,max_features=None,max_depth=None,min_samples_split=None,
             min_samples_leaf=None,bootstrap=None,X=None,y=None):
    rf =  RandomForestRegressor(n_estimators=n_estimators,max_features=max_features,max_depth=max_depth,
                                 min_samples_split=min_samples_split,min_samples_leaf=min_samples_leaf,bootstrap=bootstrap)
    return rf.fit(X,y)
    
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
    def __init__(self,seed=None,target=None,lag=None,exp=None,alt_exp=None,alt_target=None,prefix=None,suffix=None):
        self.seed=seed
        self.target=target
        self.lagtime=lag
        self.exp=exp
        self.alt_exp=alt_exp # Patch for experiment trained with VMAX
        self.alt_target=alt_target # Yes or No with routines with VMAX experiments
        self.suffix=suffix
        self.prefix=prefix

    def get_best_rf_vars(self,Xnorml=None,target=None,var_names=None):
        ytrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[target][self.lagtime:]) for key in Xnorml['train'].keys()],axis=0)
        Xtrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna().drop(columns=[target])[:-self.lagtime]) for key in Xnorml['train'].keys()],axis=0)
        yvalid = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[target][self.lagtime:]) for key in Xnorml['valid'].keys()],axis=0)
        Xvalid = np.concatenate([np.asarray(Xnorml['valid'][key].dropna().drop(columns=[target])[:-self.lagtime]) for key in Xnorml['valid'].keys()],axis=0)
        
        random_grid = {'n_estimators':[20,30,40],'max_features':[None],
                       'max_depth':[20,30,40],'min_samples_split':[40,80],
                       'min_samples_leaf':[40,80],'bootstrap':[True]
                      }
        
        options = list(itertools.product(random_grid['n_estimators'],random_grid['max_features'],random_grid['max_depth'],\
                                         random_grid['min_samples_split'],random_grid['min_samples_leaf'],random_grid['bootstrap']))
        
        models = []
        for obj in options:
            model = train_rf(obj[0],obj[1],obj[2],obj[3],obj[4],obj[5],Xtrain,ytrain)
            models.append(model)
        
        bestindex = np.asarray([r2_score(yvalid,models[i].predict(Xvalid)) for i in range(len(models))]).argmax()
        forest_importances_gini = pd.Series(models[bestindex].feature_importances_,index=var_names[1:])
        return forest_importances_gini#.sort_values(ascending=False).index
        
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
        try:
            causal_predictor_list = [var_names[i] for i in [obj[0] for obj in PC1_results[0][0]]]
        except:
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
                'regr':regr_causal,
                'corrrank':causal_predictor_list
               }
        
    def score_corrFS(self,Xnorml=None,target=None,targetcausal='VMAX',var_names=None,shapez=None):
        if self.alt_target=='Yes':
            # Create Dataset
            ytrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[targetcausal][self.lagtime:]) for key in Xnorml['train'].keys()],axis=0)
            Xtrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna().drop(columns=[target,targetcausal])[:-self.lagtime]) for key in Xnorml['train'].keys()],axis=0)
            # put into a dataframe
            Xnorml_df_train = pd.DataFrame(Xtrain,columns=[var_names[1:]])
            Xnorml_df_train[target] = ytrain
            # Rank the correlation between different features and the target
            corrrank = pd.Series({name: np.abs(Xnorml_df_train[name].iloc[:,0].corr(Xnorml_df_train[target].iloc[:,0])) for name in var_names[1:]})            
        else:
            # Create Dataset
            ytrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[target][self.lagtime:]) for key in Xnorml['train'].keys()],axis=0)
            Xtrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna().drop(columns=[target])[:-self.lagtime]) for key in Xnorml['train'].keys()],axis=0)
            # put into a dataframe
            Xnorml_df_train = pd.DataFrame(Xtrain,columns=[var_names[1:]])
            Xnorml_df_train[target] = ytrain
            # Rank the correlation between different features and the target
            corrrank = pd.Series({name: np.abs(Xnorml_df_train[name].iloc[:,0].corr(Xnorml_df_train[target].iloc[:,0])) for name in var_names[1:]})
        
        # Score Correlation
        scores_s = []
        corr_list = corrrank.sort_values(ascending=False).index
        Xs,ys,regr_corrs = [],[],[]
        for i in range(1,shapez-1):#len(corr_list)-1):
            Xtrain_corr = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[corr_list[:i]][:-self.lagtime]) for key in Xnorml['train'].keys()],axis=0)
            Xvalid_corr = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[corr_list[:i]][:-self.lagtime]) for key in Xnorml['valid'].keys()],axis=0)
            Xtest_corr = np.concatenate([np.asarray(Xnorml['test'][key].dropna()[corr_list[:i]][:-self.lagtime]) for key in Xnorml['test'].keys()],axis=0)
            ytrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[target][self.lagtime:]) for key in Xnorml['train'].keys()],axis=0)
            yvalid = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[target][self.lagtime:]) for key in Xnorml['valid'].keys()],axis=0)
            ytest = np.concatenate([np.asarray(Xnorml['test'][key].dropna()[target][self.lagtime:]) for key in Xnorml['test'].keys()],axis=0)
            
            Xnorml_corr = {'train': Xtrain_corr, 'valid': Xvalid_corr, 'test': Xtest_corr}
            Xs.append(Xnorml_corr)
            y = {'train': ytrain, 'valid': yvalid, 'test': ytest}
            ys.append(y)
            regr_corr = train_baseline.train_baseline_MLR(Xnorml_corr,y)
            regr_corrs.append(regr_corr)
            corrmlr_score = performance_scores.scoreboard(regr_corr).store_scores(Xnorml_corr,y)
            scores_s.append(corrmlr_score)
            
        return {'scoreboard':scores_s,'X':Xs,'y':ys,'regr':regr_corrs,'corrrank':corrrank}

    def score_XAIFS(self,Xnorml=None,target=None,var_names=None):
        XAIgini = self.get_best_rf_vars(Xnorml=Xnorml,target=target,var_names=var_names)
        scores_s = []
        XAI_list = XAIgini.sort_values(ascending=False).index
        Xs,ys,regr_corrs = [],[],[]
        for i in range(1,len(XAI_list)-1):
            Xtrain_corr = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[XAI_list[:i]][:-self.lagtime]) for key in Xnorml['train'].keys()],axis=0)
            Xvalid_corr = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[XAI_list[:i]][:-self.lagtime]) for key in Xnorml['valid'].keys()],axis=0)
            Xtest_corr = np.concatenate([np.asarray(Xnorml['test'][key].dropna()[XAI_list[:i]][:-self.lagtime]) for key in Xnorml['test'].keys()],axis=0)
            ytrain = np.concatenate([np.asarray(Xnorml['train'][key].dropna()[target][self.lagtime:]) for key in Xnorml['train'].keys()],axis=0)
            yvalid = np.concatenate([np.asarray(Xnorml['valid'][key].dropna()[target][self.lagtime:]) for key in Xnorml['valid'].keys()],axis=0)
            ytest = np.concatenate([np.asarray(Xnorml['test'][key].dropna()[target][self.lagtime:]) for key in Xnorml['test'].keys()],axis=0)
            
            Xnorml_corr = {'train': Xtrain_corr, 'valid': Xvalid_corr, 'test': Xtest_corr}
            Xs.append(Xnorml_corr)
            y = {'train': ytrain, 'valid': yvalid, 'test': ytest}
            ys.append(y)
            regr_corr = train_baseline.train_baseline_MLR(Xnorml_corr,y)
            regr_corrs.append(regr_corr)
            corrmlr_score = performance_scores.scoreboard(regr_corr).store_scores(Xnorml_corr,y)
            scores_s.append(corrmlr_score)
            
        return {'scoreboard':scores_s,'X':Xs,'y':ys,'regr':regr_corrs,'XAIrank':XAIgini}
        
    def read_stored(self,exp=None):
        #miss.read_pickle('../2024_causalML_results/results/'+str(self.lagtime)+'_tmin0/'+'SHIPSonly_causal/'+'results_seed'+str(int(self.seed))+'.pkl')
        if self.suffix:
            return miss.read_pickle(str(self.prefix)+str(self.lagtime)+'_tmin0/'+str(exp)+'/'+'results_seed'+str(int(self.seed))+str(self.suffix)+'.pkl')
        else:
            return miss.read_pickle(str(self.prefix)+str(self.lagtime)+'_tmin0/'+str(exp)+'/'+'results_seed'+str(int(self.seed))+'.pkl')

    def run_score_noFS(self):
        store = self.read_stored(exp=self.exp)
        return self.score_noFS(store['dataframes'],self.target)
        
    def run_score_causalFS(self):
        if self.alt_target=='Yes':
            store = self.read_stored(exp=self.exp) #Exp trained on DELV
            alt_store = self.read_stored(exp=self.alt_exp) #Exp trained on VMAX
            results = store['PC1_results']
            storescores = []
            for obj in results:
                storescores.append(self.score_causalFS(obj,alt_store['dataframes'],self.target,store['var_names']))
        else: 
            store = self.read_stored(exp=self.exp)
            results = store['PC1_results']
            storescores = []
            for obj in results:
                storescores.append(self.score_causalFS(obj,store['dataframes'],self.target,store['var_names']))
        return storescores

    def run_score_corrFS(self,shapez=None,targetcausal=None):
        if self.alt_target=='Yes':
            store = self.read_stored(exp=self.exp)
            alt_store = self.read_stored(exp=self.alt_exp)
            return self.score_corrFS(alt_store['dataframes'],self.target,targetcausal,store['var_names'],shapez=shapez)
        else:
            store = self.read_stored(exp=self.exp)
            return self.score_corrFS(store['dataframes'],self.target,targetcausal,store['var_names'],shapez=shapez)

    def run_score_XAIFS(self):
        if self.alt_target=='Yes':
            store = self.read_stored(exp=self.exp)
            alt_store = self.read_stored(exp=self.alt_exp)
            return self.score_XAIFS(alt_store['dataframes'],self.target,store['var_names'])
        else:
            store = self.read_stored()
            return self.score_XAIFS(store['dataframes'],self.target,store['var_names'])