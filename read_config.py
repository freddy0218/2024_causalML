import configparser

def read_config():
    config = configparser.ConfigParser()
    
    # Read config file
    config.read('config.ini')
    
    # Access values
    start_year = config.get('General','start_year')
    end_year = config.get('General','end_year')
    target_lag = config.get('General','target_lag')
    splitratio = config.get('General','splitratio')
    filt_TCs = config.get('Dataset', 'TCfilt')
    SHIPSops_varname = config.get('Dataset','SHIPSop_varname')
    track_path = config.get('paths','tracks_path')
    vars_path = config.get('paths','vars_path')
    
    
    # Return dictionary
    config_values = {
        'TCfilt': filt_TCs,
        'track_path':track_path,
        'vars_path':vars_path,
        'start_year':start_year,
        'end_year':end_year,
        'target_lag':target_lag,
        'splitratio':splitratio,
        'SHIPSops_varname':SHIPSops_varname,
    }
    return config_values
    