import logging

def config_log(level):
    FORMAT = "%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(message)s"
    logging.basicConfig(format=FORMAT, level=level)
