import logging
import logging.config
import yaml

def setup():
    """
        Sets up the logging module with the config specified in `config/logger.yaml`.
    """

    try:
        with open('config/logger.yaml', 'r') as f:
            logger_config = yaml.safe_load(f.read())
            logging.config.dictConfig(logger_config)
    except FileNotFoundError:
        print('Configuring logger via basicConfig')
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )