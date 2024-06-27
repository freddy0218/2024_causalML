import pandas as pd
from tqdm.auto import tqdm
import numpy as np
import glob

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




