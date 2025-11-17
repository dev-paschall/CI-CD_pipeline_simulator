import time
import uvicorn

from simulator.logging_config import get_logger
from simulator.watcher import start_watcher
from simulator.dashboard import app

logger = get_logger(__name__)

# Project path to be watched.
PATH_TO_WATCH = "sample_project"

def main():
    logger.info("--- CI/CD Simulator Starting Up ---")
    
    # Starts the file watcher
    observer = start_watcher(PATH_TO_WATCH)

    # starts the fastapi server
    logger.info("Starting FastAPI dashboard at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.01", port=8000)

if __name__ == "__main__":
    main()