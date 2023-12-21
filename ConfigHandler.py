import configparser

def read_config(config_file_path='config.ini'):
    config = configparser.ConfigParser()

    try:
        config.read('config.ini')

    except FileNotFoundError:
        print("Error: The configuration file 'config.ini' was not found.")
    except configparser.Error as e:
        print(f"Error reading the configuration file: {e}")

        return config

# Example Usage:
# config = read_config()
# database_config = config['Database']
# host = database_config['host']
# user = database_config['user']
# password = database_config['password']
# database_name = database_config['database']