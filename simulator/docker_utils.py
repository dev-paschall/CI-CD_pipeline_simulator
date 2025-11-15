import logging
import docker
from docker.errors import BuildError, ImageNotFound, APIError

logger = logging.getLogger(__name__)

try:
    docker_client = docker.from_env()
    docker_client.ping()
    logger.info("Docker client initialized successfully.")
except Exception as e:
    logger.error("Docker client initialization failed. Is docker running?: %s", e)
    docker_client = None

def build_image(repo_path, docker_path, image_name):
    if not docker_client:
        logger.error("Docker not running. Cannot build.")
        return False
    
    logger.info("building image: %s from path: %s", image_name, repo_path)

    try:
        image , image_build_logs = docker_client.images.build(
            path=repo_path,
            dockerfile=docker_path,
            tag=image_name,
            rm=True)
        
        logger.info("Successfully built image: %s", image.tags)
        for log_line in image_build_logs:
            if isinstance(log_line, dict) and "stream" in log_line: 
                logger.debug(str(log_line["stream"]).strip())
        return True
    
    except BuildError as e:
        logger.error("Docker build failed: %s", e)
        for log_line in e.build_log:
            if isinstance(log_line, dict) and "stream" in log_line:
                logger.debug(str(log_line["stream"]).strip())
        return False
    except APIError as e:
        logger.error("Docker API error: %s", e)
        return False
    except Exception as e:
        logger.error("An unknown error occurred during build: %s", e)
        return False
    
def push_image(image_name):
    if not docker_client:
        logger.error("Docker not running. Cannot push image.")
        return False
    
    logger.info("Pushing image: %s", image_name)

    try:
        push_logs = docker_client.images.push(image_name, stream=True, decode=True)

        for line in push_logs:
            if "status" in line:
                logger.debug(line["status"])
            if "error" in line:
                logger.error(line["error"])
                return False
        logger.info("Successfully pushed image: %s", image_name)
        return True
    except APIError as e:
        logger.error("Docker API error: %s", e)
        return False
    except Exception as e:
        logger.error("An unknown error occurred while pushing image: %s", e)
        return False
