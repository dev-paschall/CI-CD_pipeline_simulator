import logging
import yaml
import time
import subprocess
import os 

logger = logging.getLogger(__name__)
from .docker_utils import build_image as docker_build, push_image as docker_push

# Store build status.
build_status = {}

def parse_config(repo_path):
    """ Loads the config file from the project ."""
    config_path = os.path.join(repo_path, ".cicd.yml")
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            logger.info("Loaded config from %s", config_path)
            return config
    except FileNotFoundError:
        logger.error("Config file not found at %s", config_path)
        return None
    except Exception as e:
        logger.error("Error parsing config %s", e)
        return None
    
def run_test(config):
    """ Runs the test command specified in the config file. """
    test_command  = config.get("test", {}).get("command", {})
    if not test_command:
        logger.warning("No test command found in config file. Skipping test")
        return True
    logger.info("Running tests: %s", test_command)
    try:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            check=True,
            text=True)
        logger.info("Test output: \n%s", result.stdout)
        logger.info("Tests passed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Test failed!.")
        logger.error("Test STDOUT: \n%s", result.stdout)
        logger.error("Test STDERR: \n%s", result.stderr)
        return False
    except Exception as e:
        logger.error("An unknown error occured while running the test: %s", e)
        return False
    
def build_image(config, repo_path, image_name_with_tag):
    ''' Builds the Docker image. '''
    build_config = config.get("build", {})
    dockerfile_name = build_config.get("dockerfile", "Dockerfile")
    
    logger.info("Building Docker image: %s...", image_name_with_tag)

    build_success = docker_build(repo_path=repo_path,
                                 docker_path=dockerfile_name,
                                 image_name=image_name_with_tag)
    
    if build_success:
        logger.info("Docker build complete: %s", image_name_with_tag)
    else:
        logger.error("Docker build failed for %s", image_name_with_tag)

    return build_success

def deploy_image(config, image_name_with_tag):
    '''Deploy(push) the Docker image.'''
    registry = config.get("deploy", {}).get("registry")

    if not image_name_with_tag or not registry:
        logger.info("Missing 'image_name' or 'registry' in config file. Cannot deploy.")
        return False
    
    logger.info("Starting docker push for %s to %s...", image_name_with_tag, registry)

    push_success = docker_push(image_name=image_name_with_tag)

    if push_success:
        logger.info("Docker push complete: %s", image_name_with_tag)
    else:
        logger.error("Docker push failed for %s", image_name_with_tag)

    return push_success

def trigger_pipeline(repo_path):
    '''Main pipeline function'''
    build_id = f"build-{int(time.time())}"
    logger.info("---pipeline triggered for build ID: %s---", build_id)

    # store initial build status
    build_status[build_id] = {"id": build_id, "status": "pending"}

    try:
        # Parse config file.
        build_status[build_id]["status"] = "parsing"
        config_info = parse_config(repo_path)
        if not config_info:
            raise Exception("failed to open or parse .cicd.yml.")

        # Getting image base_name and version
        build_config = config_info.get("build", {})
        base_name = build_config.get("base_name")
        image_tag = build_config.get("version", "latest")

        if not base_name:
            logger.error("No 'base_name' found in .cicd.yml build config.")
        
        image_name_with_tag= f"{base_name}:{image_tag}"
        logger.info(f"Using full image name: {image_name_with_tag}")
        
        # Run tests.
        build_status[build_id]["status"] = "testing"
        if not run_test(config_info):
            raise Exception("Tests failed.")
        
        # Build Docker image.
        build_status[build_id]["status"] = "building"
        if not build_image(config_info, repo_path, image_name_with_tag):
            raise Exception("Docker image build failed.")
        
        # Deploy Docker image.
        build_status[build_id]["status"] = "deploying"
        if not deploy_image(config_info, image_name_with_tag):
            raise Exception("Docker image deploy failed.")
        
        # If all the steps are successful
        build_status[build_id]['status'] = 'success'
        logger.info("--- Build ID %s: Pipeline Succeeded ---", build_id)

    except Exception as e:
        # If any step fails:
        logger.error("Pipeline failed: %s", e)
        build_status[build_id]['status'] = 'failed'
        logger.info("--- Build ID %s: Pipeline Failed ---", build_id)
