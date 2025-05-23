import os
import configparser

def add_onion_to_config(onion, config_file_path, section="Tor", key="Onion"):
    """
    Adds or updates a URL in an INI configuration file.
    
    Args:
        onion (str): The URL to add or update
        config_file_path (str): Path to the INI file
        section (str, optional): Section name. Defaults to "urls".
        key (str, optional): Key name. Defaults to "default_url".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create config parser
        config = configparser.ConfigParser()


        # Read existing config if file exists
        if os.path.exists(config_file_path):
            config.read(config_file_path)
        
        # Create section if it doesn't exist
        if section not in config:
            config[section] = {}
        
        # Add or update the URL
        config[section][key] = onion
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(config_file_path)), exist_ok=True)
        
        # Write to file
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
            
        return True
        
    except Exception as e:
        print(f"Error adding URL to config: {str(e)}")
        return False
