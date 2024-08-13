import yaml


def load_config(file_path):
    """
    Load the YAML configuration file.

    Args:
        file_path (str): Path to the YAML config file.

    Returns:
        dict: Loaded configuration.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def save_config(config, file_path):
    """
    Save the configuration to a YAML file.

    Args:
        config (dict): Configuration to save.
        file_path (str): Path to save the YAML config file.
    """
    with open(file_path, "w") as file:
        yaml.dump(config, file)
