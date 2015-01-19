from logging import getLogger, Formatter


def create_logger(name, level, handler):
    logger = getLogger(name)
    logger.setLevel(level)
    formatter = Formatter(
        '[%(levelname)s] %(asctime)s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        )
    handler.setFormatter(formatter)
    handler.level = level
    logger.addHandler(handler)

    return logger
