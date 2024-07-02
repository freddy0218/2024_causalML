from copy import deepcopy
# Imports
import pandas as pd
import numpy as np
import xarray as xr
import numpy as np
import matplotlib   
import glob,os
from tqdm.auto import tqdm
import math

class proc_data:
    def __init__(self,df=None,seed=42):
        self.df = df
        self.seed = seed

    def random_testindex(self,totalexp=None,testexp=None):
        from numpy.random import default_rng
        rng = default_rng(self.seed)
        np.random.seed(self.seed)
        seed = rng.choice(totalexp, testexp, replace=False)
        return seed

    def random_validindex(self,totalexp=None,testindex=None,validexp=None):
        from numpy.random import default_rng
        rng = default_rng(self.seed)
        np.random.seed(self.seed)
        listt = [int(obj) for obj in np.linspace(0,totalexp-1,totalexp)]
        seed = np.random.choice([obj for obj in listt if obj not in testindex],validexp,replace=False)
        return seed

    def random_splitdata(self,validindex=None,newtestindex=None):
        datae = self.df.copy()
        traindata = {}
        testdata = {}
        validdata = {}
        stormnames_fulllist = list(datae.keys())
        
        for ind,obj in enumerate(datae.keys()):
            if ind in list(newtestindex):
                testdata[stormnames_fulllist[ind]] = datae[stormnames_fulllist[ind]]
            elif ind in list(validindex):
                validdata[stormnames_fulllist[ind]] = datae[stormnames_fulllist[ind]]
            else:
                traindata[stormnames_fulllist[ind]] = datae[stormnames_fulllist[ind]]
        return traindata,validdata,testdata

    def year_splitdata(self,testyears=None,config=None):
        datae = self.df.copy()
        traindata = {}
        validdata = {}

        # Separate test data
        testdata = {}
        trainvaliddata = {}
        for i in testyears:
            TC_keys = list(datae.keys())
            for obj in TC_keys:
                if obj[:4]==str(i):
                    testdata[obj] = datae[obj]
                else:
                    trainvaliddata[obj] = datae[obj]
                    
        # indices for valid dataset
        validindex = self.random_testindex(totalexp=len(trainvaliddata.keys()),testexp=int(len(trainvaliddata.keys())*float(config['splitratio'])))
        stormnames_fulllist = list(trainvaliddata.keys())
        
        for ind,obj in enumerate(trainvaliddata.keys()):
            if ind in list(validindex):
                validdata[stormnames_fulllist[ind]] = trainvaliddata[stormnames_fulllist[ind]]
            else:
                traindata[stormnames_fulllist[ind]] = trainvaliddata[stormnames_fulllist[ind]]
        return traindata,validdata,testdata,validindex
        
# Split data into three subsets
def splitdata_handler(df=None,method='random',seed=None,config=None,testyears=[2020,2021]):
    if method=='random':
        testindex = proc_data(df=df,seed=42).random_testindex(totalexp=len(df.keys()),\
                                                                            testexp=int(len(df.keys())*float(config['splitratio'])))
        validindex = proc_data(df=df,seed=seed).random_validindex(totalexp=len(df.keys()),
                                                                              testindex=testindex,
                                                                              validexp=int(len(df.keys())*float(config['splitratio'])))
        traindata,validdata,testdata = proc_data(df=df,seed=seed).random_splitdata(validindex=validindex,newtestindex=testindex)
        return {'train':traindata,'valid':validdata,'test':testdata,'validindex':validindex,'testindex':testindex}
    elif method=='year':
        traindata,validdata,testdata,validindex = proc_data(df=df,seed=seed).year_splitdata(testyears=testyears,config=config)
        return {'train':traindata,'valid':validdata,'test':testdata,'validindex':validindex}

def combine_df_storms(datastore=None,targetname=None):
    storepred,storetarget,outsize = [],[],[]
    for stormname in datastore.keys():
        storetarget.append(datastore[stormname][targetname])
        storepred.append(datastore[stormname].drop(columns=[targetname]))
        outsize.append(np.asarray(datastore[stormname][targetname].shape[0]))
    predictors = pd.concat(storepred).reset_index(drop=True)
    targets = pd.concat(storetarget).reset_index(drop=True)
    return targets,predictors,outsize
        
def df_proc_separate(trainstore=None,validstore=None,teststore=None,target='DELV24'):
    ytrain,Xtrain,trainsize = combine_df_storms(datastore=trainstore,targetname=target)
    yvalid,Xvalid,validsize = combine_df_storms(datastore=validstore,targetname=target)
    ytest,Xtest,testsize = combine_df_storms(datastore=teststore,targetname=target)
    return {'train':Xtrain,'valid':Xvalid,'test':Xtest},{'train':ytrain,'valid':yvalid,'test':ytest},{'train':trainsize,'valid':validsize,'test':testsize}



