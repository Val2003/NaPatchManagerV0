from loguru import logger
import sys


def get_logger(log_level):
    logger.remove()

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level:<8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=log_level
    )
    logger.add(
        "..logs/patch_builder.log",
        rotation="10.MB",
        compression="zip",
        level="DEBUG",
        backtrace=True,
        diagnose=True,
    )
    return logger
