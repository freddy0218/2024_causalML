import configparser

def read_config():
    config = configparser.ConfigParser()
    
    # Read config file
    config.read('config.ini')
    
    # Access values
    filt_TCs = config.get('Dataset', 'TCfilt')
    
    # Return dictionary
    config_values = {
        'TCfilt': filt_TCs,
    }
    return config_values
    