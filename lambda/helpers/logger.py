import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a handler and set the formatter
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def set_log_level(level: str) -> None:
    """Set the logging level based on input.

    Args:
        level (str): The desired logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    """

    # Normalize the input level to uppercase
    level = level.upper()

    # Validate the input level and set the logger's level accordingly
    if level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:

        # Set the logger's level
        logger.setLevel(level)

        # Log the change
        logger.info(f"Log level set to {level}.")

    else:

        # Log an error if the level is invalid
        logger.error("Invalid log level provided. Keeping current level.")
