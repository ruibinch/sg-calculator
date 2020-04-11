import logging
import logging.config
import os
import yaml

def setup():
    """Sets up the logging module with the config specified in `config/logger.yaml`."""

    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'dev', 'logger.yml'), 'r') as f:
            logger_config = yaml.safe_load(f.read())
            logging.config.dictConfig(logger_config)
            print('Configuring logger via logger.yml file')
    except FileNotFoundError:
        print('Configuring logger via basicConfig')
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
