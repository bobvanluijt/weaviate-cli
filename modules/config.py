import yaml
from modules.Messages import Messages
from modules.Helpers import Helpers
from os.path import expanduser
import validators
import weaviate
import weaviate.connect

CONFIG_KEY_URL = "url"
CONFIG_KEY_EMAIL = "email"
CONFIG_KEY_AUTH_CLIENTSECRET = "auth_clientsecret"

def load_config():
    """ Read the config from the users home folder
    If the config does not exist the user is asked to create it

    :return: dict containing the config
    """
    config_file = expanduser("~") + "/.weaviate.conf"

    try:
        config = yaml.load(open(config_file), Loader=yaml.FullLoader)
        Helpers(config).Info(Messages().Get(120))
        return config
    except IOError:
        config = _create_config_dialog()
        _write_config_file(config_file, config)
        return config

def _write_config_file(config_file_path, config):
    """Write to a config YAML file"""
    try:
        with open(config_file_path, 'w') as config_file_path:
            yaml.dump(config, config_file_path, default_flow_style=False)
        Helpers(None).Info(Messages().Get(119))
    except IOError:
        Helpers(None).Error(Messages().Get(205) + config_file_path)

def _create_config_dialog():
    """ Asks the user to set the config if he has none specified

    :return: a dict containing the config
    """
    config = {}

    config[CONFIG_KEY_URL] = input(Messages().Get(130) + ": ")
    if not validators.url(config[CONFIG_KEY_URL]):
        Helpers(None).Error(Messages().Get(211))

    # Check if the Weaviate can be detected
    client = weaviate.Client(config[CONFIG_KEY_URL])
    if not client.is_reachable():
        Helpers(None).Error(Messages().Get(210))

    config[CONFIG_KEY_EMAIL] = input(Messages().Get(131) + ": ")
    if not validators.email(config[CONFIG_KEY_EMAIL]):
        Helpers(None).Error(Messages().Get(212))

    # Detect openID
    conn = weaviate.connect.Connection(config[CONFIG_KEY_URL])
    try:
        response = conn.run_rest(".well-known/openid-configuration", weaviate.connect.REST_METHOD_GET)

    except ConnectionError:
        Helpers(None).Error(Messages().Get(210))

    # OpenID is set, continue the config
    if response.status_code == 200:
        # Fixed OAuth variables
        config["auth_bearer"] = None # TODO test if really still necessary
        config["auth_expires"] = 0 # TODO test if really still necessary
        # Variable OpenID info
        config[CONFIG_KEY_AUTH_CLIENTSECRET] = input(Messages().Get(137) + ": ")

    return config