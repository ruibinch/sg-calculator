import logging
import logging.config
import yaml

try:
    with open('config/logger.yaml', 'r') as f:
        logger_config = yaml.safe_load(f.read())
        logging.config.dictConfig(logger_config)
    print('Configuring logger via YAML file')
except FileNotFoundError:
    print('Configuring logger via basicConfig')
    logging.basicConfig(
        level=logging.DEBUG,
        filename='tmp/output.log',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )