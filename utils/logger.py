import logging
import os

def setup():
    """Sets up the logging module.
    
    In development, logs will be written to files in /logs based on the config specified in `logger.yml`.
    In production, logs will be printed to the console which will be stored in CloudWatch.
    """

    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'dev', 'logger.yml'), 'r') as f:
            import yaml
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
