import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .pipeline import trigger_pipeline

logger = logging.getLogger(__name__)
DEBOUNCE_SECONDS = 60.0 # Time before pipeline is triggered after changes is discoverd.

class cicd_pipeline_simulator_event_handler(FileSystemEventHandler):
    
    # We pass the repo_path in when we create the handler
    def __init__(self, repo_path):
        super().__init__()
        self.repo_path = repo_path
        self.timer = None

        logger.info(f"Handler initialized to watch: {self.repo_path}")

    def _trigger_pipeline(self):
        """Internal method that calls the pipeline."""
        logger.info(f"Quiet period over. Triggering pipeline for {self.repo_path}...")
        trigger_pipeline(repo_path=self.repo_path)
        self.timer = None # Clear the timer

    def on_any_event(self, event):
        if event.is_directory:
            return
        
        if event.event_type == 'modified':
            logger.debug(f"Change detected: {event.src_path}. Resetting timer...")

            # If a timer is already running, cancel it.
            if self.timer:
                self.timer.cancel()
            
            # Start a new timer that will call our pipeline function after DEBOUNCE_SECONDS.
            self.timer = threading.Timer(DEBOUNCE_SECONDS, self._trigger_pipeline)
            self.timer.start()

def start_watcher(path_to_watch):
    logger.info(f"Starting watcher on directory: {path_to_watch}")

    event_handler = cicd_pipeline_simulator_event_handler(repo_path=path_to_watch)

    observer = Observer()

    # This is better for watching a whole project
    observer.schedule(event_handler, path_to_watch, recursive=True)

    # This stops the watcher from blocking the FastAPI server
    observer_thread = threading.Thread(target=observer.start)
    observer_thread.daemon = True  # So it exits when the main app exits
    observer_thread.start()
    
    logger.info("Watcher started in background thread.")
    
    return observer
