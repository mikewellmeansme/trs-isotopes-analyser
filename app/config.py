import yaml


def load_config(path):
    
    config = {}

    try:
        with open(path, 'r') as yml_file:
            data = yaml.load(yml_file, yaml.Loader)
            if data:
                config.update(data)
    except FileNotFoundError as e:
        raise Exception(f'{path} file not found!')
    
    return config
