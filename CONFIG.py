import configparser

def create_config():
    config = configparser.ConfigParser()

    # Add sections and value pairs
    config['General'] = {'start_year': 2000,
                         'end_year': 2021,
                         'target_lag':4,
                         'splitratio':0.15,
                        }
    config['Dataset'] = {'TCfilt': 
                         [(2010,'MATTHEW'),(2010,'NICOLE'),(2012,'KIRK'),(2013,'ERIN'),(2021,'ODETTE')],
                         'SHIPSop_varname':['VMAX','MSLP','T200','T250','LAT','CSST','PSLV','Z850','D200','EPOS','SHDC',\
                                            'RHMD','TWAC','G200','TADV','SHGC','POT','POT2','LHRD','VSHR','PER','VPER'],\
                         
                        }
    config['paths'] = {'tracks_path': '/work/FAC/FGSE/IDYST/tbeucler/default/saranya/causal/besttracks/na/',
                       'vars_path': '/work/FAC/FGSE/IDYST/tbeucler/default/saranya/causal/ts_notebooks/ships/timeseries/',
                      }
    
    # Write the config to a file
    with open('config.ini','w') as configfile:
        config.write(configfile)

if __name__=="__main__":
    create_config()
        
        
    