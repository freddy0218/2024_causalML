import pandas as pd
from tqdm.auto import tqdm
import numpy as np
import glob
import ast
import pickle

def remove_storms(trackpath=None,basinID='NA',yearmin=None,yearmax=None,remove_set=None):
    """
    Hard-code storm removal.
    """
    filt_stormnames = []
    for year in tqdm([int(obj) for obj in np.linspace(yearmin,yearmax,yearmax-yearmin+1)]):
        # Read processed track files
        track = sorted(glob.glob(trackpath+basinID+'_'+str(year)+'.csv'))
        tracksDF = pd.read_csv(track[0])
        # Find unique TCs in the track file
        tracksDF['name'].unique()
        stormnames = list(tracksDF['name'].unique())

        # Use the dictionary "remove_set" to filter TCs
        for obj in remove_set:
            yearFILT,stormFILT=obj[0],obj[1]
            if year==yearFILT:
                stormnames.remove(stormFILT)
        filt_stormnames.append(stormnames)
    return filt_stormnames

        
def read_processed_vars_ships(loc=None,foldernames=['newships_dev_POT'],year=None,stormname=None):
    store = []
    for foldername in foldernames:
        tmp = pd.read_csv(glob.glob(loc+str(foldername)+'/'+\
                                 str(year)+'/'+str(year)+'*shipsdev*'+str(stormname)+'.csv')[0],delimiter=r",").fillna(0)
        store.append(tmp.iloc[:,:])
    return store

################################################################################################################################################################
# SHIPS routine
################################################################################################################################################################
def read_SHIPS_csv(startyear=None,endyear=None,vars_path=None,filted_TCnames=None,suffixlist=None):
    storeyear = []
    for ind,year in tqdm(enumerate([int(obj) for obj in np.linspace(startyear,endyear,int(endyear)-int(startyear)+1)])):
        filt_TCyear = filted_TCnames[ind]
        storestorms = {}
        for i in range(len(filt_TCyear)):
            storestorms[filt_TCyear[i]] = read_processed_vars_ships(vars_path,suffixlist,year,filt_TCyear[i])
        storeyear.append(storestorms)
    return storeyear

def create_SHIPS_df(startyear=None,endyear=None,SHIPSdict=None,wantvarnames=None,targetname=None,filted_TCnames=None,lagnum=None):
    store_dfstorms = {}
    for inddd,year in tqdm(enumerate([int(obj) for obj in np.linspace(int(startyear),int(endyear),int(endyear)-int(startyear)+1)])):
        filt_TCyear = filted_TCnames[inddd]
        want_varnames = ast.literal_eval(wantvarnames)
        df_storms = {}
        for stormname in filt_TCyear:
            temp = pd.concat([SHIPSdict[inddd][stormname][i] for i in range(len(SHIPSdict[inddd][stormname]))], axis=1, join='inner')
            tempv = temp[targetname][lagnum:].reset_index(drop=True)
            tempd = temp[want_varnames][:-lagnum].reset_index(drop=True)
            df_storms[stormname] = pd.concat([tempv,tempd], axis=1, join='inner')
        store_dfstorms[year]=df_storms
    return store_dfstorms

def add_derive_df(startyear=None,endyear=None,SHIPSdict=None,addfilepath=None,addvarname=None,filted_TCnames=None,lagnum=None):
    with open(addfilepath, 'rb') as f:
        ships_df = pickle.load(f)   
    store_dfstorms = {}
    for inddd,year in tqdm(enumerate([int(obj) for obj in np.linspace(int(startyear),int(endyear),int(endyear)-int(startyear)+1)])):
        filt_TCyear = filted_TCnames[inddd]
        df_storms = {}
        for stormname in filt_TCyear:
            temp = ships_df[year][stormname]
            tempd = temp[addvarname][:-lagnum].reset_index(drop=True)
            df_storms[stormname] = pd.concat([SHIPSdict[year][stormname],tempd], axis=1, join='inner')
        store_dfstorms[year]=df_storms
    return store_dfstorms




