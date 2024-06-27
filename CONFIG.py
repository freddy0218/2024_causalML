import configparser

def create_config():
    config = configparser.ConfigParser()

    # Add sections and value pairs
    config['Dataset'] = {'TCfilt': 
                         [(2010,'MATTHEW'),(2010,'NICOLE'),(2012,'KIRK'),(2013,'ERIN'),(2021,'ODETTE')]
                        }
    config['paths'] = {'tracks_path': '/work/FAC/FGSE/IDYST/tbeucler/default/saranya/causal/besttracks/na/',
                       '
    
    # Write the config to a file
    with open('config.ini','w') as configfile:
        config.write(configfile)

if __name__=="__main__":
    create_config()
        
        
    