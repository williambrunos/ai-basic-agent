import yaml


def load_agent_config(yaml_path: str):
    """Load agent configuration from a YAML file."""
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    return config