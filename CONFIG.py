import configparser
#---------------------------------------------------------------------------------------------------------
# Notes:
# (1) Remove "VMAX" from "SHIPSop_varname" if you would like to set "VMAX" as a target
#---------------------------------------------------------------------------------------------------------
def create_config():
    config = configparser.ConfigParser()

    # Add sections and value pairs
    config['General'] = {'start_year': 2000,
                         'end_year': 2021,
                         'target_lag':8,
                         'splitratio':0.2,
                         'PRIMED_levels':[100, 150, 200, 250, 300, 400,  500, 700, 850, 1000],
                         'basin':'NA',
                        }
    config['Dataset'] = {'TCfilt': 
                         [(2010,'MATTHEW'),(2010,'NICOLE'),(2012,'KIRK'),(2013,'ERIN'),(2021,'ODETTE')],
                         'SHIPSop_varname':['MSLP','T200','T250','LAT','CSST','PSLV','Z850','D200','EPOS','SHDC',\
                                            'RHMD','TWAC','G200','TADV','SHGC','POT','POT2','LHRD','VSHR','PER','VPER'],
                         'ERA5SPS_varname':['wind10','pmin','out_t250','out_t200','spdx','out_mean_midrhum',\
                                            'POT','POT2','PER','VPER','pc20','VSHR','LHRD','EPOS','clat','tadv','shearmag',\
                                            'out_shearmag','sdir','d200','z850','twnd850'],
                         'ERA5_dropvarname':['pmin','wind10', 'delv','div_50','div_600','div_800','div_925', 'eqt600', 'eqt800', 'eqt925', '2mdewtmp','2mtmp',\
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
                                             'shear_925_200.1','shear_925_250.1',],
                         
                        }
    config['paths'] = {'tracks_path': '/work/FAC/FGSE/IDYST/tbeucler/default/saranya/causal/besttracks/na/',
                       'vars_path': '/work/FAC/FGSE/IDYST/tbeucler/default/saranya/causal/ts_notebooks/ships/timeseries/',
                       'PRIMED_path':'/work/FAC/FGSE/IDYST/tbeucler/default/saranya/causal/ts_notebooks/ships/tc_primed_names/',
                       'ERA5_SHIPSemul_path':'/work/FAC/FGSE/IDYST/tbeucler/default/saranya/causal/SHIPS/ships_pkl/',
                      }
    config['causal'] = {'tau_min': 8,
                        'tau_max': 8,
                        'alpha_totest':[0.0001, 0.00015 ,0.001,0.0015,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,
                          0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.86,0.88,0.9]
                       }
    
    # Write the config to a file
    with open('config.ini','w') as configfile:
        config.write(configfile)

if __name__=="__main__":
    create_config()
        
        
    
