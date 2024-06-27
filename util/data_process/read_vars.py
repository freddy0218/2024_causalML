import pandas as pd

def remove_storms(trackpath=None,basinID='NA',yearmin=None,yearmax=None,remove_set=None):
    """
    Hard-code storm removal.
    """
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
    return stormnames

        
def read_processed_vars_ships(loc=None,foldername=['newships_dev_POT'],year=None,stormname=None):
    store = []
    for foldername in foldernames:
        tmp = pd.read_csv(glob.glob(loc+str(foldername)+'/'+\
                                 str(year)+'/'+str(year)+'*shipsdev*'+str(stormname)+'.csv')[0],delimiter=r",").fillna(0)
        store.append(tmp.iloc[:,:])
    return store