from event_finder.application import Application
from event_finder.config.loader import get_config
from event_finder.logging.loader import get_logger


def main():
    logger = get_logger()
    logger.info("Applications: Starting")
    
    config = get_config()

    app = Application(config)
    app.run()
    
    logger.info("Application: Done")


if __name__ == "__main__":
    main()

