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

################################################################################################################################################################
# ERA5 routine
################################################################################################################################################################
def read_processed_vars_era5(loc=None,year=None,stormname=None,era5_dropvar=None):
    """
    era5_dropvar: Variables dropped due to inconsistency with SHIPS
    """
    foldernames = ['obsw_dwmax','tigramite_6hr']
    store = []
    for foldername in foldernames:
        tmp = pd.read_csv(glob.glob(loc+str(foldername)+'/'+\
                                 str(year)+'/'+str(year)+'*'+str(stormname)+'.csv')[0],delimiter=r",").fillna(0)

        tmp.rename({"Unnamed: 0":"a"}, axis="columns", inplace=True)
        tmp=tmp.drop('a', axis=1)
        #tmp=tmp.drop('index', axis=1)
        if "Unnamed: 0.1" in tmp.keys():
            tmp.rename({"Unnamed: 0.1":"b"}, axis="columns", inplace=True)
            tmp=tmp.drop('b', axis=1)
        if "index" in tmp.keys():
            tmp=tmp.drop('index', axis=1)
        if foldername=='obsw_dwmax':
            tmp = tmp.iloc[:,:]
            tmp = tmp[['delv24']]

        if foldername=='tigramite_6hr':
            tmp = tmp.iloc[:,:]
            #here according to CIRA suggestion we only keep the vertical levels present in GFS and also remove the single level variables
            tmp = tmp.drop(['pmin','wind10', 'delv','div_50','div_600','div_800','div_925', 'eqt600', 'eqt800', 'eqt925', '2mdewtmp','2mtmp',\
                            'conv_ppt','tot_cld_ice','tot_cldwtr','tot_cld_rain','vi_div_cld_froz_wtr','vi_div_cld_liq_wtr',\
                            'vi_div_gpot_flux','vi_div_ke_flux','vi_div_mass_flux','vi_div_moisture_flux','vi_div_olr_flux',\
                            'vi_div_tot_enrgy_flux','vi_ke','vi_pe_inte','vi_pe_ie_latentenrgy','vi_temp','vi_olr','vi_tot_enrgy',\
                            'vi_moisture_div','cape','inst_10m_wnd_gst','inst_moisture_flux','inst_ssh_flux','surfmean_swr_flux',\
                            'surfmean_lhf','surfmean_lwr_flux','surfmean_shf','dwnwrdmean_swr_flux','topmean_lwr_flux','topmean_swr_flux',\
                            'vimean_moisture_div','surf_lhf','surf_shf','tot_suprcool_liqwtr','tot_wtr_vpr','conv_rrate','ls_rrate','mn_conv_prate',\
                            'mn_ls_prate','mn_tot_prate', 'vort_50','vort_70','vort_600','vort_800','vort_900','vort_925','vort_950','vort_975','pvor_50',\
                            'pvor_70','pvor_600','pvor_925','pvor_975','rhum_50','rhum_70','rhum_600','rhum_800','rhum_900','rhum_925','rhum_950','rhum_975',\
                            'gpot_50','gpot_70','gpot_600','gpot_900','gpot_925','gpot_950','gpot_975','temp_50','temp_70','temp_600','temp_800','temp_900',\
                            'temp_925','temp_950','temp_975','vvel_50','vvel_70','vvel_600','vvel_925','vvel_975','outdiv_50','outdiv_600','outdiv_800','outdiv_925',\
                            'outeqt600','outeqt800','outeqt925','out2mdewtmp','out2mtmp','outconv_ppt','outtot_cld_ice','outtot_cldwtr','outtot_cld_rain',\
                            'outvi_div_cld_froz_wtr','outvi_div_cld_liq_wtr','outvi_div_gpot_flux','outvi_div_ke_flux','outvi_div_mass_flux','outvi_div_moisture_flux',\
                            'outvi_div_olr_flux','outvi_div_tot_enrgy_flux','outvi_ke','outvi_pe_inte','outvi_pe_ie_latentenrgy','outvi_temp','outvi_olr','outvi_tot_enrgy',\
                            'outvi_moisture_div','outcape','outinst_10m_wnd_gst','outinst_moisture_flux','outinst_ssh_flux','outsurfmean_swr_flux','outsurfmean_lhf',\
                            'outsurfmean_lwr_flux','outsurfmean_shf','outdwnwrdmean_swr_flux','outtopmean_lwr_flux','outtopmean_swr_flux','outvimean_moisture_div',\
                            'outsurf_lhf','outsurf_shf','outtot_suprcool_liqwtr','outtot_wtr_vpr','outconv_rrate','outls_rrate','outmn_conv_prate','outmn_ls_prate',\
                            'outmn_tot_prate','outvort_50','outvort_70','outvort_600','outvort_800','outvort_900','outvort_925','outvort_950','outvort_975','outpvor_50',\
                            'outpvor_70','outpvor_600','outpvor_925','outpvor_975','outrhum_50','outrhum_70','outrhum_600','outrhum_800','outrhum_900','outrhum_925',\
                            'outrhum_950','outrhum_975','outgpot_50','outgpot_70','outgpot_600','outgpot_800','outgpot_900','outgpot_925','outgpot_950','outgpot_975',\
                            'outtemp_50','outtemp_70','outtemp_200','outtemp_250','outtemp_600','outtemp_800','outtemp_900','outtemp_925','outtemp_950','outtemp_975',\
                            'outvvel_50','outvvel_70','outvvel_600','outvvel_925','outvvel_975','shear_925_200','shear_925_250',\
                            'shear_925_200.1','shear_925_250.1',], axis=1)
        store.append(tmp)
    return store

