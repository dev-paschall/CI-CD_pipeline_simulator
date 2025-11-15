import time

from simulator.logging_config import get_logger
from simulator.watcher import start_watcher

logger = get_logger(__name__)

# Project path to be watched.
PATH_TO_WATCH = "sample_project"

def main():
    logger.info("--- CI/CD Simulator Starting Up ---")
    
    # Start the file watcher
    observer = start_watcher(PATH_TO_WATCH)

    # Keep the main application alive
    logger.info("Application running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        observer.stop()
        observer.join()
        logger.info("Watcher stopped. Goodbye.")

if __name__ == "__main__":
    main()