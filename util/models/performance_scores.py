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