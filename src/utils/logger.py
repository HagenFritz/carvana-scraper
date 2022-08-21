import logging
import pathlib

def setup(log_file_name, level=logging.INFO):
    """
    Creates a logging object
    Parameters
    ----------
    log_file_name : str
        how to name the log file
    Returns
    -------
    logger : logging object
        a logger to debug
    """
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Clearing log instances
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handler
    dir_path = pathlib.Path(__file__).resolve().parent
    f_handler = logging.FileHandler(f'{dir_path}/{log_file_name}.log',mode='w')
    logging.getLogger().setLevel(level)

    # Create formatter and add it to handler
    f_format = logging.Formatter('%(asctime)s: %(name)s (%(lineno)d) - %(levelname)s - %(message)s',datefmt='%m/%d/%y %H:%M:%S')
    f_handler.setFormatter(f_format)

    # Add handler to the logger
    logger.addHandler(f_handler)

    # repeat the above steps but for a StreamHandler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level)
    c_format = logging.Formatter('%(asctime)s: %(name)s (%(lineno)d) - %(levelname)s - %(message)s',datefmt='%m/%d/%y %H:%M:%S')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    return logger